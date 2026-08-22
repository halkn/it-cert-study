#!/usr/bin/env python3
"""Build an answer-free question bundle for model-based Domain evaluation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot read {path}: {exc}") from exc


def resolve_exam(value: str) -> Path:
    exam = Path(value)
    if not exam.is_absolute():
        exam = ROOT / exam
    exam = exam.resolve()
    try:
        exam.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"Exam must be inside the repository: {exam}") from exc
    if not (exam / "exam-config.json").is_file():
        raise SystemExit(f"Exam config does not exist: {exam / 'exam-config.json'}")
    return exam


def strip_answer_sections(text: str, question_id: str) -> str:
    marker = "\n## 正解"
    if marker not in text:
        raise SystemExit(f"Question {question_id} has no answer heading")
    return text.split(marker, 1)[0].rstrip()


def select_questions(exam: Path, domains: set[int]) -> list[dict]:
    config = load_json(exam / "exam-config.json")
    registry_path = exam / config["registries"]["questions"]
    questions = load_json(registry_path).get("questions", [])
    selected = []
    for question in questions:
        objective_domains = {int(item.split(".", 1)[0]) for item in question.get("objective_ids", [])}
        if question.get("layer") == "mock" and objective_domains and objective_domains <= domains:
            selected.append(question)
    if not selected:
        values = ", ".join(str(item) for item in sorted(domains))
        raise SystemExit(f"No mock questions are fully contained in Domain(s): {values}")
    return selected


def build_bundle(exam: Path, domains: set[int], mode: str) -> str:
    prompt_name = "textbook-only-prompt.md" if mode == "textbook-only" else "question-quality-prompt.md"
    prompt = (ROOT / "shared" / "evals" / prompt_name).read_text(encoding="utf-8").rstrip()
    parts = [
        "# Generated blind evaluation bundle",
        "",
        f"- Exam: `{exam.relative_to(ROOT)}`",
        f"- Domains: {', '.join(str(item) for item in sorted(domains))}",
        f"- Mode: `{mode}`",
        "- This bundle intentionally contains no answer or explanation sections.",
        "",
        prompt,
    ]

    if mode == "textbook-only":
        parts.extend(["", "# Allowed textbook content"])
        for domain in sorted(domains):
            textbook_dir = exam / "textbook" / f"domain-{domain}"
            files = sorted(textbook_dir.glob("*.md"))
            if not files:
                raise SystemExit(f"No textbook files found: {textbook_dir}")
            for path in files:
                parts.extend(
                    [
                        "",
                        f"## FILE: {path.relative_to(exam)}",
                        "",
                        path.read_text(encoding="utf-8").rstrip(),
                    ]
                )

    parts.extend(["", "# Blind questions"])
    for question in select_questions(exam, domains):
        path = exam / question["file"]
        if not path.is_file():
            raise SystemExit(f"Question file does not exist: {path}")
        parts.extend(
            [
                "",
                f"## FILE: {question['file']}",
                "",
                strip_answer_sections(path.read_text(encoding="utf-8"), question["id"]),
            ]
        )
    return "\n".join(parts).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exam", required=True, help="Exam directory or path relative to the repository")
    parser.add_argument("--domains", required=True, nargs="+", type=int, help="Domain numbers to include")
    parser.add_argument("--mode", choices=("question-quality", "textbook-only"), default="question-quality")
    parser.add_argument("--output", help="Output file; stdout is used when omitted")
    args = parser.parse_args()

    domains = set(args.domains)
    if not domains or any(item < 1 for item in domains):
        raise SystemExit("Domain numbers must be positive integers")
    bundle = build_bundle(resolve_exam(args.exam), domains, args.mode)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(bundle, encoding="utf-8")
    else:
        sys.stdout.write(bundle)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
