#!/usr/bin/env python3
"""Validate the COF-C03 content registries using only the Python standard library."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ALLOWED_STATUSES = {"planned", "draft", "review", "complete"}
EXPECTED_OBJECTIVES = {
    "1.1", "1.2", "1.3", "1.4", "1.5", "1.6",
    "2.1", "2.2", "2.3",
    "3.1", "3.2", "3.3",
    "4.1", "4.2", "4.3", "4.4",
    "5.1", "5.2", "5.3",
}
EXPECTED_WEIGHTS = {1: 31, 2: 20, 3: 18, 4: 21, 5: 10}
OFFICIAL_HOSTS = {
    "docs.snowflake.com",
    "learn.snowflake.com",
    "www.snowflake.com",
    "snowflake.com",
    "publish-p93462-e887935.adobeaemcloud.com",
}


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def load_json(relative_path: str):
    path = ROOT / relative_path
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot read {relative_path}: {exc}") from exc


def is_safe_repo_path(value: str) -> bool:
    path = Path(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts


def main() -> int:
    validation = Validation()
    matrix = load_json("docs/coverage-matrix.json")
    source_data = load_json("docs/sources.json")
    diagram_data = load_json("docs/diagrams.json")
    question_data = load_json("docs/questions.json")

    sources = source_data.get("sources", [])
    source_ids = [item.get("id") for item in sources]
    validation.check(len(source_ids) == len(set(source_ids)), "sources.json has duplicate ids")
    for source in sources:
        source_id = source.get("id", "<missing>")
        parsed = urlparse(source.get("url", ""))
        validation.check(
            parsed.scheme == "https" and parsed.hostname in OFFICIAL_HOSTS,
            f"source {source_id} is not an allowed Snowflake official HTTPS URL",
        )
        validation.check(
            bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", source.get("checked_on", ""))),
            f"source {source_id} has no valid checked_on date",
        )
        validation.check(source.get("status") in {"active", "superseded", "unavailable"}, f"source {source_id} has invalid status")

    domains = matrix.get("domains", [])
    weights = {item.get("id"): item.get("weight_percent") for item in domains}
    validation.check(weights == EXPECTED_WEIGHTS, f"domain weights differ from C03 guide: {weights}")
    validation.check(sum(weights.values()) == 100, "domain weights do not total 100")
    validation.check(matrix.get("exam", {}).get("study_guide_source_id") in source_ids, "exam study guide source is missing")

    diagrams = diagram_data.get("diagrams", [])
    diagram_ids = [item.get("id") for item in diagrams]
    validation.check(len(diagram_ids) == len(set(diagram_ids)), "diagrams.json has duplicate ids")
    for diagram in diagrams:
        diagram_id = diagram.get("id", "<missing>")
        validation.check(diagram.get("status") in ALLOWED_STATUSES, f"diagram {diagram_id} has invalid status")
        validation.check(set(diagram.get("objective_ids", [])) <= EXPECTED_OBJECTIVES, f"diagram {diagram_id} references an unknown objective")
        validation.check(set(diagram.get("source_ids", [])) <= set(source_ids), f"diagram {diagram_id} references an unknown source")
        if diagram.get("status") != "planned":
            file_value = diagram.get("file")
            validation.check(isinstance(file_value, str) and is_safe_repo_path(file_value), f"diagram {diagram_id} needs a safe file path")
            if isinstance(file_value, str) and is_safe_repo_path(file_value):
                validation.check((ROOT / file_value).is_file(), f"diagram {diagram_id} file does not exist: {file_value}")
            validation.check(bool(diagram.get("source_ids")), f"diagram {diagram_id} needs official sources")

    questions = question_data.get("questions", [])
    question_ids = [item.get("id") for item in questions]
    validation.check(len(question_ids) == len(set(question_ids)), "questions.json has duplicate ids")
    for question in questions:
        question_id = question.get("id", "<missing>")
        validation.check(question.get("layer") in {"chapter", "domain", "mock"}, f"question {question_id} has invalid layer")
        validation.check(set(question.get("objective_ids", [])) <= EXPECTED_OBJECTIVES, f"question {question_id} references an unknown objective")
        validation.check(set(question.get("answer_source_ids", [])) <= set(source_ids), f"question {question_id} references an unknown answer source")
        file_value = question.get("file")
        validation.check(isinstance(file_value, str) and is_safe_repo_path(file_value), f"question {question_id} needs a safe file path")
        if isinstance(file_value, str) and is_safe_repo_path(file_value):
            validation.check((ROOT / file_value).is_file(), f"question {question_id} file does not exist: {file_value}")

    objectives = matrix.get("objectives", [])
    objective_ids = [item.get("objective_id") for item in objectives]
    validation.check(set(objective_ids) == EXPECTED_OBJECTIVES, "Coverage Matrix does not contain exactly all 19 C03 objectives")
    validation.check(len(objective_ids) == len(set(objective_ids)), "Coverage Matrix has duplicate objective ids")
    for objective in objectives:
        objective_id = objective.get("objective_id", "<missing>")
        status = objective.get("status")
        validation.check(status in ALLOWED_STATUSES, f"objective {objective_id} has invalid status")
        expected_domain = int(str(objective_id).split(".")[0]) if re.fullmatch(r"[1-5]\.\d", str(objective_id)) else None
        validation.check(objective.get("domain") == expected_domain, f"objective {objective_id} has wrong domain")

        chapter = objective.get("chapter", "")
        validation.check(is_safe_repo_path(chapter), f"objective {objective_id} has an unsafe chapter path")
        chapter_path = ROOT / chapter
        validation.check(chapter_path.is_file(), f"objective {objective_id} chapter does not exist: {chapter}")
        if chapter_path.is_file():
            chapter_text = chapter_path.read_text(encoding="utf-8")
            validation.check(f"# {objective_id} " in chapter_text, f"chapter {chapter} does not declare objective {objective_id}")
            validation.check(f"> Status: {status}" in chapter_text, f"chapter {chapter} status differs from Coverage Matrix")

        technical_sources = set(objective.get("technical_source_ids", []))
        answer_sources = set(objective.get("answer_source_ids", []))
        further_sources = set(objective.get("further_reading_source_ids", []))
        validation.check(technical_sources <= set(source_ids), f"objective {objective_id} references an unknown technical source")
        validation.check(answer_sources <= set(source_ids), f"objective {objective_id} references an unknown answer source")
        validation.check(further_sources <= set(source_ids), f"objective {objective_id} references an unknown further-reading source")

        diagram = objective.get("diagram", {})
        objective_diagrams = set(diagram.get("ids", []))
        validation.check(objective_diagrams <= set(diagram_ids), f"objective {objective_id} references an unknown diagram")
        validation.check(not diagram.get("required") or bool(objective_diagrams), f"objective {objective_id} requires a diagram but has no diagram id")

        all_question_ids = (
            objective.get("chapter_question_ids", [])
            + objective.get("domain_question_ids", [])
            + objective.get("mock_question_ids", [])
        )
        validation.check(set(all_question_ids) <= set(question_ids), f"objective {objective_id} references an unknown question")

        if status in {"review", "complete"}:
            validation.check(bool(technical_sources), f"objective {objective_id} needs technical sources before review")
            validation.check(objective.get("last_verified") is not None, f"objective {objective_id} needs last_verified before review")
        if status == "complete":
            validation.check(bool(objective.get("chapter_question_ids")), f"complete objective {objective_id} needs chapter questions")
            validation.check(bool(objective.get("domain_question_ids")), f"complete objective {objective_id} needs domain questions")
            validation.check(bool(objective.get("mock_question_ids")), f"complete objective {objective_id} needs mock questions")
            validation.check(bool(answer_sources), f"complete objective {objective_id} needs answer sources")
            if diagram.get("required"):
                states = {item["id"]: item["status"] for item in diagrams}
                validation.check(all(states[item] == "complete" for item in objective_diagrams), f"complete objective {objective_id} has incomplete diagrams")

    required_template_sections = {
        "templates/chapter.md": ["## What", "## How", "## When / Why", "## Compare", "## 確認問題", "## 根拠"],
        "templates/question.md": ["## 問題", "## 選択肢", "## 正解理由", "## 各誤答", "## 周辺知識", "## 解答根拠", "## 追加学習"],
    }
    for relative_path, headings in required_template_sections.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        for heading in headings:
            validation.check(heading in text, f"{relative_path} is missing required section: {heading}")

    if validation.errors:
        print(f"Validation failed with {len(validation.errors)} error(s):")
        for error in validation.errors:
            print(f"- {error}")
        return 1

    print(
        f"Validation passed: {len(objectives)} objectives, "
        f"{len(sources)} sources, {len(diagrams)} diagrams, {len(questions)} questions."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
