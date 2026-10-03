# Email texts in Hebrew, with straight quotes, which read the same right to left. Values are filled
# in with str.format; the HTML version escapes them.

TEXTS = {
    "share": {
        "subject": 'קיבלת הזמנה מ-{inviter} אל "{title}"',
        "preheader": "יש להתחבר עם {email} כדי להתחיל להתכונן.",
        "heading": "הכנה בשבילך",
        "lines": [
            'קיבלת הזמנה מ-{inviter} להתכונן עם "{title}" ב-prepza.',
            "יש להתחבר עם {email} כדי להצטרף. רק כתובת זו יכולה לקבל את ההזמנה.",
        ],
        "button": "פתיחת ההזמנה",
    },
    "candidate": {
        "subject": "קיבלת הזמנה לראיון מ-{company}",
        "preheader": 'ראיון "{title}" ב-prepza. יש להתחבר עם {email} כדי להתחיל.',
        "heading": "הזמנה לראיון",
        "lines": [
            'קיבלת הזמנה מ-{company} לראיון "{title}" ב-prepza.',
            "יש להתחבר עם {email} כדי להתחיל. רק כתובת זו יכולה לגשת לראיון, ויש ניסיון אחד בלבד.",
        ],
        "button": "פתיחת ההזמנה",
    },
    "footer": "הודעה זו נשלחה אל {email} כי מישהו הזמין את הכתובת הזו ב-prepza. אם לא ציפית לה, "
    "אפשר להתעלם ממנה.",
    "paste_link": "או להדביק את הקישור הזה בדפדפן",
}
