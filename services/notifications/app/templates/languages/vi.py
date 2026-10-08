# Email texts in Vietnamese. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "candidate": {
        "subject": "{company} mời bạn tham gia phỏng vấn",
        "preheader": "Tham gia phỏng vấn “{title}” trên prepza. Đăng nhập bằng {email} để bắt đầu.",
        "heading": "Lời mời phỏng vấn",
        "lines": [
            "{company} mời bạn tham gia buổi phỏng vấn “{title}” trên prepza.",
            (
                "Đăng nhập bằng {email} để bắt đầu. Chỉ địa chỉ này mới có thể tham "
                "gia phỏng vấn và bạn chỉ có một lần làm bài."
            ),
        ],
        "button": "Mở lời mời",
    },
    "reminder": {
        "subject": "Nhắc nhở: {company} đang chờ bạn làm bài phỏng vấn",
        "preheader": "“{title}” vẫn đang mở. Đăng nhập bằng {email} để bắt đầu.",
        "heading": "Buổi phỏng vấn đang chờ bạn",
        "lines": [
            (
                "{company} đã mời bạn tham gia buổi phỏng vấn “{title}” trên prepza vài ngày "
                "trước, và bạn vẫn chưa bắt đầu."
            ),
            (
                "Đăng nhập bằng {email} để bắt đầu. Chỉ địa chỉ này mới có thể tham gia phỏng "
                "vấn và bạn chỉ có một lần làm bài. Lời mời hết hạn sau 30 ngày kể từ khi gửi."
            ),
        ],
        "button": "Mở lời mời",
    },
    "report": {
        "subject": "Báo cáo ứng viên: {candidate}",
        "preheader": "{candidate} đã tham gia phỏng vấn “{title}” tại {company}. Báo cáo được đính kèm.",
        "heading": "Báo cáo ứng viên",
        "lines": [
            (
                "{sender} từ {company} đã chia sẻ báo cáo của {candidate} cho buổi phỏng vấn "
                "“{title}”."
            ),
            (
                "Báo cáo được đính kèm dưới dạng PDF một trang: điểm tổng, điểm từng chủ đề và "
                "những gì trình duyệt của ứng viên ghi nhận. Trả lời email này để phản hồi {sender}."
            ),
        ],
        "button": "Truy cập prepza",
        "footer": "Email này được gửi đến {email} vì {sender} đã chia sẻ một báo cáo ứng viên "
        "với địa chỉ này trên prepza. Nếu bạn không mong đợi email này, bạn có thể bỏ qua.",
    },
    "candidates": {
        "subject": "Báo cáo tất cả ứng viên: {title}",
        "preheader": "Tất cả ứng viên của buổi phỏng vấn “{title}” tại {company}. Báo cáo được đính kèm.",
        "heading": "Báo cáo ứng viên",
        "lines": [
            (
                "{sender} từ {company} đã chia sẻ báo cáo tất cả ứng viên cho buổi phỏng vấn "
                "“{title}”."
            ),
            (
                "Báo cáo được đính kèm dưới dạng PDF: điểm, tiến độ của từng ứng viên và những gì "
                "trình duyệt của họ ghi nhận, xếp từ cao xuống thấp. Trả lời email này để phản hồi "
                "{sender}."
            ),
        ],
        "button": "Truy cập prepza",
        "footer": "Email này được gửi đến {email} vì {sender} đã chia sẻ một báo cáo ứng viên "
        "với địa chỉ này trên prepza. Nếu bạn không mong đợi email này, bạn có thể bỏ qua.",
    },
    "footer": "Email này được gửi đến {email} vì có người đã mời địa chỉ này trên prepza. Nếu "
    "bạn không mong đợi email này, bạn có thể bỏ qua.",
    "paste_link": "Hoặc dán liên kết này vào trình duyệt của bạn",
    # The footer's links: optional emails' unsubscribe and settings, and a candidate's own.
    "unsubscribe": "Hủy đăng ký",
    "email_settings": "Thay đổi cài đặt email",
    "stop_reminders": "Đừng gửi lời nhắc về buổi phỏng vấn này cho tôi",
    "stop_company": "Đừng gửi email từ {company} cho tôi",
}
