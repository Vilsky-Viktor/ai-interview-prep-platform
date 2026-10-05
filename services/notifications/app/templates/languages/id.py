# Email texts in Indonesian. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
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
    "reminder": {
        "subject": "Pengingat: {company} menunggu wawancaramu",
        "preheader": "“{title}” masih terbuka. Masuk dengan {email} untuk mulai.",
        "heading": "Wawancaramu sedang menunggu",
        "lines": [
            (
                "{company} mengundangmu ke wawancara “{title}” di prepza beberapa hari lalu, dan "
                "kamu belum memulainya."
            ),
            (
                "Masuk dengan {email} untuk mulai. Hanya alamat ini yang bisa mengikuti wawancara, "
                "dan kamu punya satu kesempatan. Undangan kedaluwarsa 30 hari setelah dikirim."
            ),
        ],
        "button": "Buka undangan",
    },
    "report": {
        "subject": "{sender} membagikan laporan kandidat: {candidate}",
        "preheader": "{candidate} mengikuti “{title}” di {company}. Laporannya terlampir.",
        "heading": "Laporan kandidat",
        "lines": [
            "{sender} dari {company} membagikan laporan {candidate} untuk wawancara “{title}”.",
            (
                "Laporan terlampir sebagai PDF satu halaman: nilai keseluruhan, skor tiap topik, dan "
                "apa yang ditunjukkan browser kandidat. Balas email ini untuk menjawab {sender}."
            ),
        ],
        "button": "Kunjungi prepza",
        "footer": "Email ini dikirim ke {email} karena {sender} membagikan laporan kandidat "
        "dengan alamat ini di prepza. Jika kamu tidak mengharapkannya, abaikan saja.",
    },
    "candidates": {
        "subject": "{sender} membagikan laporan semua kandidat: {title}",
        "preheader": "Semua kandidat untuk “{title}” di {company}. Laporannya terlampir.",
        "heading": "Laporan kandidat",
        "lines": [
            "{sender} dari {company} membagikan laporan semua kandidat untuk wawancara “{title}”.",
            (
                "Laporan terlampir sebagai PDF: nilai, progres, dan apa yang ditunjukkan browser "
                "tiap kandidat, diurutkan dari yang terbaik. Balas email ini untuk menjawab {sender}."
            ),
        ],
        "button": "Kunjungi prepza",
        "footer": "Email ini dikirim ke {email} karena {sender} membagikan laporan kandidat "
        "dengan alamat ini di prepza. Jika kamu tidak mengharapkannya, abaikan saja.",
    },
    "footer": "Email ini dikirim ke {email} karena seseorang mengundang alamat ini di prepza. "
    "Jika kamu tidak mengharapkannya, abaikan saja.",
    "paste_link": "Atau tempel tautan ini di browsermu",
}
