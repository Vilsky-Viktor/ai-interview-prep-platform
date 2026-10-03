# Email texts in Vietnamese. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "share": {
        "subject": "{inviter} mời bạn tham gia “{title}”",
        "preheader": "Đăng nhập bằng {email} để bắt đầu chuẩn bị.",
        "heading": "Bộ chuẩn bị dành cho bạn",
        "lines": [
            "{inviter} mời bạn cùng chuẩn bị với “{title}” trên prepza.",
            ("Đăng nhập bằng {email} để tham gia. Chỉ địa chỉ này mới có thể chấp nhận lời mời."),
        ],
        "button": "Mở lời mời",
    },
    "candidate": {
        "subject": "{company} mời bạn tham gia phỏng vấn",
        "preheader": "Làm bài “{title}” trên prepza. Đăng nhập bằng {email} để bắt đầu.",
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
    "footer": "Email này được gửi đến {email} vì có người đã mời địa chỉ này trên prepza. Nếu "
    "bạn không mong đợi email này, bạn có thể bỏ qua.",
    "paste_link": "Hoặc dán liên kết này vào trình duyệt của bạn",
}
