# Email texts in Hebrew, with straight quotes, which read the same right to left. Values are filled
# in with str.format; the HTML version escapes them.

TEXTS = {
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
    "reminder": {
        "subject": "תזכורת: {company} מחכה לראיון שלך",
        "preheader": 'ראיון "{title}" עדיין פתוח. יש להתחבר עם {email} כדי להתחיל.',
        "heading": "הראיון שלך מחכה",
        "lines": [
            (
                'קיבלת הזמנה מ-{company} לראיון "{title}" ב-prepza לפני כמה ימים, ועדיין לא '
                "התחלת אותו."
            ),
            (
                "יש להתחבר עם {email} כדי להתחיל. רק כתובת זו יכולה לגשת לראיון, ויש ניסיון "
                "אחד בלבד. תוקף ההזמנה פג 30 ימים אחרי שליחתה."
            ),
        ],
        "button": "פתיחת ההזמנה",
    },
    "report": {
        "subject": "{sender} שיתף/ה דוח מועמד: {candidate}",
        "preheader": '{candidate} ניגש/ה ל-"{title}" ב-{company}. הדוח מצורף.',
        "heading": "דוח מועמד",
        "lines": [
            '{sender} מ-{company} שיתף/ה את הדוח של {candidate} בראיון "{title}".',
            (
                "הוא מצורף כקובץ PDF בן עמוד אחד: הציון הכולל, הציון בכל נושא ומה שהדפדפן "
                "של המועמד הראה. אפשר להשיב לאימייל הזה כדי לענות ל-{sender}."
            ),
        ],
        "button": "כניסה ל-prepza",
        "footer": "הודעה זו נשלחה אל {email} כי {sender} שיתף/ה דוח מועמד עם הכתובת הזו "
        "ב-prepza. אם לא ציפית לה, אפשר להתעלם ממנה.",
    },
    "candidates": {
        "subject": "{sender} שיתף/ה דוח של כל המועמדים: {title}",
        "preheader": 'כל המועמדים ל-"{title}" ב-{company}. הדוח מצורף.',
        "heading": "דוח מועמדים",
        "lines": [
            '{sender} מ-{company} שיתף/ה את הדוח של כל המועמדים בראיון "{title}".',
            (
                "הוא מצורף כקובץ PDF: הציון של כל מועמד, ההתקדמות שלו ומה שהדפדפן שלו הראה, "
                "מהטוב ביותר ומטה. אפשר להשיב לאימייל הזה כדי לענות ל-{sender}."
            ),
        ],
        "button": "כניסה ל-prepza",
        "footer": "הודעה זו נשלחה אל {email} כי {sender} שיתף/ה דוח מועמדים עם הכתובת הזו "
        "ב-prepza. אם לא ציפית לה, אפשר להתעלם ממנה.",
    },
    "footer": "הודעה זו נשלחה אל {email} כי מישהו הזמין את הכתובת הזו ב-prepza. אם לא ציפית לה, "
    "אפשר להתעלם ממנה.",
    "paste_link": "או להדביק את הקישור הזה בדפדפן",
}
