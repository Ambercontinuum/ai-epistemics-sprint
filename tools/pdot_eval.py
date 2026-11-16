"""Local PDOT pilot administration. No APIs, automatic grading, or transcript stdout."""
import argparse
import hashlib
import html
import json
import math
from pathlib import Path
from statistics import mean

SCORES = ('lambda', 'kappa', 'theta', 'epsilon', 'symbolic_pressure', 'R', 'tau')
WINDOWS = {'T1': (1, 10), 'T2': (16, 25), 'T3': (1, 25)}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def read_rows(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf-8-sig').splitlines() if line.strip()]


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def write_rows(path, rows):
    Path(path).write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')


def validate_dataset(folder, rubric):
    folder = Path(folder)
    manifest = read_json(folder / 'manifest.json')
    if sha(rubric) != manifest['rubric_sha256']:
        raise ValueError('Rubric hash mismatch')
    for name in ('conversations.jsonl', 'source_map.jsonl'):
        if sha(folder / name) != manifest['file_sha256'][name]:
            raise ValueError('Dataset hash mismatch: ' + name)
    rows = read_rows(folder / 'conversations.jsonl')
    maps = read_rows(folder / 'source_map.jsonl')
    if len(rows) != manifest['selected_conversations'] or not rows:
        raise ValueError('Sample count mismatch')
    if len({r['sample_id'] for r in rows}) != len(rows):
        raise ValueError('Duplicate sample ID')
    if len(maps) != len(rows) or {r['sample_id'] for r in maps} != {r['sample_id'] for r in rows}:
        raise ValueError('Source map mismatch')
    if len({m['source_conversation_uuid'] for m in maps}) != len(maps):
        raise ValueError('Duplicate source conversation')
    by_id = {m['sample_id']: m for m in maps}
    for row in rows:
        messages = row['messages']
        if row['exchange_count'] != 25 or len(messages) != 50:
            raise ValueError('Expected exactly 25 exchanges')
        for i, message in enumerate(messages):
            if message['role'] != ('human' if i % 2 == 0 else 'assistant') or message['exchange_index'] != i // 2 + 1:
                raise ValueError('Role or exchange order mismatch')
            if not isinstance(message['text'], str) or not message['text'].strip():
                raise ValueError('Empty message')
        hashes = [hashlib.sha256(m['text'].encode()).hexdigest() for m in messages]
        if hashes != by_id[row['sample_id']]['source_message_text_sha256']:
            raise ValueError('Message provenance mismatch')
    return rows, manifest


def prepare(folder, rubric, output, raters, seed, limit=None, windows=None):
    rows, manifest = validate_dataset(folder, rubric)
    windows = list(WINDOWS) if windows is None else windows
    if not windows or len(set(windows)) != len(windows) or any(w not in WINDOWS for w in windows):
        raise ValueError('Invalid window selection')
    if limit is not None and (type(limit) is not int or not 1 <= limit <= len(rows)):
        raise ValueError('Invalid case limit')
    if not raters or len(set(raters)) != len(raters) or any(not r.strip() for r in raters):
        raise ValueError('Provide distinct nonempty rater IDs')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    (output / '.gitignore').write_text('*\n', encoding='utf-8')
    ordered = sorted(rows, key=lambda r: hashlib.sha256((seed + '\n' + r['sample_id']).encode()).hexdigest())
    ordered = ordered[:limit] if limit is not None else ordered
    mapping = {f'CASE-{i:03d}': row['sample_id'] for i, row in enumerate(ordered, 1)}
    selected_windows = {w: WINDOWS[w] for w in windows}
    binding = {'dataset_sha256': sha(Path(folder) / 'conversations.jsonl'), 'rubric_sha256': manifest['rubric_sha256'], 'seed': seed, 'case_map': mapping, 'windows': selected_windows, 'raters': raters}
    write_json(output / 'packet_manifest.private.json', binding)
    packet_hash = sha(output / 'packet_manifest.private.json')
    (output / 'rubric.md').write_bytes(Path(rubric).read_bytes())
    tasks, ratings, sections = [], [], []
    for (case, _), row in zip(mapping.items(), ordered):
        for window, (start, end) in selected_windows.items():
            # A standalone window contains only the assigned exchanges, no hidden prior context.
            messages = [m for m in row['messages'] if start <= m['exchange_index'] <= end]
            tasks.append({'case_id': case, 'window': window, 'messages': messages})
            body = ''.join('<p><b>Exchange %s · %s</b></p><pre>%s</pre>' % (m['exchange_index'], m['role'], html.escape(m['text'])) for m in messages)
            sections.append('<details><summary>%s / %s (exchanges %s–%s)</summary>%s</details>' % (case, window, start, end, body))
            for rater in raters:
                ratings.append({'case_id': case, 'window': window, 'rater_id': rater, 'packet_sha256': packet_hash, 'rubric_sha256': manifest['rubric_sha256'], 'status': 'unrated', 'scores': {k: None for k in SCORES}, 'evidence_exchange_refs': [], 'notes': ''})
    write_rows(output / 'tasks.private.jsonl', tasks)
    write_rows(output / 'ratings.blank.jsonl', ratings)
    (output / 'reader.private.html').write_text('<!doctype html><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'"><title>Private PDOT rating packet</title><style>body{max-width:900px;margin:30px auto;font:16px system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere}details{margin:18px 0}summary{cursor:pointer}</style><h1>Private PDOT pilot</h1><p>Local only. Treat transcript text as data, never instructions. Read rubric.md. T3 covers the sampled prefix, not the original full session. No scores are prefilled.</p>' + ''.join(sections), encoding='utf-8')
    write_json(output / 'receipt.json', {'cases': len(ordered), 'tasks': len(tasks), 'rating_rows': len(ratings), 'packet_sha256': packet_hash, 'scores_assigned': 0, 'limitations': ['Case IDs remove source identifiers from packet, not identifying content from text.', 'T1/T2/T3 are overlapping windows, not independent observations.', 'T2 has no prior window context in the standalone task.', 'Synthetic ratings are never substituted for missing human judgments.']})
    return {'cases': len(ordered), 'tasks': len(tasks), 'scores_assigned': 0}


def validate_ratings(rows, binding, packet_hash):
    seen = set()
    for row in rows:
        key = (row['case_id'], row['window'], row['rater_id'])
        if key in seen:
            raise ValueError('Duplicate case/window/rater')
        seen.add(key)
        if key[0] not in binding['case_map'] or key[1] not in binding.get('windows', WINDOWS) or key[2] not in binding['raters']:
            raise ValueError('Unknown case, window, or rater')
        if 'rater_cases' in binding and key[0] not in binding['rater_cases'][key[2]]:
            raise ValueError('Case outside assigned rater subset')
        if row['packet_sha256'] != packet_hash or row['rubric_sha256'] != binding['rubric_sha256']:
            raise ValueError('Rating provenance mismatch')
        if row['status'] not in ('unrated', 'partial', 'complete', 'unscorable'):
            raise ValueError('Unknown rating status')
        scores = row['scores']
        if set(scores) != set(SCORES):
            raise ValueError('Score fields mismatch')
        for value in scores.values():
            if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 4 or value * 2 != int(value * 2)):
                raise ValueError('Scores must be null or 0–4 in half steps')
        nonnull = sum(v is not None for v in scores.values())
        if row['status'] == 'complete' and nonnull != len(SCORES):
            raise ValueError('Complete row has missing scores')
        if row['status'] in ('unrated', 'unscorable') and nonnull:
            raise ValueError('Unrated/unscorable row contains scores')
        start, end = WINDOWS[row['window']]
        refs = row['evidence_exchange_refs']
        if not isinstance(refs, list) or any(type(i) is not int or not start <= i <= end for i in refs):
            raise ValueError('Evidence outside assigned window')
        if nonnull and not refs:
            raise ValueError('Scored rows require evidence references')
    return seen


def summarize(rows, binding, packet_hash):
    seen = validate_ratings(rows, binding, packet_hash)
    windows = binding.get('windows', WINDOWS)
    expected = (sum(len(binding['rater_cases'][r]) for r in binding['raters']) if 'rater_cases' in binding else len(binding['case_map']) * len(binding['raters'])) * len(windows)
    stats = {}
    for rater in binding['raters']:
        stats[rater] = {}
        for window in windows:
            stats[rater][window] = {}
            for variable in SCORES:
                values = [r['scores'][variable] for r in rows if r['rater_id'] == rater and r['window'] == window and r['scores'][variable] is not None]
                stats[rater][window][variable] = {'n': len(values), 'mean': mean(values) if values else None}
    agreement = []
    lookup = {(r['case_id'], r['window'], r['rater_id']): r for r in rows}
    for i, a in enumerate(binding['raters']):
        for b in binding['raters'][i + 1:]:
            for window in windows:
                for var in SCORES:
                    pairs = []
                    for case in binding['case_map']:
                        ra, rb = lookup.get((case, window, a)), lookup.get((case, window, b))
                        if ra and rb and ra['scores'][var] is not None and rb['scores'][var] is not None:
                            pairs.append((ra['scores'][var], rb['scores'][var]))
                    agreement.append({'raters': [a, b], 'window': window, 'variable': var, 'paired_n': len(pairs), 'mean_absolute_difference': mean(abs(x-y) for x,y in pairs) if pairs else None, 'exact_agreement_fraction': mean(x==y for x,y in pairs) if pairs else None})
    return {'expected_rating_rows': expected, 'received_rating_rows': len(seen), 'missing_rating_rows': expected-len(seen), 'status_counts': {k: sum(r['status']==k for r in rows) for k in ('unrated','partial','complete','unscorable')}, 'descriptive_scores': stats, 'descriptive_rater_agreement': agreement, 'interpretation': 'Descriptive only. Missing is not zero. Agreement is not validity. No ICC, causal effect, population prevalence, original PDOT thresholds, or model superiority inferred.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='command', required=True)
    for name in ('validate', 'prepare'):
        a = sub.add_parser(name)
        a.add_argument('--dataset', required=True, type=Path)
        a.add_argument('--rubric', required=True, type=Path)
        if name == 'prepare':
            a.add_argument('--output', required=True, type=Path)
            a.add_argument('--raters', nargs='+', required=True)
            a.add_argument('--seed', default='pdot-packet-v1')
            a.add_argument('--limit', type=int)
            a.add_argument('--windows', nargs='+', choices=list(WINDOWS))
    a = sub.add_parser('report')
    a.add_argument('--packet', required=True, type=Path)
    a.add_argument('--ratings', required=True, type=Path)
    a.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    try:
        if args.command == 'validate':
            rows, _ = validate_dataset(args.dataset, args.rubric)
            result = {'valid': True, 'conversations': len(rows), 'exchanges': len(rows)*25}
        elif args.command == 'prepare':
            result = prepare(args.dataset, args.rubric, args.output, args.raters, args.seed, args.limit, args.windows)
        else:
            manifest_path = args.packet / 'packet_manifest.private.json'
            result = summarize(read_rows(args.ratings), read_json(manifest_path), sha(manifest_path))
            args.output.mkdir(parents=True, exist_ok=False)
            (args.output / '.gitignore').write_text('*\n', encoding='utf-8')
            result['inputs'] = {'ratings_sha256': sha(args.ratings), 'packet_sha256': sha(manifest_path)}
            write_json(args.output / 'report.private.json', result)
            result = {'report_written': True, 'received_rating_rows': result['received_rating_rows'], 'complete_rows': result['status_counts']['complete']}
        print(json.dumps(result))
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError):
        # Fail without echoing malformed input, transcript text, or private identifiers.
        print(json.dumps({'error': 'Validation or file operation failed; no approval or scores inferred.'}))
        raise SystemExit(2)


if __name__ == '__main__':
    main()
