#!/usr/bin/env python3
"""Render a reproducible mock set with separate question and answer documents."""

from __future__ import annotations

import argparse
import os
import re
from collections import Counter
from pathlib import Path

from build_blind_exam import load_json, resolve_exam


def allocate_questions(weights: dict[int, int], count: int) -> dict[int, int]:
    """Use largest remainders; break ties by weight, then Domain number."""
    if not isinstance(count, int) or count <= 0 or sum(weights.values()) != 100:
        raise ValueError('question count must be positive and Domain weights must total 100')
    counts = {domain: count * weight // 100 for domain, weight in weights.items()}
    priority = sorted(weights, key=lambda d: (-(count * weights[d] % 100), -weights[d], d))
    for domain in priority[:count - sum(counts.values())]:
        counts[domain] += 1
    return counts


def load_sets(exam: Path) -> tuple[dict, dict[str, dict]]:
    config = load_json(exam / 'exam-config.json')
    manifest_path = config.get('registries', {}).get('mock_sets', 'docs/mock-sets.json')
    manifest = load_json(exam / manifest_path)
    questions = load_json(exam / config['registries']['questions'])['questions']
    return manifest, {q['id']: q for q in questions}


def render_set(exam: Path, spec: dict, registry: dict[str, dict], answers: bool = False) -> str:
    config = load_json(exam / 'exam-config.json')
    weights = {int(d): w for d, w in config['expected']['domain_weights'].items()}
    ids = spec['question_ids']
    if not ids or len(ids) != len(set(ids)):
        raise ValueError('mock set must contain unique question IDs')
    if len(ids) != spec['question_count']:
        raise ValueError('mock set question count does not match its question IDs')
    counts = Counter()
    objectives = set()
    for qid in ids:
        if qid not in registry:
            raise ValueError(f'unknown question: {qid}')
        q = registry[qid]
        domains = {int(o.split('.')[0]) for o in q['objective_ids']}
        if q['layer'] != 'mock' or q['status'] != 'complete' or len(domains) != 1:
            raise ValueError(f'question must be a complete, single-Domain mock question: {qid}')
        counts.update(domains)
        objectives.update(q['objective_ids'])
    if dict(counts) != allocate_questions(weights, len(ids)):
        raise ValueError(f'mock set Domain counts differ from the blueprint allocation: {dict(counts)}')
    if objectives != set(config['expected']['objective_ids']):
        raise ValueError('mock set must cover every Objective')
    relative_output = spec['answer_file'] if answers else spec['question_file']
    output = exam / relative_output
    if Path(relative_output).is_absolute() or '..' in Path(relative_output).parts:
        raise ValueError('mock output must be inside the exam package')
    label = '解答・復習' if answers else '問題'
    parts = [f"# {spec['title']} — {label}", '',
             f"問題数: {len(ids)}。各問は必要な選択数をすべて選び、選択肢の集合が一致した場合に1点とします。部分点はありません。", '']
    if answers:
        parts += ['この点数は教材の理解確認用です。実試験の得点尺度や合格判定とは異なります。', '']
        parts += ['## 採点一覧', '', '| 問題 | 正解 | Domain |', '|---|---|---|']
        for position, qid in enumerate(ids, 1):
            q = registry[qid]
            domain = q['objective_ids'][0].split('.')[0]
            parts += [f"| [第{position}問](#第{position}問) | {', '.join(q['correct_option_ids'])} | {domain} |"]
        parts += ['', '## Domain別の振り返り', '', '| Domain | 問題数 | 正答数 | 正答率 |', '|---|---|---|---|']
        parts += [f'| {domain} | {counts[domain]} | 記入 | 記入 |' for domain in sorted(weights)]
        parts += ['', '総合正答率と各Domainの正答率を記録し、誤答したObjectiveの本文へ戻って復習します。', '']
    else:
        parts += [f"練習時間の目安: {spec['practice_time_minutes']}分。解答・解説を開かずに全問を解き、回答を記録してから採点します。", '']
    matrix = load_json(exam / config['registries']['coverage_matrix'])
    chapters = {o['objective_id']: o['chapter'] for o in matrix['objectives']}
    for position, qid in enumerate(ids, 1):
        q = registry[qid]
        source = exam / q['file']
        text = source.read_text(encoding='utf-8')
        marker = '\n## 正解\n'
        if marker not in text:
            raise ValueError(f'question has no answer heading: {qid}')
        before, after = text.split(marker, 1)
        parts += [f'## 第{position}問', '']
        if answers:
            link = Path(os.path.relpath(source, output.parent)).as_posix()
            parts += [f"出題元: [{qid}]({link}) / Objective: {', '.join(q['objective_ids'])}", '']
            study_links = []
            for objective in q['objective_ids']:
                chapter_link = Path(os.path.relpath(exam / chapters[objective], output.parent)).as_posix()
                study_links.append(f'[Objective {objective}の本文]({chapter_link})')
            parts += ['復習: ' + ' / '.join(study_links), '', '### 正解', '']
            body = after
        else:
            parts += [f"必要選択数: {q['required_selections']}", '']
            body = before.split('\n## 問題\n', 1)[1]
        body = re.sub(r'^## ', '### ', body.strip(), flags=re.MULTILINE)
        # Question files can contain relative study links; resolve them from their source.
        def rebase(match):
            target = match.group(2)
            if target.startswith(('https://', 'http://', '#')):
                return match.group(0)
            path, separator, anchor = target.partition('#')
            rebased = Path(os.path.relpath(source.parent / path, output.parent)).as_posix()
            return f'[{match.group(1)}]({rebased}{separator}{anchor})'
        body = re.sub(r'\[([^\]]*)\]\(([^)]+)\)', rebase, body)
        parts += [body, '']
    return '\n'.join(parts).rstrip() + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exam', required=True)
    parser.add_argument('--set', required=True, dest='set_id')
    parser.add_argument('--check', action='store_true', help='Check committed documents without writing')
    args = parser.parse_args()
    exam = resolve_exam(args.exam)
    manifest, registry = load_sets(exam)
    matches = [spec for spec in manifest['sets'] if spec['id'] == args.set_id]
    if len(matches) != 1:
        parser.error('set ID must identify exactly one set')
    spec = matches[0]
    for answers, key in ((False, 'question_file'), (True, 'answer_file')):
        rendered = render_set(exam, spec, registry, answers)
        path = exam / spec[key]
        if args.check:
            if not path.is_file() or path.read_text(encoding='utf-8') != rendered:
                raise SystemExit(f'Mock document is missing or stale: {path}')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(rendered, encoding='utf-8')
        print(('Checked: ' if args.check else 'Written: ') + str(path))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
