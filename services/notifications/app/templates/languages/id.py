# Email texts in Indonesian. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "share": {
        "subject": "{inviter} mengundangmu ke “{title}”",
        "preheader": "Masuk dengan {email} untuk mulai bersiap.",
        "heading": "Persiapan untukmu",
        "lines": [
            "{inviter} mengundangmu untuk bersiap dengan “{title}” di prepza.",
            ("Masuk dengan {email} untuk bergabung. Hanya alamat ini yang bisa menerima undangan."),
        ],
        "button": "Buka undangan",
    },
    "candidate": {
        "subject": "{company} mengundangmu ke wawancara",
        "preheader": "Ikuti “{title}” di prepza. Masuk dengan {email} untuk mulai.",
        "heading": "Undangan wawancara",
        "lines": [
            "{company} mengundangmu ke wawancara “{title}” di prepza.",
            (
                "Masuk dengan {email} untuk mulai. Hanya alamat ini yang bisa "
                "mengikuti wawancara, dan kamu punya satu kesempatan."
            ),
        ],
        "button": "Buka undangan",
    },
    "footer": "Email ini dikirim ke {email} karena seseorang mengundang alamat ini di prepza. "
    "Jika kamu tidak mengharapkannya, abaikan saja.",
    "paste_link": "Atau tempel tautan ini di browsermu",
}
