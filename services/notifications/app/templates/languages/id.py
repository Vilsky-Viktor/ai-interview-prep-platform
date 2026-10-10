# Email texts in Indonesian. Values are filled in with str.format; the HTML version escapes them.

# The footer of reminders to a company's owners and admins.
MEMBER_FOOTER = (
    "Email ini dikirim ke {email} karena kamu pemilik atau admin sebuah perusahaan di prepza."
)

TEXTS = {
    "candidate": {
        "subject": "{company} mengundangmu mengikuti wawancara",
        "preheader": "Ikuti “{title}” di prepza. Masuk dengan {email} untuk mulai.",
        "heading": "Undangan wawancara",
        "lines": [
            "{company} mengundangmu mengikuti wawancara “{title}” di prepza.",
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
                "{company} mengundangmu mengikuti wawancara “{title}” di prepza beberapa hari "
                "lalu, dan kamu belum memulainya."
            ),
            (
                "Masuk dengan {email} untuk mulai. Hanya alamat ini yang bisa mengikuti wawancara, "
                "dan kamu punya satu kesempatan. Undangan kedaluwarsa 30 hari setelah dikirim."
            ),
        ],
        "button": "Buka undangan",
    },
    "member": {
        "subject": "{inviter} mengundangmu bergabung dengan tim {company} di prepza",
        "preheader": (
            "Bergabunglah dengan tim {company} sebagai {role}. Masuk dengan {email} untuk menerima "
            "undangan."
        ),
        "heading": "Undangan bergabung dengan tim",
        "lines": [
            "{inviter} mengundangmu bergabung dengan tim {company} di prepza sebagai {role}.",
            (
                "Masuk dengan {email} untuk menerima undangan. Hanya alamat ini yang bisa menerima "
                "undangan."
            ),
        ],
        "button": "Buka undangan",
        # The role's name as the lines use it.
        "roles": {"admin": "admin", "viewer": "pelihat"},
    },
    "report": {
        "subject": "Laporan kandidat: {candidate}",
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
        "subject": "Laporan semua kandidat: {title}",
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
    "digest": {
        "subject": "Ringkasan aktivitasmu di prepza",
        "preheader": "Apa yang terjadi di perusahaanmu dalam 24 jam terakhir.",
        "heading": "Ringkasan aktivitasmu",
        "lines": [
            "Inilah yang terjadi di perusahaanmu di prepza dalam 24 jam terakhir.",
        ],
        "rows": {
            "candidate_finished": "Kandidat yang selesai: {count} · “{title}”",
            "invite_undelivered": "Undangan yang tidak terkirim: {count} · “{title}”",
            "ats_not_invited": "Kandidat ATS yang tidak diundang: {count}",
            "interview_ready": "Wawancara siap: “{title}”",
        },
        "button": "Buka prepza",
        "footer": (
            "Email ini dikirim ke {email} karena kamu anggota sebuah perusahaan di prepza "
            "dan menerima ringkasan aktivitasnya."
        ),
    },
    "low_credits": {
        "subject": "Kreditmu hampir habis",
        "preheader": "Isi ulang untuk terus mengundang kandidat.",
        "heading": "Kredit hampir habis",
        "lines": [
            (
                "Perusahaan ini tidak punya cukup kredit untuk mengundang satu kandidat "
                "lagi. Isi ulang untuk terus mengundang kandidat."
            ),
        ],
        "rows": {
            "company": "{company} · kredit tersedia: {available}",
        },
        "button": "Isi ulang",
        "footer": MEMBER_FOOTER,
    },
    "no_candidates": {
        "subject": "Menunggu kandidat",
        "preheader": "Undang kandidat lewat email atau bagikan tautan wawancaranya.",
        "heading": "Menunggu kandidat",
        "lines": [
            (
                "Wawancara ini sudah siap sejak beberapa hari lalu, tetapi belum ada yang "
                "diundang. Undang kandidat lewat email atau bagikan tautan wawancaranya."
            ),
        ],
        "rows": {
            "interview": "“{title}” · {company}",
        },
        "button": "Undang kandidat",
        "footer": MEMBER_FOOTER,
    },
    "review_waiting": {
        "subject": "Topikmu menunggu ditinjau",
        "preheader": "Konfirmasi topiknya, lalu pertanyaan akan dibuat.",
        "heading": "Tinjau topikmu",
        "lines": [
            (
                "Topik wawancara yang kamu mulai sedang menunggu tinjauanmu. Setelah kamu "
                "mengonfirmasinya, pertanyaan akan dibuat. Tinjauan yang dibiarkan terbuka "
                "selama 14 hari akan dibatalkan."
            ),
        ],
        "rows": {
            "interview": "{company} · hari menunggu: {days}",
        },
        "button": "Tinjau topik",
        "footer": MEMBER_FOOTER,
    },
    "top_up_failed": {
        "subject": "Isi ulang otomatis untuk {company} gagal",
        "preheader": "Kartu tidak dapat ditagih. Isi ulang untuk terus mengundang kandidat.",
        "heading": "Isi ulang otomatis gagal",
        "lines": [
            (
                "Isi ulang otomatis gagal menagih kartu untuk {company}, jadi tidak ada "
                "kredit yang ditambahkan."
            ),
            (
                "Isi ulang untuk terus mengundang kandidat. Isi ulang otomatis akan mencoba"
                " kartu itu lagi nanti."
            ),
        ],
        "button": "Isi ulang",
        "footer": (
            "Email ini dikirim ke {email} karena kamu pemilik atau admin {company} di "
            "prepza. Email ini tentang penagihan perusahaanmu, jadi selalu dikirim apa pun "
            "pengaturan emailmu."
        ),
    },
    "footer": "Email ini dikirim ke {email} karena seseorang mengundang alamat ini di prepza. "
    "Jika kamu tidak mengharapkannya, abaikan saja.",
    "paste_link": "Atau tempel tautan ini di browsermu",
    # The footer's links: optional emails' unsubscribe and settings, and a candidate's own.
    "unsubscribe": "Berhenti berlangganan",
    "email_settings": "Ubah pengaturan email",
    "stop_reminders": "Jangan kirimi saya pengingat untuk wawancara ini",
    "stop_company": "Jangan kirimi saya email dari {company}",
    # Who runs prepza, at the end of every email.
    "operator": "prepza dijalankan oleh {name}, {address}.",
}
