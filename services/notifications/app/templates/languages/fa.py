# Email texts in Persian. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "share": {
        "subject": "{inviter} شما را به «{title}» دعوت می\u200cکند",
        "preheader": "برای شروع آمادگی با {email} وارد شوید.",
        "heading": "آمادگی برای شما",
        "lines": [
            "{inviter} شما را دعوت می\u200cکند تا با «{title}» در prepza آماده شوید.",
            "برای پیوستن با {email} وارد شوید. فقط این نشانی می\u200cتواند دعوت را بپذیرد.",
        ],
        "button": "باز کردن دعوت",
    },
    "candidate": {
        "subject": "{company} شما را به مصاحبه دعوت می\u200cکند",
        "preheader": "مصاحبهٔ «{title}» را در prepza انجام دهید. برای شروع با {email} وارد شوید.",
        "heading": "دعوت به مصاحبه",
        "lines": [
            "{company} شما را به مصاحبهٔ «{title}» در prepza دعوت می\u200cکند.",
            (
                "برای شروع با {email} وارد شوید. فقط این نشانی می\u200cتواند در "
                "مصاحبه شرکت کند و تنها یک فرصت دارید."
            ),
        ],
        "button": "باز کردن دعوت",
    },
    "footer": "این ایمیل به {email} فرستاده شد چون کسی این نشانی را در prepza دعوت کرده است. اگر "
    "انتظارش را نداشتید، می\u200cتوانید آن را نادیده بگیرید.",
    "paste_link": "یا این پیوند را در مرورگر خود بچسبانید",
}
