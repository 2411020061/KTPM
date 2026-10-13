"""Build reviewed, slide-based follow-up questions.

Every entry below asks for one fact separate from the original question.  The
extracted slide paragraphs are useful for review, but are not safe to turn into
questions automatically: some slide matches are imperfect and generic prompts
do not test the missing fact.
"""

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'On_KTPM' / 'web'
knowledge = json.loads((ROOT / 'knowledge.json').read_text())
questions = {q['id']: q for name in ('questions.json', 'pdf-questions.json') for q in json.loads((ROOT / name).read_text())}
applied = json.loads((ROOT / 'applied-questions.json').read_text())
supplemental = json.loads((ROOT / 'supplemental-questions.json').read_text())
reviewed_slides = json.loads((ROOT / 'reviewed-slide-questions.json').read_text())
quiz_links = json.loads((ROOT / 'reviewed-quiz-links.json').read_text())
quiz_bank = {q['id']: q for q in json.loads((ROOT / 'questions.json').read_text())}

QUIZ_VISUALS = {
    't7-2-1': {
        'image': 'media/extra/bva-age-1-99.svg',
        'imageAlt': 'Tuổi hợp lệ 1 đến 99; kiểm tra 0, 1, 99 và 100 tại hai biên',
        'explain': 'Tuổi hợp lệ là 1–99. BVA hai giá trị lấy ngay ngoài và tại mỗi biên: 0–1, 99–100.',
    },
    't36-1-3': {
        'image': 'media/extra/ep-integer-1-15.svg',
        'imageAlt': 'Ba vùng số nguyên: nhỏ hơn 1, từ 1 đến 15, lớn hơn 15',
        'explain': 'Các vùng không chồng lấn và phủ toàn bộ miền: <1, 1–15, >15. Chọn một đại diện mỗi vùng.',
    },
}

STOP = set('cau nao sau day la cua de va trong cho voi mot nhung cac theo tren slide bai giang kiem thu phan mem duoc co the hay khong khi ve den tu'.split())

def words(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return set(re.findall(r'[a-z0-9]{3,}', s)) - STOP

def original_text(q):
    raw = q.get('raw', '')
    stem = re.split(r'\n\s*[A-D][.．)]\s*', raw, maxsplit=1)[0]
    answer = q.get('answer', '')
    match = re.search(r'(?m)^\s*' + re.escape(answer) + r'[.．)]\s*(.*?)(?=\n\s*[A-D][.．)]|\Z)', raw, re.S) if answer else None
    return stem + ' ' + (match.group(1) if match else '')

def clean(s):
    return re.sub(r'\s+', ' ', re.sub(r'^[▸•\-\s]+', '', s)).strip(' .;:')

def key(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return ' '.join(re.findall(r'[a-z0-9]+', s))

def question_stem(raw):
    return re.sub(r'^Câu\s*\d+\s*:\s*', '', re.split(r'\n\s*[A-D][.．)]\s*', raw, maxsplit=1)[0], flags=re.I)

def correct_option_text(q):
    match = re.search(r'(?m)^\s*' + re.escape(q['answer']) + r'[.．)]\s*(.*?)(?=^\s*[A-E][.．)]\s*|\Z)', q['raw'], re.S)
    if not match:
        raise ValueError(f'Quiz question has no marked answer text: {q["id"]}')
    return clean(match.group(1))

OVERRIDES = {
    'pdf-C1-9': ('Tư duy người kiểm thử cần chú ý đến loại luồng nào ngoài luồng thành công?', 'Luồng ngoại lệ (negative path) và các tình huống có thể xảy ra ngoài dự kiến.'),
    'pdf-C1-17': ('Một thất bại có thể xảy ra mà không do khiếm khuyết phần mềm trong trường hợp nào?', 'Khi điều kiện môi trường như phần cứng, nhiễu điện từ hoặc cấu hình sai gây ra hành vi sai.'),
    'pdf-C3-2': ('Kiểm thử tự động hỗ trợ CI/CD phát hiện lỗi sớm bằng cách nào?', 'Sau mỗi lần đẩy mã nguồn, hệ thống tự động chạy test để phát hiện lỗi trước khi triển khai.'),
    'pdf-C3-5': ('Vì sao một script kiểm thử tự động có thể tiết kiệm công sức qua nhiều phiên bản?', 'Script viết một lần có thể tái sử dụng để kiểm thử nhiều phiên bản phần mềm.'),
    'pdf-C2-4': ('Trong mô hình chữ V, việc thiết kế test diễn ra song song với hoạt động nào?', 'Song song với các giai đoạn phát triển ở nhánh trái của mô hình.'),
    'pdf-C2-9': ('Trong mô hình chữ V, thiết kế test sớm đem lại lợi ích gì so với Waterfall?', 'Giúp phát hiện lỗi sớm hơn vì mỗi giai đoạn phát triển có cấp độ kiểm thử tương ứng.'),
    'main-24-0': ('Khi xem xét test case bằng kiểm thử tĩnh, có thể phát hiện thiếu những nội dung nào?', 'Thiếu liên kết truy vết tới yêu cầu, thiếu kết quả mong đợi, dữ liệu không đủ hoặc bước thực hiện không rõ.'),
    'main-20-0': ('Vì sao nên ưu tiên bộ định vị Id khi tìm phần tử?', 'Id thường nhanh và ổn định hơn các bộ định vị khác.'),
    'pdf-C1-1': ('Việc xem xét tài liệu yêu cầu và thiết kế từ sớm giúp ngăn ngừa điều gì?', 'Ngăn ngừa khiếm khuyết phát sinh trong mã nguồn.'),
    'pdf-C1-2': ('Sau khi lập trình viên sửa lỗi, hoạt động nào xác nhận lỗi đã được sửa đúng?', 'Kiểm thử xác nhận (confirmation testing): chạy lại kiểm thử để xác nhận lỗi đã được sửa đúng.'),
    'pdf-C2-1': ('Trong giai đoạn bảo trì, hai loại kiểm thử nào cần thực hiện sau mỗi thay đổi?', 'Kiểm thử xác nhận (confirmation) và kiểm thử hồi quy (regression).'),
    'pdf-C3-1': ('Test Summary Report bàn giao thông tin gì và được lập khi nào?', 'Tổng hợp kết quả, đánh giá chất lượng, rủi ro tồn đọng và khuyến nghị; lập khi kết thúc mỗi đợt kiểm thử.'),
    'main-10-0': ('Mức độ ưu tiên (Priority) của lỗi phụ thuộc vào những yếu tố nào?', 'Tần suất người dùng gặp lỗi, ảnh hưởng đến doanh thu và hình ảnh thương hiệu.'),
    'main-15-0': ('So với kiểm thử thủ công, kiểm thử tự động khác gì về tốc độ và cách thực hiện?', 'Máy chạy script đã lập trình sẵn, nhanh hơn đáng kể so với thao tác thủ công của tester.'),
    'main-30-0': ('Phân tích giá trị biên áp dụng cho dữ liệu nào và không phù hợp với dữ liệu nào?', 'Áp dụng cho các vùng có thứ tự như số, ngày tháng, độ dài chuỗi; không áp dụng cho dữ liệu rời rạc như màu sắc.'),
    'pdf-C2-7': ('Trong mô hình chữ V, test được thiết kế vào thời điểm nào?', 'Song song với hoạt động phát triển để phát hiện lỗi sớm.'),
    'pdf-C2-10': ('Mỗi giai đoạn phát triển cần đi kèm hoạt động nào?', 'Một hoạt động kiểm chứng tương ứng.'),
    'pdf-C2-13': ('Kiểm thử hệ thống dựa trên cơ sở nào và thường do ai thực hiện?', 'Dựa trên đặc tả yêu cầu chức năng và phi chức năng; thường do tester độc lập thực hiện.'),
    'pdf-C3-10': ('Khi số ca kiểm thử tăng lên, chi phí trên mỗi lần chạy tự động thay đổi thế nào?', 'Giảm mạnh, giúp đạt ROI dương sau một số vòng chạy dù chi phí đầu tư ban đầu cao.'),
    'pdf-C3-11': ('Ngoài phương thức HTTP, kiểm thử API còn xác minh những thuộc tính nào?', 'Tính chính xác, hiệu năng và độ tin cậy của giao diện trao đổi dữ liệu giữa các hệ thống.'),
    'pdf-C3-14': ('Kiểm thử API xác minh những thuộc tính nào của giao diện trao đổi dữ liệu?', 'Tính chính xác, hiệu năng và độ tin cậy.'),
    'pdf-C3-15': ('Công cụ kiểm thử kéo–thả hoặc dựa trên từ khóa giúp giảm yêu cầu về kỹ năng nào?', 'Kỹ năng lập trình khi xây dựng kịch bản kiểm thử.'),
    'pdf-C3-20': ('Appium hỗ trợ những loại ứng dụng di động nào?', 'Native app, hybrid app và mobile web.'),
    'pdf-C4-7': ('Vì sao bảng quyết định đầy đủ 16 quy tắc trong ví dụ được rút gọn còn 5?', 'Hệ thống kiểm tra lần lượt C1 đến C4 và chỉ trả về nguyên nhân không hợp lệ đầu tiên.'),
    'pdf-C4-14': ('Khi một vùng tương đương chứa các cách xử lý khác nhau, cần làm gì?', 'Chia lại vùng đó vì phân vùng hiện tại chưa đúng.'),
    'pdf-C4-15': ('Khi nào nên dùng kiểm thử chuyển trạng thái?', 'Khi hành vi hệ thống phụ thuộc vào trạng thái hiện tại và lịch sử các sự kiện đã xảy ra.'),
    'pdf-C4-18': ('Hai yếu tố nào quyết định hành vi của hệ thống trong kiểm thử chuyển trạng thái?', 'Trạng thái hiện tại và lịch sử các sự kiện đã xảy ra.'),
    'pdf-C4-20': ('Sau khi hủy đăng ký học phần thành công, hệ thống cần cập nhật gì?', 'Xóa đăng ký, cập nhật sĩ số và chuyển sang trạng thái Đã hủy.'),
    'main-4-1': ('Kiểm thử hệ thống thường do ai thực hiện?', 'Tester độc lập.'),
    'main-4-2': ('Kiểm thử chấp nhận đặt hệ thống trong ngữ cảnh nào?', 'Ngữ cảnh nghiệp vụ thực tế của khách hàng hoặc người dùng.'),
    'main-9-0': ('Trong ví dụ RTM, yêu cầu khóa tài khoản sau 5 lần sai được truy vết tới các test case nào?', 'TC_LOGIN_005 và TC_LOGIN_006.'),
    'main-11-3': ('Ở hình thức inspection, việc chuẩn bị cá nhân có bắt buộc không?', 'Có, đây là bước bắt buộc.'),
    'main-14-1': ('Khi hủy đăng ký học phần còn trong thời hạn hủy, trạng thái tiếp theo là gì?', 'Đã hủy.'),
    'main-14-3': ('Statement coverage đo tỷ lệ của đối tượng nào?', 'Các câu lệnh có thể thực thi đã được tập test case chạy qua.'),
    'main-15-1': ('Khi kiểm tra nhiều chi tiết độc lập trên cùng trang, nên dùng Assert hay Verify?', 'Verify, vì nó ghi nhận lỗi nhưng vẫn tiếp tục chạy các bước kiểm tra khác.'),
    'main-19-2': ('Node trong Selenium Grid trực tiếp làm việc gì sau khi nhận lệnh từ Hub?', 'Khởi động trình duyệt và thực thi các bước kiểm thử trên môi trường của Node.'),
    'main-20-2': ('Thuộc tính nào của WebElement dùng để đọc nội dung văn bản?', 'element.Text.'),
    'main-20-3': ('Muốn xóa nội dung sẵn có trong ô nhập trước khi gõ mới, gọi phương thức nào?', 'element.Clear().'),
    'main-21-0': ('Sau một bài kiểm thử Selenium, vì sao nên gọi driver.Quit()?', 'Để đóng toàn bộ trình duyệt và giải phóng tiến trình driver, tránh treo tài nguyên.'),
    'main-21-1': ('Explicit Wait khác Implicit Wait ở điểm nào?', 'Explicit Wait đợi một điều kiện cụ thể; Implicit Wait đặt thời gian chờ tối đa chung khi tìm phần tử.'),
    'main-21-2': ('Muốn chờ phần tử result sẵn sàng để đọc, Explicit Wait cần kiểm tra điều kiện gì?', 'Đợi phần tử có id result xuất hiện và hiển thị (Displayed).'),
    'main-22-0': ('Trong ví dụ kiểm thử đăng nhập, script lấy thông báo kết quả bằng cách nào?', 'Đọc thuộc tính Text của phần tử có id flash.'),
    'main-25-2': ('Kiểm thử đơn vị chủ yếu kiểm tra những đối tượng nào?', 'Hàm, phương thức, lớp hoặc module nhỏ nhất.'),
    'main-26-3': ('Trong Test Plan, mục phạm vi cần chỉ rõ hai nhóm chức năng nào?', 'Chức năng nằm trong phạm vi kiểm thử (in scope) và ngoài phạm vi (out of scope).'),
    'main-28-0': ('Explicit Wait trong ví dụ đợi điều kiện gì trước khi tiếp tục?', 'Đợi phần tử có id result xuất hiện và hiển thị, tối đa 10 giây.'),
    'main-28-1': ('Với dropdown HTML, muốn chọn mục Vinh Long bằng Selenium C# thì dùng lệnh nào?', 'Tạo SelectElement rồi gọi SelectByText("Vinh Long").'),
    'main-29-0': ('Trong ví dụ bảng quyết định, hệ thống kiểm tra các điều kiện theo thứ tự nào?', 'C1 → C2 → C3 → C4 và chỉ báo nguyên nhân không hợp lệ đầu tiên.'),
    'main-29-1': ('Vì sao 16 tổ hợp điều kiện được rút gọn còn 5 quy tắc?', 'Vì hệ thống kiểm tra C1 → C4 theo thứ tự và dừng ở nguyên nhân không hợp lệ đầu tiên.'),
    'main-29-2': ('Ở biên trên 25, bộ ba giá trị nào giúp phát hiện lỗi lệch một đơn vị?', '24, 25 và 26.'),
    'main-29-3': ('Ngoài các miền số hợp lệ và không hợp lệ, ô nhập tín chỉ cần thử loại dữ liệu nào?', 'Ô trống, chữ cái, số thập phân, số âm và ký tự đặc biệt.'),
    'main-30-2': ('Khi nào kỹ thuật kiểm thử chuyển trạng thái đặc biệt phù hợp?', 'Khi hành vi phụ thuộc cả trạng thái hiện tại lẫn lịch sử sự kiện đã xảy ra.'),
    'main-30-3': ('Nếu hủy đăng ký khi còn trong thời hạn cho phép, hệ thống phải làm gì?', 'Xóa đăng ký, cập nhật sĩ số và chuyển trạng thái sang Đã hủy.'),
    'main-31-0': ('Trong ví dụ kiểm tra số tín chỉ, hai quyết định D1 và D2 tạo tổng cộng bao nhiêu nhánh?', 'Bốn nhánh: đúng và sai cho mỗi quyết định.'),
    'main-31-2': ('Statement coverage đo điều gì?', 'Tỷ lệ các câu lệnh có thể thực thi đã được tập test case chạy qua.'),
    'main-31-3': ('Hai quyết định D1 và D2 trong ví dụ kiểm tra những giới hạn tín chỉ nào?', 'D1 kiểm tra credits < 1; D2 kiểm tra credits > 25.'),
    'main-32-1': ('Công thức tính bao phủ nhánh (Branch Coverage) là gì?', 'BC = (Số nhánh đã thực thi / Tổng số nhánh) × 100%.'),
    'pdf-C2-18': ('Trong DevOps/CI-CD, kiểm thử được chạy vào thời điểm nào?', 'Tự động và liên tục sau mỗi commit.'),
    'pdf-C2-20': ('Theo nguyên tắc shift-left, có thể bắt đầu thiết kế kiểm thử khi nào?', 'Ngay khi cơ sở kiểm thử như yêu cầu hoặc thiết kế sẵn sàng.'),
    'pdf-C3-3': ('Khi nào kiểm thử thủ công có thể phù hợp hơn việc viết script?', 'Khi công sức xây dựng script lớn hơn lợi ích thu được; thao tác thủ công nhanh và linh hoạt hơn.'),
    'pdf-C3-19': ('Công cụ quản lý kiểm thử hỗ trợ ba công việc chính nào?', 'Quản lý test case, thực thi và tạo báo cáo.'),
    'pdf-C4-5': ('Để đạt bao phủ nhánh cho một quyết định, cần thử những kết quả nào?', 'Cả kết quả đúng (True) và sai (False).'),
    'main-2-0': ('Trong Agile/DevOps, ranh giới giữa tester và developer thay đổi thế nào?', 'Tester có thể tham gia gỡ lỗi; developer cũng viết và chạy unit test.'),
    'main-2-3': ('Test Manager/QA Manager chịu trách nhiệm gì ngoài lập kế hoạch?', 'Phân bổ nguồn lực, theo dõi tiến độ và báo cáo cho các bên liên quan.'),
    'main-3-1': ('Vì sao người không trực tiếp viết sản phẩm có thể kiểm thử khách quan hơn?', 'Họ hiểu ngữ cảnh nhưng ít bị thiên kiến xác nhận hơn người tạo ra sản phẩm.'),
    'main-3-2': ('Các sản phẩm bàn giao kiểm thử hỗ trợ việc bảo trì về sau như thế nào?', 'Chúng tạo tính minh bạch và khả năng truy vết.'),
    'main-4-3': ('Kiểm thử tích hợp tập trung vào các giao tiếp nào?', 'Giao tiếp giữa các module, giữa các hệ thống và qua API.'),
    'main-6-3': ('Những yếu tố nào khiến phân tích tác động trong bảo trì trở nên khó khăn?', 'Đặc tả lỗi thời hoặc thiếu, không có ma trận truy vết, người viết hệ thống đã nghỉ việc và tài liệu không được cập nhật.'),
    'main-7-0': ('Trong CI, điều gì xảy ra nếu unit test hoặc phân tích tĩnh thất bại?', 'Quy trình bị chặn ngay sau bước build và kiểm tra tự động.'),
    'main-8-3': ('Test strategy xác định những nội dung nào?', 'Nguyên tắc, cách tiếp cận, chuẩn áp dụng và mức tự động hóa.'),
    'main-10-2': ('Vì sao cần lưu sản phẩm bàn giao kiểm thử?', 'Để bảo đảm minh bạch, truy vết và hỗ trợ bảo trì, nâng cấp.'),
    'main-11-0': ('Sản phẩm bàn giao kiểm thử giúp ích gì sau khi kết thúc đợt test?', 'Hỗ trợ truy vết, bảo trì và nâng cấp hệ thống về sau.'),
    'main-11-2': ('Mục tiêu nổi bật của informal review là gì?', 'Nhận phản hồi nhanh.'),
    'main-12-0': ('Người điều phối trong buổi review chịu trách nhiệm gì?', 'Tổ chức hoạt động, giữ đúng mục tiêu, kiểm soát thời gian và trao đổi khách quan.'),
    'main-12-2': ('BVA bổ sung cho phân vùng tương đương bằng cách tập trung vào đâu?', 'Những điểm có rủi ro cao tại ranh giới của các vùng.'),
    'main-12-3': ('Phân vùng tương đương và BVA bổ sung cho nhau thế nào?', 'Phân vùng tương đương xác định các miền; BVA kiểm tra các ranh giới có rủi ro cao.'),
    'main-14-2': ('Một quyết định cần được chạy qua những kết quả nào để đạt bao phủ nhánh?', 'Cả nhánh đúng (True) và nhánh sai (False).'),
    'main-16-2': ('Sau khi script chạy trên nhiều môi trường, kết quả được lưu kèm bằng chứng gì?', 'Trạng thái Pass/Fail, log và ảnh chụp màn hình.'),
    'main-17-0': ('Trong Selenium, lệnh nào chọn tùy chọn Vinh Long của dropdown?', 'Tạo SelectElement cho dropdown rồi gọi SelectByText("Vinh Long").'),
    'main-17-3': ('Nếu kiểm thử tuần tự ba trình duyệt, mỗi trình duyệt 10 phút, tổng thời gian là bao lâu?', '30 phút.'),
    'main-18-0': ('Khi phân tích kết quả chạy tự động, cần xem những bằng chứng nào?', 'Trạng thái Pass/Fail, log và ảnh chụp màn hình.'),
    'main-19-1': ('Dù Selenium Grid có nhiều Node, tester gửi yêu cầu kiểm thử đến đâu?', 'Đến một điểm điều phối duy nhất là Hub.'),
    'main-23-3': ('Tài liệu kiểm thử giúp truy vết và bảo trì về sau nhờ điều gì?', 'Tính minh bạch và khả năng truy vết của các sản phẩm bàn giao.'),
    'main-24-0': ('Phân tích tĩnh mã nguồn có thể phát hiện những vấn đề nào?', 'Biến chưa khởi tạo, mã không thể tiếp cận, mã trùng lặp, độ phức tạp cao và vi phạm quy tắc viết mã.'),
    'main-24-1': ('Hình thức informal review phù hợp với sản phẩm có mức rủi ro nào?', 'Sản phẩm nhỏ, rủi ro thấp.'),
    'main-24-3': ('Trong CI, bước kiểm tra nào có thể chặn quy trình ngay khi thất bại?', 'Unit test hoặc phân tích tĩnh sau khi server tự build.'),
    'main-26-1': ('Giám sát và kiểm soát kiểm thử diễn ra khi nào?', 'Song song, xuyên suốt các hoạt động kiểm thử khác.'),
    'main-27-3': ('Vì sao 100% bao phủ nhánh vẫn chưa chứng minh phần mềm không còn lỗi?', 'Bao phủ chỉ cho biết các nhánh đã được chạy, không chứng minh chương trình không còn khiếm khuyết.'),
    'main-31-1': ('Bao phủ nhánh và bao phủ câu lệnh có chứng minh chương trình hết lỗi không?', 'Không; cả hai đều không chứng minh chương trình không còn khiếm khuyết.'),
    'main-32-0': ('Hai độ đo bao phủ câu lệnh và nhánh có giới hạn chung nào?', 'Không độ đo nào chứng minh chương trình không còn khiếm khuyết.'),
}

# Questions from the supplementary Word file already appear in questions.json.
# These additions come from other facts visible on the associated slides.
OVERRIDES.update({
    'pdf-C1-3': ('Một khiếm khuyết trong mã nguồn có luôn gây ra thất bại khi chạy chương trình không?', 'Không. Khiếm khuyết có thể nằm ở đoạn mã không bao giờ được thực thi.'),
    'pdf-C1-4': ('Tài liệu yêu cầu mơ hồ là ví dụ của yếu tố nào dẫn đến sai sót?', 'Nguyên nhân gốc (root cause).'),
    'pdf-C1-5': ('Khi chạy mãi một bộ test mà không tìm ra lỗi mới, nên làm gì?', 'Rà soát và bổ sung test case để phát hiện lỗi mới.'),
    'pdf-C1-7': ('Khi lỗi được sửa hoặc yêu cầu đổi, quy trình kiểm thử có thể quay lại những bước nào?', 'Quay lại phân tích, thiết kế hoặc thực thi kiểm thử.'),
    'pdf-C1-8': ('Bước lập kế hoạch kiểm thử cần xác định những tiêu chí nào để biết lúc nào dừng?', 'Tiêu chí kết thúc kiểm thử (exit criteria).'),
    'pdf-C1-10': ('Ngoài thiệt hại tài chính, lỗi phần mềm có thể gây ra hậu quả nghiêm trọng nào?', 'Mất dữ liệu, tổn hại uy tín và thậm chí nguy hiểm tính mạng.'),
    'pdf-C1-11': ('Một thất bại có thể xảy ra mà không bắt nguồn từ khiếm khuyết phần mềm khi nào?', 'Khi môi trường có lỗi phần cứng, nhiễu điện từ hoặc cấu hình sai.'),
    'pdf-C1-13': ('Theo mô hình Boehm, chi phí sửa lỗi ở giai đoạn vận hành so với giai đoạn yêu cầu xấp xỉ bao nhiêu lần?', 'Khoảng 100 lần.'),
    'pdf-C1-15': ('Thuộc tính chất lượng nào liên quan đến thời gian phản hồi và thông lượng?', 'Hiệu năng (performance efficiency).'),
    'pdf-C1-18': ('Rà soát tài liệu yêu cầu mà không chạy chương trình thuộc loại kiểm thử nào?', 'Kiểm thử tĩnh.'),
    'pdf-C1-19': ('Kiểm thử chấp nhận tập trung vào mục tiêu nào trong các mục tiêu kiểm thử?', 'Xây dựng niềm tin rằng sản phẩm đáp ứng nhu cầu và kỳ vọng sử dụng.'),
    'pdf-C1-20': ('Trong một test case, kết quả mong đợi cần được xác định vào lúc nào?', 'Trước khi chạy kiểm thử.'),
    'pdf-C2-3': ('Trong mô hình chữ V, kiểm thử đơn vị tương ứng với giai đoạn phát triển nào?', 'Thiết kế chi tiết và lập trình.'),
    'pdf-C2-6': ('Ngoài thứ tự thực hiện, các cấp độ kiểm thử còn được phân biệt theo những tiêu chí nào?', 'Đối tượng, mục tiêu, cơ sở kiểm thử và người thực hiện.'),
    'pdf-C2-11': ('Cơ sở để thiết kế kiểm thử đơn vị là gì?', 'Thiết kế chi tiết và mã nguồn.'),
    'pdf-C2-12': ('Ai thường thực hiện kiểm thử đơn vị?', 'Lập trình viên.'),
    'pdf-C2-14': ('Kiểm thử chấp nhận lấy cơ sở từ tài liệu và thông tin nào?', 'Yêu cầu nghiệp vụ, quy trình và hợp đồng.'),
    'main-18-2': ('Kiểm thử khả năng sử dụng có thể đánh giá những đặc điểm nào?', 'Số thao tác để hoàn thành tác vụ, độ rõ của thông báo lỗi và hỗ trợ người khuyết tật.'),
    'main-18-3': ('Selenium hỗ trợ viết kịch bản kiểm thử bằng những ngôn ngữ nào?', 'C#, Java, Python, Ruby, JavaScript và PHP.'),
    'main-19-0': ('Selenium IDE lưu kịch bản bằng cách nào khi người dùng thao tác trên trình duyệt?', 'Ghi lại thao tác nhấp chuột, nhập văn bản và chuyển trang để phát lại.'),
    'main-23-0': ('Kiểm thử bảo mật cần kiểm tra hai kiểu tấn công chèn dữ liệu phổ biến nào?', 'SQL injection và XSS.'),
    'main-23-1': ('Sau bước build và unit test trong CI, bước kiểm thử tự động nào thường được chạy?', 'Kiểm thử tích hợp và API.'),
    'main-23-2': ('Cách tiếp cận kiểm thử dựa trên kinh nghiệm thường dùng kỹ thuật nào?', 'Đoán lỗi và kiểm thử thăm dò.'),
    'main-25-3': ('Sau khi lập trình viên báo đã sửa lỗi, nên chạy lại test case nào để kiểm tra sửa lỗi?', 'Chính test case đã phát hiện lỗi, với cùng dữ liệu và môi trường.'),
    'main-26-0': ('Ai cùng chịu trách nhiệm về chất lượng theo cách tiếp cận whole-team trong Scrum?', 'Developer, tester và Product Owner.'),
    'main-26-2': ('Công thức tính tỷ lệ đạt (Pass Rate) là gì?', 'Số test case Pass chia số test case đã chạy, nhân 100%.'),
    'main-27-0': ('Loại kiểm thử nào có thể bắt đầu ngay khi mới có bản nháp tài liệu?', 'Kiểm thử tĩnh.'),
    'main-27-1': ('Trong ví dụ phân tích mã, việc hard-code chuỗi “Locked” và số 25 được gọi là gì?', 'Magic string và magic number.'),
    'main-27-2': ('Khi thiết kế test từ use case, tối thiểu cần bao nhiêu ca kiểm thử cho mỗi luồng thay thế hoặc ngoại lệ?', 'Ít nhất một test case cho mỗi luồng.'),
    'main-28-3': ('Trong bảng quyết định, ký hiệu “–” ở một điều kiện có nghĩa gì?', 'Giá trị điều kiện đó không ảnh hưởng đến hành động của quy tắc.'),
})

result = {}
bank_questions = {key(question_stem(q['raw'])) for q in questions.values()}
visible_questions = {key(question_stem(questions[id]['raw'])) for id in knowledge}
used_questions = set()
used_answers = set()
for id, k in knowledge.items():
    if id in applied:
        items = applied[id] if isinstance(applied[id], list) else [applied[id]]
        candidates = [(item['q'], item['a'], item, True) for item in items]
    elif id in supplemental:
        item = supplemental[id]
        candidates = [(item['q'], item['a'], item, False)]
    else:
        candidates = [(*OVERRIDES[id], {}, False)] if id in OVERRIDES else []
    result[id] = []
    for question, answer, item, is_applied in candidates:
        qkey, akey = key(question), key(answer)
        if qkey in bank_questions or qkey in used_questions or akey in used_answers:
            if id in supplemental or id in applied:
                raise ValueError(f'Duplicate follow-up for {id}: {question}')
            continue
        if is_applied:
            result[id].append({
                **item,
                'tag': 'Bài áp dụng',
                'badge': 'Đổi dữ kiện',
                'badgeClass': 'quiz',
                'source': f"Kiến thức slide tr. {questions[id]['page']}",
            })
        else:
            related = item.get('related')
            qref = questions[id]
            if related:
                label = f'Slide liên quan {related}'
            elif qref.get('matchType') == 'Khớp chủ đề câu hỏi':
                label = f"Slide liên quan {qref['file'].split('_')[1]} · tr. {qref['page']}"
            else:
                label = f"Slide tr. {qref['page']}"
            result[id].append({'q': question, 'a': answer, 'tag': 'Cùng slide', 'badge': label, 'badgeClass': 'yes', 'source': label, **{k: item[k] for k in ('relatedFile', 'relatedPage') if k in item}})
        used_questions.add(qkey)
        used_answers.add(akey)

    q = questions[id]
    related = supplemental.get(id, {})
    slide_file = q.get('file') or related.get('relatedFile')
    slide_page = q.get('page') or related.get('relatedPage')
    if slide_file and slide_page:
        page_key = f"{slide_file.split('_')[1]}:{slide_page}"
        if page_key not in reviewed_slides:
            raise ValueError(f'Unreviewed slide {page_key} for {id}')
        original = original_text(q)
        existing_questions = [x['q'] for x in result[id]]
        existing_answers = {key(x['a']) for x in result[id]}
        existing_concepts = {x['concept'] for x in result[id] if x.get('concept')}
        for quiz_id in quiz_links.get(page_key, []):
            source = quiz_bank[quiz_id]
            if not source.get('answerVerified') or source.get('kind') != 'supplemental':
                raise ValueError(f'Quiz source lacks verified answer: {quiz_id}')
            if source.get('file') != slide_file or source.get('page') != slide_page:
                raise ValueError(f'Quiz source maps to a different slide: {quiz_id}')
            quiz_question = clean(question_stem(source['raw']))
            quiz_answer = correct_option_text(source)
            qkey, akey = key(quiz_question), key(quiz_answer)
            if qkey in visible_questions or qkey in {key(x) for x in existing_questions} or akey in existing_answers:
                continue
            if len(akey) > 15 and akey in key(original):
                continue
            if any(len(words(quiz_question) & words(x)) / max(1, len(words(quiz_question) | words(x))) > .55 for x in [original, *existing_questions]):
                continue
            result[id].append({
                'q': quiz_question, 'a': quiz_answer, 'tag': 'Từ QUIZ',
                'badge': f"QUIZ · câu {source['number']}", 'badgeClass': 'quiz',
                'source': f"QUIZ C1–C6 · câu {source['number']}",
                **QUIZ_VISUALS.get(quiz_id, {}),
            })
            existing_questions.append(quiz_question)
            existing_answers.add(akey)
        for item in reviewed_slides[page_key]:
            if id in item.get('skipFor', []):
                continue
            qkey, akey = key(item['q']), key(item['a'])
            if qkey in bank_questions or any(qkey == key(x) for x in existing_questions):
                continue
            if akey in existing_answers:
                continue
            if item.get('concept') in existing_concepts:
                continue
            # Omit another wording of the fact answered by the original item.
            if len(akey) > 15 and akey in key(original):
                continue
            if any(len(words(item['q']) & words(x)) / max(1, len(words(item['q']) | words(x))) > .55 for x in [original, *existing_questions]):
                continue
            related_slide = not q.get('page') or q.get('matchType') == 'Khớp chủ đề câu hỏi'
            label = f"Slide liên quan {slide_file.split('_')[1]} · tr. {slide_page}" if related_slide else f"Slide tr. {slide_page}"
            result[id].append({**{k: v for k, v in item.items() if k != 'skipFor'}, 'tag': 'Cùng slide', 'badge': label, 'badgeClass': 'yes', 'source': label,
                               **({'relatedFile': slide_file, 'relatedPage': slide_page} if not q.get('page') else {})})
            existing_questions.append(item['q'])
            existing_answers.add(akey)
            if item.get('concept'):
                existing_concepts.add(item['concept'])

missing = [id for id, entries in result.items() if not entries]
if missing:
    raise ValueError(f'{len(missing)} questions lack a follow-up: {missing}')
for id, entries in result.items():
    seen = set()
    for item in entries:
        if not item.get('q') or not item.get('a'):
            raise ValueError(f'Missing exam question or single answer in {id}')
        qkey = key(item['q'])
        if qkey in seen:
            raise ValueError(f'Repeated question in {id}: {item["q"]}')
        seen.add(qkey)
        if item.get('image') and not (ROOT / item['image']).is_file():
            raise ValueError(f'Missing diagram in {id}: {item["image"]}')
        table = item.get('table')
        if table and (not table.get('headers') or not all(len(row) == len(table['headers']) for row in table.get('rows', []))):
            raise ValueError(f'Incomplete table in {id}: {item["q"]}')
if not any(item.get('table') for item in result['pdf-C4-19']):
    raise ValueError('PDF C4 question 19 needs a new decision table')
if not {'execution', 'dre', 'requirements', 'density'} <= {x.get('concept') for x in result['main-10-1']}:
    raise ValueError('Question 42 needs formulas other than Pass Rate')

(ROOT / 'extra-questions.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print('Generated', sum(bool(v) for v in result.values()), 'questions for', len(result), 'original questions')
