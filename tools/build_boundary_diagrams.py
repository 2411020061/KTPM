"""Draw the numbered equivalence-partition and boundary-value study grids."""

from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'On_KTPM/web/media/extra'
OUT.mkdir(parents=True, exist_ok=True)


def diagram(name, title, zones, points, footer):
    """points are (x, value, note, kind): invalid/valid/added/quiet."""
    palette = {
        'invalid': ('#fee2e2', '#b91c1c'),
        'valid': ('#dcfce7', '#15803d'),
        'added': ('#dbeafe', '#1d4ed8'),
        'quiet': ('#e2e8f0', '#475569'),
    }
    cells = []
    for index, (label, sub, tone) in enumerate(zones):
        fill, ink = palette[tone]
        x = 24 + index * 284
        cells.extend([
            f'<rect x="{x}" y="62" width="284" height="78" fill="{fill}"/>',
            f'<text x="{x+142}" y="94" text-anchor="middle" fill="{ink}" font-size="19" font-weight="700">{escape(label)}</text>',
            f'<text x="{x+142}" y="122" text-anchor="middle" fill="#334155" font-size="15">{escape(sub)}</text>',
        ])
    dots = []
    for x, value, note, tone in points:
        fill, ink = palette[tone]
        dots.extend([
            f'<circle cx="{x}" cy="190" r="25" fill="{ink}"/>',
            f'<text x="{x}" y="198" text-anchor="middle" fill="white" font-size="19" font-weight="700">{escape(str(value))}</text>',
            f'<text x="{x}" y="239" text-anchor="middle" fill="#334155" font-size="13">{escape(note)}</text>',
        ])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="300" viewBox="0 0 900 300" role="img" aria-labelledby="title">
<title id="title">{escape(title)}</title>
<rect width="900" height="300" rx="14" fill="white"/>
<text x="24" y="38" fill="#183153" font-size="23" font-weight="700">{escape(title)}</text>
<g font-family="Arial,sans-serif">{''.join(cells)}
<path d="M24 62H876M24 140H876M24 259H876" stroke="#94a3b8" stroke-width="2"/>
<path d="M308 62V259M592 62V259" stroke="#ef4444" stroke-width="2"/>
<path d="M42 190H858" stroke="#475569" stroke-width="3"/>
<path d="M858 190l-12 -6v12z" fill="#475569"/>{''.join(dots)}
<text x="24" y="285" fill="#1e3a5f" font-size="15">{escape(footer)}</text></g></svg>'''
    (OUT / name).write_text(svg, encoding='utf-8')


diagram('bva-20-50.svg', 'BVA 3 giá trị: miền hợp lệ 20–50',
        [('Dưới 20', 'không hợp lệ', 'invalid'), ('20–50', 'hợp lệ', 'valid'), ('Trên 50', 'không hợp lệ', 'invalid')],
        [(238, 19, 'sát ngoài', 'invalid'), (308, 20, 'biên dưới', 'valid'),
         (378, 21, 'sát trong', 'valid'), (522, 49, 'sát trong', 'valid'),
         (592, 50, 'biên trên', 'valid'), (662, 51, 'sát ngoài', 'invalid')],
        'Mỗi biên: sát ngoài → đúng biên → sát trong.')

diagram('bva-30-70.svg', 'BVA 2 giá trị: miền hợp lệ 30–70',
        [('Dưới 30', 'không hợp lệ', 'invalid'), ('30–70', 'hợp lệ', 'valid'), ('Trên 70', 'không hợp lệ', 'invalid')],
        [(238, 29, 'sát ngoài', 'invalid'), (308, 30, 'biên dưới', 'valid'),
         (592, 70, 'biên trên', 'valid'), (662, 71, 'sát ngoài', 'invalid')],
        'Bốn giá trị chọn: 29, 30, 70, 71.')

diagram('bva-5-30.svg', 'BVA 3 giá trị tại biên trên 30',
        [('Dưới 5', 'không hợp lệ', 'invalid'), ('5–30', 'hợp lệ', 'valid'), ('Trên 30', 'không hợp lệ', 'invalid')],
        [(522, 29, 'sát trong', 'valid'), (592, 30, 'biên trên', 'valid'),
         (662, 31, 'sát ngoài', 'invalid')],
        'Nhìn quanh vạch 30: 29 → 30 → 31.')

diagram('ep-30-70.svg', 'Phân vùng tương đương: miền 30–70',
        [('≤ 29', 'vùng thấp', 'invalid'), ('30–70', 'vùng hợp lệ', 'valid'), ('≥ 71', 'vùng cao', 'invalid')],
        [(220, 29, 'đại diện', 'invalid'), (450, 50, 'đại diện', 'valid'),
         (680, 71, 'đại diện', 'invalid')],
        'Một số đại diện trong mỗi vùng: 29, 50, 71.')

diagram('bva-120-450.svg', 'BVA 3 giá trị tại biên trên 450',
        [('Dưới 120', 'không hợp lệ', 'invalid'), ('120–450', 'hợp lệ', 'valid'), ('Trên 450', 'không hợp lệ', 'invalid')],
        [(522, 449, 'sát trong', 'valid'), (592, 450, 'biên trên', 'valid'),
         (662, 451, 'sát ngoài', 'invalid')],
        'Kiểm tra 449, 450, 451 để bắt lỗi lệch một đơn vị.')

diagram('bva-10-20.svg', 'BVA 3 giá trị: miền hợp lệ 10–20',
        [('Dưới 10', 'không hợp lệ', 'invalid'), ('10–20', 'hợp lệ', 'valid'), ('Trên 20', 'không hợp lệ', 'invalid')],
        [(238, 9, 'BVA 2 và 3', 'invalid'), (308, 10, 'BVA 2 và 3', 'valid'),
         (378, 11, 'thêm ở BVA 3', 'added'), (522, 19, 'thêm ở BVA 3', 'added'),
         (592, 20, 'BVA 2 và 3', 'valid'), (662, 21, 'BVA 2 và 3', 'invalid')],
        'Hai số BVA 3 thêm vào là 11 và 19.')

diagram('bva-10-30.svg', 'BVA 3 giá trị: miền hợp lệ 10–30',
        [('Dưới 10', 'không hợp lệ', 'invalid'), ('10–30', 'hợp lệ', 'valid'), ('Trên 30', 'không hợp lệ', 'invalid')],
        [(238, 9, 'ngoài biên', 'invalid'), (308, 10, 'biên dưới', 'valid'),
         (378, 11, 'sát biên', 'added'), (522, 29, 'sát biên', 'added'),
         (592, 30, 'biên trên', 'valid'), (662, 31, 'ngoài biên', 'invalid')],
        'Lấy ngay dưới, tại và ngay trên mỗi biên: 9–10–11; 29–30–31.')

diagram('ep-age-18-60.svg', 'Phân vùng tuổi hợp lệ 18–60',
        [('< 18 tuổi', 'không hợp lệ', 'invalid'), ('18–60 tuổi', 'hợp lệ', 'valid'), ('> 60 tuổi', 'không hợp lệ', 'invalid')],
        [(238, 17, 'vùng dưới', 'invalid'), (450, 35, 'vùng hợp lệ', 'valid'),
         (662, 61, 'vùng trên', 'invalid')],
        'Ba số đại diện: 17 (không hợp lệ), 35 (hợp lệ), 61 (không hợp lệ).')

diagram('bva-age-1-99.svg', 'Giá trị biên: tuổi hợp lệ 1–99',
        [('< 1 tuổi', 'không hợp lệ', 'invalid'), ('1–99 tuổi', 'hợp lệ', 'valid'), ('> 99 tuổi', 'không hợp lệ', 'invalid')],
        [(238, 0, 'ngay dưới 1', 'invalid'), (308, 1, 'biên dưới', 'valid'),
         (592, 99, 'biên trên', 'valid'), (662, 100, 'ngay trên 99', 'invalid')],
        'BVA 2 giá trị: 0–1 quanh biên dưới, 99–100 quanh biên trên.')

diagram('ep-integer-1-15.svg', 'Ba lớp tương đương cho số nguyên 1–15',
        [('< 1', 'không hợp lệ', 'invalid'), ('1–15', 'hợp lệ', 'valid'), ('> 15', 'không hợp lệ', 'invalid')],
        [(238, 0, 'lớp dưới', 'invalid'), (450, 8, 'lớp hợp lệ', 'valid'),
         (662, 16, 'lớp trên', 'invalid')],
        'Các lớp không chồng lấn; mỗi lớp chọn một số đại diện.')

diagram('ep-score-50.svg', 'Ba mức kết quả của bài thi 50 câu',
        [('0–29', 'chưa đạt', 'invalid'), ('30–44', 'đạt', 'valid'), ('45–50', 'xuất sắc', 'added')],
        [(220, 29, 'chưa đạt', 'invalid'), (308, 30, 'bắt đầu đạt', 'valid'),
         (522, 44, 'vẫn đạt', 'valid'), (592, 45, 'xuất sắc', 'added')],
        '44 thuộc vùng đạt; 45 mới bắt đầu vùng xuất sắc.')

diagram('temperature-18-21.svg', 'Bật dưới 18°C, tắt từ 21°C',
        [('< 18°C', 'bật sưởi', 'added'), ('18–20°C', 'tùy trạng thái trước', 'valid'), ('≥ 21°C', 'tắt sưởi', 'invalid')],
        [(238, 17, 'bật', 'added'), (308, 18, 'vùng giữa', 'valid'),
         (450, 19, 'phụ thuộc trước', 'valid'), (592, 21, 'tắt', 'invalid')],
        'Ở 19°C, cần biết sưởi đang bật hay tắt từ trước.')

diagram('ep-overlap-10-20.svg', 'Các vùng không được chồng lấn',
        [('≤ 9', 'vùng 1', 'invalid'), ('10–20', 'vùng 2', 'valid'), ('≥ 20', 'vùng 3', 'invalid')],
        [(238, 9, 'chỉ vùng 1', 'invalid'), (450, 15, 'chỉ vùng 2', 'valid'),
         (592, 20, 'trùng 2 vùng', 'invalid')],
        'Số 20 xuất hiện ở cả vùng 2 và vùng 3: phải sửa ranh giới.')
