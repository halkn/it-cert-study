#!/usr/bin/env python3
"""Validate a saved Domain evaluation and invalidate stale content hashes."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MINIMUM_THRESHOLDS = {
    "overall_score_percent": 80,
    "per_domain_score_percent": 70,
    "textbook_evidence_percent": 90,
    "maximum_ambiguous_questions": 0,
}
CONFIDENCE_VALUES = {"high", "medium", "low"}
EVIDENCE_VALUES = {"sufficient", "partial", "missing"}


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot read {path}: {exc}") from exc


def resolve_inside_repo(value: str, expected_file: str | None = None) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"Path must be inside the repository: {path}") from exc
    if expected_file and not (path / expected_file).is_file():
        raise SystemExit(f"Required file does not exist: {path / expected_file}")
    return path


def stable_hash(paths: list[Path], base: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.relative_to(base).as_posix()):
        relative = path.relative_to(base).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def stable_json_hash(value) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def percent(numerator: int, denominator: int) -> float:
    return round(100.0 * numerator / denominator, 1) if denominator else 0.0


def heading_exists(path: Path, heading: str) -> bool:
    text = path.read_text(encoding="utf-8")
    return bool(re.search(rf"^#+\s+{re.escape(heading)}\s*$", text, flags=re.MULTILINE))


def compute_hashes(exam: Path, report: dict, questions_by_id: dict[str, dict]) -> dict[str, str | None]:
    domains = {int(item) for item in report.get("domains", [])}
    textbook_paths = []
    for domain in domains:
        textbook_paths.extend((exam / "textbook" / f"domain-{domain}").glob("*.md"))
    question_paths = [exam / questions_by_id[item["id"]]["file"] for item in report.get("questions", []) if item.get("id") in questions_by_id]
    matrix = load_json(exam / "docs" / "coverage-matrix.json")
    exam_metadata = matrix.get("exam", {})
    coverage_slice = {
        "exam": {
            key: exam_metadata.get(key)
            for key in ("code", "study_guide_source_id", "study_guide_language", "study_guide_updated_on")
        },
        "domains": [item for item in matrix.get("domains", []) if item.get("id") in domains],
        "objectives": [item for item in matrix.get("objectives", []) if item.get("domain") in domains],
    }
    return {
        "textbook_sha256": stable_hash(textbook_paths, exam) if report.get("evaluation_type") == "textbook-only" else None,
        "questions_sha256": stable_hash(question_paths, exam),
        "coverage_matrix_sha256": stable_json_hash(coverage_slice),
    }


def validate(exam: Path, report_path: Path, show_hashes: bool) -> list[str]:
    report = load_json(report_path)
    config = load_json(exam / "exam-config.json")
    question_registry = load_json(exam / config["registries"]["questions"])
    questions_by_id = {item["id"]: item for item in question_registry.get("questions", [])}
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    check(report.get("schema_version") == 1, "unsupported schema_version")
    evaluation_type = report.get("evaluation_type")
    check(evaluation_type in {"question-quality", "textbook-only"}, "invalid evaluation_type")
    check(report.get("exam_id") == config.get("id"), "exam_id does not match exam-config.json")
    check(bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", report.get("evaluated_on", ""))), "evaluated_on must be YYYY-MM-DD")

    domains = {int(item) for item in report.get("domains", []) if isinstance(item, int)}
    check(bool(domains), "domains must contain at least one integer")
    model = report.get("model", {})
    check(bool(model.get("id")), "model.id is required")
    check(bool(model.get("reasoning_effort")), "model.reasoning_effort is required")
    revision = report.get("source_revision", {})
    check(bool(re.fullmatch(r"[0-9a-f]{40}", revision.get("git_commit", ""))), "source_revision.git_commit must be a full SHA")
    check(isinstance(revision.get("working_tree_dirty"), bool), "source_revision.working_tree_dirty must be boolean")
    controls = report.get("test_controls", {})
    check(controls.get("answers_hidden_until_locked") is True, "answers must remain hidden until responses are locked")
    check(controls.get("registry_hidden_until_locked") is True, "question registry must remain hidden until responses are locked")
    if evaluation_type == "textbook-only":
        check(controls.get("external_sources_allowed") is False, "textbook-only evaluation cannot allow external sources")
        allowed_paths = set(controls.get("allowed_paths", []))
        expected_paths = {f"textbook/domain-{domain}/*.md" for domain in domains}
        check(allowed_paths == expected_paths, "textbook-only allowed_paths must exactly match evaluated Domains")

    thresholds = report.get("thresholds", {})
    required_thresholds = {"overall_score_percent", "per_domain_score_percent", "maximum_ambiguous_questions"}
    if evaluation_type == "textbook-only":
        required_thresholds.add("textbook_evidence_percent")
    for key in required_thresholds:
        minimum = MINIMUM_THRESHOLDS[key]
        value = thresholds.get(key)
        if key == "maximum_ambiguous_questions":
            check(value == minimum, f"{key} must be {minimum}")
        else:
            check(isinstance(value, (int, float)) and value >= minimum, f"{key} must be at least {minimum}")

    entries = report.get("questions", [])
    check(bool(entries), "questions must not be empty")
    entry_ids = [item.get("id") for item in entries]
    check(len(entry_ids) == len(set(entry_ids)), "questions contain duplicate ids")
    expected_ids = {
        question_id
        for question_id, question in questions_by_id.items()
        if question.get("layer") == "mock"
        and {int(item.split(".", 1)[0]) for item in question.get("objective_ids", [])}
        and {int(item.split(".", 1)[0]) for item in question.get("objective_ids", [])} <= domains
    }
    check(set(entry_ids) == expected_ids, "report questions must exactly match all mock questions in the evaluated Domains")

    correct_count = 0
    sufficient_count = 0
    ambiguous_count = 0
    domain_totals: dict[int, int] = defaultdict(int)
    domain_correct: dict[int, int] = defaultdict(int)
    for entry in entries:
        question_id = entry.get("id", "<missing>")
        question = questions_by_id.get(question_id)
        check(question is not None, f"unknown question id: {question_id}")
        if question is None:
            continue
        check(question.get("layer") == "mock", f"evaluation question must use mock layer: {question_id}")
        question_domains = {int(item.split(".", 1)[0]) for item in question.get("objective_ids", [])}
        check(question_domains <= domains, f"question {question_id} references a Domain outside the report")
        selected = entry.get("selected_option_ids", [])
        check(isinstance(selected, list) and all(re.fullmatch(r"[A-Z]", str(item)) for item in selected), f"invalid answer for {question_id}")
        check(len(selected) == len(set(selected)), f"duplicate selected options for {question_id}")
        check(len(selected) == question.get("required_selections"), f"selected option count does not match required selections for {question_id}")
        selected = sorted(set(selected))
        correct = selected == sorted(question.get("correct_option_ids", []))
        correct_count += int(correct)
        for domain in question_domains:
            domain_totals[domain] += 1
            domain_correct[domain] += int(correct)

        confidence = entry.get("confidence")
        check(confidence in CONFIDENCE_VALUES, f"invalid confidence for {question_id}")
        evidence_status = entry.get("evidence_status")
        if evaluation_type == "textbook-only":
            check(evidence_status in EVIDENCE_VALUES, f"invalid evidence_status for {question_id}")
            sufficient_count += int(evidence_status == "sufficient")
        ambiguous = entry.get("ambiguous")
        check(isinstance(ambiguous, bool), f"ambiguous must be boolean for {question_id}")
        ambiguous_count += int(ambiguous is True)

        if evaluation_type == "textbook-only" and evidence_status == "sufficient":
            check(entry.get("distractor_exclusion_supported") is True, f"sufficient evidence must support distractor exclusion for {question_id}")
            evidence = entry.get("evidence", [])
            check(bool(evidence), f"sufficient evidence requires citations for {question_id}")
            for citation in evidence:
                value = citation.get("file", "")
                path = exam / value
                check(not Path(value).is_absolute() and ".." not in Path(value).parts, f"unsafe evidence path for {question_id}")
                check(path.is_file(), f"evidence file does not exist for {question_id}: {value}")
                allowed = any(value.startswith(f"textbook/domain-{domain}/") for domain in domains)
                check(allowed, f"evidence is outside evaluated textbook Domains for {question_id}: {value}")
                heading = citation.get("heading", "")
                check(bool(heading) and path.is_file() and heading_exists(path, heading), f"evidence heading does not exist for {question_id}: {heading}")

        question_path = exam / question["file"]
        check(question_path.is_file(), f"question file does not exist: {question_id}")
        if question_path.is_file():
            question_text = question_path.read_text(encoding="utf-8")
            option_match = re.search(r"^## 選択肢\s*$\n+(.*?)(?=\n## 正解)", question_text, flags=re.MULTILINE | re.DOTALL)
            answer_match = re.search(r"^## 正解\s*$\n+(.*?)(?=\n## 正解理由)", question_text, flags=re.MULTILINE | re.DOTALL)
            explanation_match = re.search(r"^## 各誤答が誤りである理由\s*$\n+(.*?)(?=\n## 周辺知識)", question_text, flags=re.MULTILINE | re.DOTALL)
            check(bool(option_match and answer_match and explanation_match), f"question sections cannot be parsed: {question_id}")
            if option_match and answer_match and explanation_match:
                option_ids = set(re.findall(r"^- ([A-Z])\. ", option_match.group(1), flags=re.MULTILINE))
                explanation_ids = set(re.findall(r"^- ([A-Z]): ", explanation_match.group(1), flags=re.MULTILINE))
                markdown_answers = sorted(set(re.findall(r"\b[A-Z]\b", answer_match.group(1))))
                check(option_ids == explanation_ids, f"option and explanation ids differ: {question_id}")
                check(markdown_answers == sorted(question.get("correct_option_ids", [])), f"Markdown and registry answers differ: {question_id}")

    overall_score = percent(correct_count, len(entries))
    evidence_score = percent(sufficient_count, len(entries)) if evaluation_type == "textbook-only" else None
    per_domain = {str(domain): percent(domain_correct[domain], domain_totals[domain]) for domain in sorted(domains)}
    passed = (
        overall_score >= thresholds.get("overall_score_percent", 101)
        and all(score >= thresholds.get("per_domain_score_percent", 101) for score in per_domain.values())
        and (evaluation_type != "textbook-only" or evidence_score >= thresholds.get("textbook_evidence_percent", 101))
        and ambiguous_count <= thresholds.get("maximum_ambiguous_questions", -1)
        and not errors
    )

    result = report.get("result", {})
    check(result.get("overall_score_percent") == overall_score, "stored overall score does not match answers")
    check(result.get("per_domain_score_percent") == per_domain, "stored per-Domain scores do not match answers")
    check(result.get("textbook_evidence_percent") == evidence_score, "stored textbook evidence score does not match entries")
    check(result.get("ambiguous_question_count") == ambiguous_count, "stored ambiguous count does not match entries")

    expected_hashes = compute_hashes(exam, report, questions_by_id)
    if show_hashes:
        print(json.dumps(expected_hashes, ensure_ascii=False, indent=2))
    else:
        check(report.get("content_hashes") == expected_hashes, "content hashes are stale; rerun the evaluation")
    check(result.get("passed") is passed, "stored pass result does not match calculated result")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exam", required=True, help="Exam directory relative to the repository")
    parser.add_argument("--report", required=True, help="Evaluation report JSON")
    parser.add_argument("--show-expected-hashes", action="store_true", help="Print current hashes without comparing saved values")
    args = parser.parse_args()

    exam = resolve_inside_repo(args.exam, "exam-config.json")
    report_path = resolve_inside_repo(args.report)
    errors = validate(exam, report_path, args.show_expected_hashes)
    if errors:
        print(f"Evaluation validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1
    if not args.show_expected_hashes:
        print(f"Evaluation validation passed: {report_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
