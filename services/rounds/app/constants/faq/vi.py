# The FAQ in vi; the {placeholders} are filled in by helpers/help.py (faq_values) with
# billing's prices and the number of languages. Questions not translated yet show in English
# (constants/faq/__init__.py).
FAQ = [
    {
        "key": "what",
        "question": "prepza là gì?",
        "answer": "Một buổi phỏng vấn có tính giờ được tạo từ mô tả công việc của bạn, cho mọi vị trí. Dùng nó để sàng lọc ứng viên trước khi gặp họ, hoặc làm chính một bước tuyển dụng: dù cách nào, bạn cũng thấy ai thật sự thạo việc.",
    },
    {
        "key": "roles",
        "question": "Tôi có thể tuyển cho những vị trí nào?",
        "answer": "Mọi vị trí cần đến kiến thức: hỗ trợ khách hàng, bán hàng, tài chính, y tế, nghề kỹ thuật, kỹ sư, marketing và nhiều hơn nữa. Nếu bạn mô tả được công việc, prepza có thể tạo buổi phỏng vấn cho nó.",
    },
    {
        "key": "hiring",
        "question": "Cách hoạt động thế nào?",
        "answer": "Dán mô tả công việc trên trang chủ, đặt tên công ty và kiểm tra các chủ đề prepza đề xuất. Sau đó mời ứng viên: nhập email của họ, dán danh sách hoặc tải tệp lên. Ứng viên chưa bắt đầu sau vài ngày sẽ nhận một lời nhắc. Mỗi ứng viên có bộ câu hỏi riêng với thời gian giới hạn cho từng câu, và bạn thấy điểm cùng mọi câu trả lời của họ ngay khi họ làm xong.",
    },
    {
        "key": "link",
        "question": "Tôi có thể đặt buổi phỏng vấn vào tin tuyển dụng không?",
        "answer": "Có. Bật liên kết chia sẻ của buổi phỏng vấn trong thẻ ứng viên và dán vào tin tuyển dụng. Ai mở liên kết sẽ đăng nhập và tham gia phỏng vấn, và mỗi người được tính phí như một ứng viên được mời. Liên kết tự tắt khi bạn đánh dấu buổi phỏng vấn là đã tuyển.",
    },
    {
        "key": "preview",
        "question": "Tôi có thể thử buổi phỏng vấn trước khi mời ai không?",
        "answer": "Có. Mở buổi phỏng vấn của bạn với tư cách ứng viên từ trang của nó, miễn phí: các lần xem trước không xuất hiện trong danh sách ứng viên hay trong thống kê câu hỏi. Bạn cũng có thể làm bất kỳ buổi phỏng vấn luyện tập miễn phí nào.",
    },
    {
        "key": "cheating",
        "question": "Ứng viên có thể dùng AI hoặc tra cứu đáp án không?",
        "answer": "Mỗi ứng viên nhận bộ câu hỏi ngẫu nhiên riêng theo thứ tự riêng, với thời gian giới hạn cho từng câu do máy chủ của chúng tôi theo dõi, nên có rất ít thời gian để tra cứu đáp án hay hỏi AI. Bảng điểm cũng cho thấy khi ứng viên rời trang, sao chép văn bản hoặc trả lời quá nhanh để kịp đọc câu hỏi.",
    },
    {
        "key": "cost",
        "question": "Chi phí bao nhiêu?",
        "answer": "Tạo buổi phỏng vấn là miễn phí. Mỗi ứng viên trả lời ít nhất một câu hỏi tốn {candidate} credit ({candidate_dollars} $), và rẻ hơn với credit từ các lần nạp lớn hơn, xuống tới 1 $. Công ty đầu tiên của bạn nhận {company} credit miễn phí, đủ cho {company_candidates} ứng viên đầu tiên. Trang bảng giá liệt kê mọi mức giá.",
    },
    {
        "key": "charged",
        "question": "Khi nào tôi bị tính phí cho một ứng viên?",
        "answer": "Chỉ khi họ hoàn thành buổi phỏng vấn và đã trả lời ít nhất một câu hỏi. Credit dành cho họ được tạm giữ khi bạn mời và được hoàn lại nếu bạn thu hồi lời mời, nếu họ không bao giờ bắt đầu, hoặc nếu họ không trả lời câu nào.",
    },
    {
        "key": "compare_hiring",
        "question": "Giá so với các công cụ đánh giá khác thế nào?",
        "answer": "Nhiều công cụ đánh giá được bán theo gói đăng ký theo tháng hoặc năm, phải trả dù bạn không kiểm tra ai. Với prepza, bạn chỉ trả theo ứng viên: {candidate} credit ({candidate_dollars} $) mỗi ứng viên, không hợp đồng, không phí theo người dùng và không tốn phí tạo buổi phỏng vấn. Một công ty mời {example_candidates} ứng viên mỗi tháng trả khoảng {example_year_dollars} $ mỗi năm. Nếu bạn kiểm tra nhiều ứng viên mỗi tháng, gói đăng ký có thể rẻ hơn, nên hãy so sánh với số liệu của bạn.",
    },
    {
        "key": "expire",
        "question": "Credit có hết hạn không?",
        "answer": "Không. Credit không bao giờ hết hạn, và không có gói đăng ký trả phí. Nếu bạn bật tự động nạp (không bắt buộc), Paddle lưu thẻ của bạn dưới dạng một gói đăng ký 0 $; bạn chỉ trả cho những lần nạp thực tế.",
    },
    {
        "key": "refunds",
        "question": "Tôi có được hoàn tiền không?",
        "answer": "Có, với credit bạn mua trong 14 ngày gần nhất và chưa dùng: qua Paddle hoặc bằng cách viết cho chúng tôi. Credit miễn phí, như quà chào mừng, không được hoàn. Chi tiết có trong điều khoản.",
    },
    {
        "key": "scorecards",
        "question": "Bảng điểm cho thấy gì?",
        "answer": "Mọi câu trả lời, đúng hay sai và mất bao lâu. Điểm hiện màu xanh hoặc đỏ so với điểm đạt bạn đặt cho buổi phỏng vấn. Bảng điểm cũng đánh dấu các câu trả lời quá nhanh để kịp đọc câu hỏi, những lần ứng viên rời trang và các lần định sao chép.",
    },
    {
        "key": "reports",
        "question": "Tôi có thể chia sẻ kết quả với quản lý tuyển dụng không?",
        "answer": "Có. Tải xuống báo cáo PDF cho một ứng viên hoặc cho tất cả ứng viên của một buổi phỏng vấn, gửi qua email thẳng từ prepza, hoặc gửi bản tóm tắt ngắn qua WhatsApp, Telegram, Viber hay LINE.",
    },
    {
        "key": "integrations",
        "question": "prepza có hoạt động với ATS hoặc các công cụ khác của tôi không?",
        "answer": "Có, không mất thêm phí. Kết nối Workable, Greenhouse, Teamtailor, Recruitee hoặc Breezy HR trong tab Tích hợp của công ty bạn: ứng viên bạn chuyển sang một giai đoạn sẽ nhận buổi phỏng vấn, và kết quả được gửi lại ATS. Slack có thể đăng thông báo của công ty vào một kênh, còn API cho phép nền tảng của riêng bạn mời ứng viên và nhận kết quả của họ; xem Tài liệu API.",
    },
    {
        "key": "candidates",
        "question": "Ứng viên thấy gì?",
        "answer": "Tên và logo công ty của bạn, những gì cần biết trước khi bắt đầu, rồi lần lượt từng câu hỏi có giới hạn thời gian. Họ không bao giờ thấy điểm của mình hay câu trả lời có đúng không.",
    },
    {
        "key": "verified",
        "question": "Dấu xác minh có nghĩa là gì?",
        "answer": "Nghĩa là chủ sở hữu hoặc quản trị viên của công ty đã đăng nhập bằng email công việc trên website của công ty, như you@acme.com, và sau đó đội ngũ của chúng tôi đã xem xét công ty. Thêm website bằng nút Xác minh ở phần đầu trang công ty; dịch vụ email miễn phí không được tính. Trong khi chờ xem xét, nhóm của bạn thấy biểu tượng đồng hồ cạnh tên, và đổi tên công ty sẽ gửi công ty đi xem xét lại. Dấu xác minh hiện cạnh tên công ty của bạn, kể cả trong lời mời.",
    },
    {
        "key": "languages",
        "question": "Hỗ trợ những ngôn ngữ nào?",
        "answer": "{count} ngôn ngữ, cho trang web, các buổi phỏng vấn và email. Hãy chọn ngôn ngữ viết buổi phỏng vấn, bất kể mô tả công việc được viết bằng ngôn ngữ nào.",
    },
    {
        "key": "privacy",
        "question": "Mô tả công việc và câu trả lời được xử lý thế nào?",
        "answer": "Mô tả công việc được dùng để tạo các buổi phỏng vấn của bạn, và câu trả lời của ứng viên để chấm điểm, chỉ cho công ty của bạn. Chính sách quyền riêng tư giải thích chúng tôi lưu gì, trong bao lâu, và quyền của mọi người.",
    },
    {
        "key": "emails",
        "question": "prepza gửi những email nào, và làm sao để dừng nhận?",
        "answer": 'Email dịch vụ, như lời mời, báo cáo, vấn đề thanh toán và thay đổi điều khoản của chúng tôi, luôn được gửi. Những email còn lại, như tóm tắt hoạt động hằng ngày, lời nhắc và cập nhật sản phẩm, bạn chọn trong Cài đặt, mục Email, hoặc dừng bằng liên kết "Hủy đăng ký" trong mỗi email. Ứng viên có thể dừng nhận email từ công ty bạn, hoặc lời nhắc của một buổi phỏng vấn, bằng các liên kết trong lời mời và lời nhắc của họ.',
    },
    {
        "key": "delete",
        "question": "Tôi có thể xóa tài khoản không?",
        "answer": "Có, trong Cài đặt. Tài khoản và dữ liệu của bạn bị xóa, và trước đó bạn có thể tải xuống bản sao dữ liệu.",
    },
]
