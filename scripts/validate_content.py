#!/usr/bin/env python3
"""Validate one or more certification-exam content packages."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_STATUSES = {"planned", "draft", "review", "complete"}


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot read {path}: {exc}") from exc


def is_safe_repo_path(value: str) -> bool:
    if not isinstance(value, str):
        return False
    path = Path(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts


def markdown_section_has_content(text: str, heading: str) -> bool:
    pattern = rf"^## {re.escape(heading)}[^\n]*\n(?P<body>.*?)(?=^## |\Z)"
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    return bool(match and match.group("body").strip())


def find_exam_configs(selected_exam: str | None) -> list[Path]:
    if selected_exam:
        selected = Path(selected_exam)
        if not selected.is_absolute():
            selected = ROOT / selected
        config = selected if selected.name == "exam-config.json" else selected / "exam-config.json"
        if not config.is_file():
            raise SystemExit(f"Exam config does not exist: {config}")
        return [config]

    configs = sorted((ROOT / "exams").glob("*/*/exam-config.json"))
    if not configs:
        raise SystemExit("No exam packages found under exams/<vendor>/<exam>/")
    return configs


def validate_exam(config_path: Path) -> tuple[Validation, str]:
    validation = Validation()
    exam_root = config_path.parent
    config = load_json(config_path)
    registries = config.get("registries", {})
    expected = config.get("expected", {})
    expected_objectives = set(expected.get("objective_ids", []))
    expected_weights = {int(key): value for key, value in expected.get("domain_weights", {}).items()}
    official_hosts = set(config.get("official_hosts", []))

    validation.check(config.get("schema_version") == 1, "exam-config.json has unsupported schema_version")
    validation.check(bool(config.get("id")), "exam-config.json needs id")
    validation.check(bool(config.get("vendor")), "exam-config.json needs vendor")
    validation.check(bool(config.get("exam_code")), "exam-config.json needs exam_code")
    validation.check(bool(expected_objectives), "exam-config.json needs expected objective_ids")
    validation.check(bool(official_hosts), "exam-config.json needs official_hosts")

    def registry_path(key: str) -> Path:
        value = registries.get(key, "")
        validation.check(is_safe_repo_path(value), f"exam registry {key} has an unsafe path")
        return exam_root / value

    matrix = load_json(registry_path("coverage_matrix"))
    source_data = load_json(registry_path("sources"))
    diagram_data = load_json(registry_path("diagrams"))
    question_data = load_json(registry_path("questions"))

    sources = source_data.get("sources", [])
    source_ids = [item.get("id") for item in sources]
    validation.check(len(source_ids) == len(set(source_ids)), "sources.json has duplicate ids")
    for source in sources:
        source_id = source.get("id", "<missing>")
        parsed = urlparse(source.get("url", ""))
        validation.check(
            parsed.scheme == "https" and parsed.hostname in official_hosts,
            f"source {source_id} is not an allowed official HTTPS URL for {config.get('id')}",
        )
        validation.check(
            bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", source.get("checked_on", ""))),
            f"source {source_id} has no valid checked_on date",
        )
        validation.check(source.get("status") in {"active", "superseded", "unavailable"}, f"source {source_id} has invalid status")

    domains = matrix.get("domains", [])
    domain_ids = {item.get("id") for item in domains}
    weights = {item.get("id"): item.get("weight_percent") for item in domains}
    if expected_weights:
        validation.check(weights == expected_weights, f"domain weights differ from exam config: {weights}")
        validation.check(sum(weights.values()) == 100, "domain weights do not total 100")
    validation.check(matrix.get("exam", {}).get("study_guide_source_id") in source_ids, "exam study guide source is missing")
    exam_metadata = matrix.get("exam", {})
    if "japanese_guide_verification" in exam_metadata:
        validation.check(exam_metadata.get("japanese_guide_verification") in {"pending", "verified"}, "exam has invalid Japanese-guide verification state")
    validation.check(exam_metadata.get("release_status") in ALLOWED_STATUSES, "exam has invalid release status")

    diagrams = diagram_data.get("diagrams", [])
    diagram_ids = [item.get("id") for item in diagrams]
    validation.check(len(diagram_ids) == len(set(diagram_ids)), "diagrams.json has duplicate ids")
    for diagram in diagrams:
        diagram_id = diagram.get("id", "<missing>")
        validation.check(diagram.get("status") in ALLOWED_STATUSES, f"diagram {diagram_id} has invalid status")
        validation.check(set(diagram.get("objective_ids", [])) <= expected_objectives, f"diagram {diagram_id} references an unknown objective")
        validation.check(set(diagram.get("source_ids", [])) <= set(source_ids), f"diagram {diagram_id} references an unknown source")
        if diagram.get("status") != "planned":
            file_value = diagram.get("file")
            validation.check(isinstance(file_value, str) and is_safe_repo_path(file_value), f"diagram {diagram_id} needs a safe file path")
            if isinstance(file_value, str) and is_safe_repo_path(file_value):
                validation.check((exam_root / file_value).is_file(), f"diagram {diagram_id} file does not exist: {file_value}")
            validation.check(bool(diagram.get("source_ids")), f"diagram {diagram_id} needs official sources")

    questions = question_data.get("questions", [])
    question_ids = [item.get("id") for item in questions]
    questions_by_id = {item.get("id"): item for item in questions}
    validation.check(len(question_ids) == len(set(question_ids)), "questions.json has duplicate ids")
    for question in questions:
        question_id = question.get("id", "<missing>")
        question_status = question.get("status")
        objective_refs = question.get("objective_ids", [])
        validation.check(question.get("layer") in {"chapter", "domain", "mock"}, f"question {question_id} has invalid layer")
        validation.check(question_status in ALLOWED_STATUSES, f"question {question_id} has invalid status")
        validation.check(bool(objective_refs) and set(objective_refs) <= expected_objectives, f"question {question_id} needs one or more valid objectives")
        validation.check(question.get("question_type") in {"single-choice", "multiple-select"}, f"question {question_id} has invalid question_type")
        selections = question.get("required_selections")
        correct_options = question.get("correct_option_ids", [])
        validation.check(isinstance(selections, int) and selections >= 1, f"question {question_id} has invalid required_selections")
        validation.check(len(correct_options) == selections, f"question {question_id} correct options do not match required_selections")
        validation.check(len(correct_options) == len(set(correct_options)), f"question {question_id} has duplicate correct options")
        validation.check(all(re.fullmatch(r"[A-Z]", str(option)) for option in correct_options), f"question {question_id} has invalid correct option ids")
        if question.get("question_type") == "single-choice":
            validation.check(selections == 1, f"single-choice question {question_id} must require one selection")
        if question.get("question_type") == "multiple-select":
            validation.check(isinstance(selections, int) and selections >= 2, f"multiple-select question {question_id} must require at least two selections")
        validation.check(set(question.get("answer_source_ids", [])) <= set(source_ids), f"question {question_id} references an unknown answer source")
        validation.check(set(question.get("further_reading_source_ids", [])) <= set(source_ids), f"question {question_id} references an unknown further-reading source")
        validation.check("answer_source_ids" in question, f"question {question_id} must declare answer_source_ids")
        validation.check("further_reading_source_ids" in question, f"question {question_id} must declare further_reading_source_ids")
        file_value = question.get("file")
        validation.check(isinstance(file_value, str) and is_safe_repo_path(file_value), f"question {question_id} needs a safe file path")
        if isinstance(file_value, str) and is_safe_repo_path(file_value):
            validation.check((exam_root / file_value).is_file(), f"question {question_id} file does not exist: {file_value}")
            if (exam_root / file_value).is_file() and question_status in {"review", "complete"}:
                question_text = (exam_root / file_value).read_text(encoding="utf-8")
                for heading in ["問題", "選択肢", "正解", "正解理由", "各誤答が誤りである理由", "周辺知識", "解答根拠", "追加学習"]:
                    validation.check(markdown_section_has_content(question_text, heading), f"question {question_id} has no content in section: {heading}")
        if question_status in {"review", "complete"}:
            validation.check(bool(question.get("answer_source_ids")), f"question {question_id} needs answer sources before review")
            validation.check(bool(question.get("further_reading_source_ids")), f"question {question_id} needs further-reading sources before review")

    objectives = matrix.get("objectives", [])
    objective_ids = [item.get("objective_id") for item in objectives]
    validation.check(set(objective_ids) == expected_objectives, "Coverage Matrix objectives differ from exam config")
    validation.check(len(objective_ids) == len(set(objective_ids)), "Coverage Matrix has duplicate objective ids")
    topic_rows = []
    all_topic_ids = []
    for objective in objectives:
        for topic in objective.get("topics", []):
            all_topic_ids.append(topic.get("topic_id"))
            topic_rows.append(str(topic.get("topic_id")) + "|" + "|".join(topic.get("scope", [])))
    topic_digest = hashlib.sha256("\n".join(sorted(topic_rows)).encode()).hexdigest()
    expected_topic_count = expected.get("topic_count")
    if expected_topic_count is not None:
        validation.check(len(all_topic_ids) == expected_topic_count, f"Coverage Matrix must contain {expected_topic_count} official topics")
    validation.check(len(all_topic_ids) == len(set(all_topic_ids)), "Coverage Matrix has duplicate topic ids")
    if expected.get("topic_scope_sha256"):
        validation.check(topic_digest == expected.get("topic_scope_sha256"), "official topic ids or scopes differ from the verified exam blueprint")
    for objective in objectives:
        objective_id = objective.get("objective_id", "<missing>")
        status = objective.get("status")
        validation.check(status in ALLOWED_STATUSES, f"objective {objective_id} has invalid status")
        validation.check(objective.get("domain") in domain_ids, f"objective {objective_id} references an unknown domain")

        chapter = objective.get("chapter", "")
        validation.check(is_safe_repo_path(chapter), f"objective {objective_id} has an unsafe chapter path")
        chapter_path = exam_root / chapter
        validation.check(chapter_path.is_file(), f"objective {objective_id} chapter does not exist: {chapter}")
        if chapter_path.is_file():
            chapter_text = chapter_path.read_text(encoding="utf-8")
            validation.check(f"# {objective_id} " in chapter_text, f"chapter {chapter} does not declare objective {objective_id}")
            validation.check(f"> Status: {status}" in chapter_text, f"chapter {chapter} status differs from Coverage Matrix")

        topics = objective.get("topics", [])
        validation.check(bool(topics), f"objective {objective_id} has no official topics")
        for topic in topics:
            topic_id = topic.get("topic_id", "<missing>")
            topic_status = topic.get("status")
            validation.check(str(topic_id).startswith(f"{objective_id}."), f"topic {topic_id} is under the wrong objective")
            validation.check(topic_status in ALLOWED_STATUSES, f"topic {topic_id} has invalid status")
            validation.check(isinstance(topic.get("scope"), list), f"topic {topic_id} needs a scope list")
            anchor = topic.get("chapter_anchor")
            validation.check(isinstance(anchor, str) and bool(anchor), f"topic {topic_id} needs a chapter anchor")
            if chapter_path.is_file() and isinstance(anchor, str):
                validation.check(f'id="{anchor}"' in chapter_text, f"chapter {chapter} is missing anchor for topic {topic_id}")
            topic_sources = set(topic.get("source_ids", []))
            topic_diagrams = set(topic.get("diagram_ids", []))
            topic_questions = topic.get("question_ids", {})
            if topic_status != "planned":
                validation.check("source_ids" in topic, f"topic {topic_id} must declare source_ids after planning")
                validation.check("diagram_ids" in topic, f"topic {topic_id} must declare diagram_ids after planning")
                validation.check("question_ids" in topic, f"topic {topic_id} must declare question_ids after planning")
                validation.check(all(layer in topic_questions for layer in ("chapter", "domain", "mock")), f"topic {topic_id} must declare every question layer after planning")
            validation.check(topic_sources <= set(source_ids), f"topic {topic_id} references an unknown source")
            validation.check(topic_diagrams <= set(diagram_ids), f"topic {topic_id} references an unknown diagram")
            for diagram_id in topic_diagrams:
                diagram_entry = next(item for item in diagrams if item.get("id") == diagram_id)
                validation.check(objective_id in diagram_entry.get("objective_ids", []), f"diagram {diagram_id} does not map back to objective {objective_id}")
            referenced_questions = []
            for layer in ("chapter", "domain", "mock"):
                layer_question_ids = topic_questions.get(layer, [])
                referenced_questions += layer_question_ids
                for referenced_id in layer_question_ids:
                    if referenced_id in questions_by_id:
                        referenced = questions_by_id[referenced_id]
                        validation.check(referenced.get("layer") == layer, f"topic {topic_id} references {referenced_id} in the wrong layer")
                        validation.check(objective_id in referenced.get("objective_ids", []), f"question {referenced_id} does not map back to objective {objective_id}")
                        if topic_status == "complete":
                            validation.check(referenced.get("status") == "complete", f"complete topic {topic_id} references incomplete question {referenced_id}")
            validation.check(set(referenced_questions) <= set(question_ids), f"topic {topic_id} references an unknown question")
            if topic_status in {"review", "complete"}:
                validation.check(bool(topic_sources), f"topic {topic_id} needs official sources before review")
                validation.check(topic.get("last_verified") is not None, f"topic {topic_id} needs last_verified before review")
            if topic_status == "complete":
                for layer in ("chapter", "domain", "mock"):
                    validation.check(bool(topic_questions.get(layer)), f"complete topic {topic_id} needs {layer} questions")
        if status == "complete":
            validation.check(all(topic.get("status") == "complete" for topic in topics), f"complete objective {objective_id} has incomplete topics")
            validation.check(objective.get("last_verified") is not None, f"complete objective {objective_id} needs last_verified")

    if exam_metadata.get("release_status") == "complete":
        for key, value in config.get("release_completion_requirements", {}).items():
            validation.check(exam_metadata.get(key) == value, f"complete exam coverage requires exam.{key}={value}")
        validation.check(all(item.get("status") == "complete" for item in objectives), "complete exam coverage requires every objective to be complete")

    required_template_sections = {
        "shared/templates/chapter.md": ["## 前提知識", "## この章の用語", "## What", "## How", "## When / Why", "## Compare", "## 確認問題", "## 章のまとめ", "## 次に学ぶこと", "## 根拠"],
        "shared/templates/question.md": ["## 問題", "## 選択肢", "## 正解理由", "## 各誤答", "## 周辺知識", "## 解答根拠", "## 追加学習"],
    }
    for relative_path, headings in required_template_sections.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        for heading in headings:
            validation.check(heading in text, f"{relative_path} is missing required section: {heading}")

    summary = (
        f"{config.get('id')}: {len(objectives)} objectives, {len(all_topic_ids)} topics, "
        f"{len(sources)} sources, {len(diagrams)} diagrams, {len(questions)} questions"
    )
    return validation, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exam", help="Exam directory or exam-config.json path; validates all exams when omitted")
    args = parser.parse_args()

    config_paths = find_exam_configs(args.exam)
    package_ids = [load_json(path).get("id") for path in config_paths]
    if len(package_ids) != len(set(package_ids)):
        print("Validation failed: exam package ids must be unique.")
        return 1

    failures = 0
    for config_path in config_paths:
        validation, summary = validate_exam(config_path)
        if validation.errors:
            failures += 1
            print(f"Validation failed for {summary} with {len(validation.errors)} error(s):")
            for error in validation.errors:
                print(f"- {error}")
        else:
            print(f"Validation passed: {summary}.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
