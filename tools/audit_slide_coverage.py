"""Check that each teaching slide has a four-choice question and a slide answer."""

import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'On_KTPM' / 'web'
base = json.loads((ROOT / 'questions.json').read_text()) + json.loads((ROOT / 'pdf-questions.json').read_text())
base = [q for q in base if q['kind'] in ('main', 'pdf')]
extra = json.loads((ROOT / 'extra-questions.json').read_text())
added = json.loads((ROOT / 'slide-coverage-questions.json').read_text())
written = json.loads((ROOT / 'written-exam-questions.json').read_text())
quiz_links = json.loads((ROOT / 'reviewed-quiz-links.json').read_text())

assert len(added) == 48 and len(written) == 28
assert len({q['id'] for q in added}) == len(added)

for q in added:
    assert len(q['options']) == 4 and q['answer'] in 'ABCD', q['id']
    assert q['followup']['q'] and q['followup']['a'], q['id']
    assert q['followup']['a'] != q['options']['ABCD'.index(q['answer'])], q['id']
    assert (ROOT / 'slides' / q['file'][:-4] / f"{q['page']:03}.jpg").is_file(), q['id']

for q in base:
    if not q.get('file') or not q.get('page'):
        continue
    page_key = f"{q['file'].split('_')[1]}:{q['page']}"
    same_slide = any(x.get('tag') == 'Cùng slide' and f"tr. {q['page']}" in x.get('source', '') for x in extra[q['id']])
    same_slide |= any(x.get('tag') == 'Từ QUIZ' for x in extra[q['id']]) and page_key in quiz_links
    assert same_slide, f"No slide-grounded follow-up for {q['id']}"

covered = {(q['file'], q['page']) for q in base + added}
missing = []
count = Counter()
for pdf in sorted(ROOT.glob('BaiGiang_*.pdf')):
    pages = subprocess.run(['pdftotext', '-layout', str(pdf), '-'], check=True, capture_output=True, text=True).stdout.split('\f')[:-1]
    for page, content in enumerate(pages, 1):
        if page <= 3:
            continue
        if any(marker in content[:200] for marker in (
            'THỜI LƯỢNG', 'BÀI TẬP', 'CÂU HỎI ÔN TẬP', 'TÓM TẮT CHƯƠNG',
            'ĐÁNH GIÁ', 'BÀI QUIZ', 'BÀI KIỂM TRA VIẾT',
        )):
            continue
        if (pdf.name, page) not in covered:
            heading = next((re.sub(r'\s+', ' ', line).strip() for line in content.splitlines() if line.strip()), '')
            missing.append((pdf.name.split('_')[1], page, heading))
        else:
            count[pdf.name.split('_')[1]] += 1

assert not missing, f"Teaching slides without an original question: {missing}"
print('Teaching slides covered by chapter:', dict(count))
print('New original questions:', len(added), 'with one slide-grounded follow-up each')
print('Existing originals with a slide-grounded follow-up:', sum(bool(q.get('file')) for q in base))
