# Email texts in Arabic. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "share": {
        "subject": "تلقيت دعوة من {inviter} إلى «{title}»",
        "preheader": "سجّل الدخول باستخدام {email} لبدء الاستعداد.",
        "heading": "استعداد من أجلك",
        "lines": [
            "تلقيت دعوة من {inviter} للاستعداد باستخدام «{title}» على prepza.",
            "سجّل الدخول باستخدام {email} للانضمام. لا يمكن قبول الدعوة إلا من هذا العنوان.",
        ],
        "button": "افتح الدعوة",
    },
    "candidate": {
        "subject": "تلقيت دعوة من {company} إلى مقابلة",
        "preheader": "أجرِ «{title}» على prepza. سجّل الدخول باستخدام {email} للبدء.",
        "heading": "دعوة إلى مقابلة",
        "lines": [
            "تلقيت دعوة من {company} إلى مقابلة «{title}» على prepza.",
            (
                "سجّل الدخول باستخدام {email} للبدء. لا يمكن إجراء المقابلة إلا من "
                "هذا العنوان، ولديك محاولة واحدة فقط."
            ),
        ],
        "button": "افتح الدعوة",
    },
    "footer": "أُرسلت هذه الرسالة إلى {email} لأن أحدهم دعا هذا العنوان على prepza. إذا لم تكن "
    "تتوقعها، فيمكنك تجاهلها.",
    "paste_link": "أو الصق هذا الرابط في متصفحك",
}
