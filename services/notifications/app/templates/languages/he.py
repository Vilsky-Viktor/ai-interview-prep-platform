# Email texts in Hebrew, with straight quotes, which read the same right to left. Values are filled
# in with str.format; the HTML version escapes them.

# The footer of reminders to a company's owners and admins.
MEMBER_FOOTER = "הודעה זו נשלחה אל {email} כי יש לכם תפקיד של בעלים או מנהל בחברה ב-prepza."

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
    "member": {
        "subject": "קיבלת הזמנה מ-{inviter} להצטרף לצוות של {company} ב-prepza",
        "preheader": (
            "הצטרפות לצוות של {company} בתפקיד {role}. יש להתחבר עם {email} כדי לקבל את ההזמנה."
        ),
        "heading": "הזמנה להצטרף לצוות",
        "lines": [
            "קיבלת הזמנה מ-{inviter} להצטרף לצוות של {company} ב-prepza בתפקיד {role}.",
            "יש להתחבר עם {email} כדי לקבל את ההזמנה. רק כתובת זו יכולה לקבל את ההזמנה.",
        ],
        "button": "פתיחת ההזמנה",
        # The role's name as the lines use it.
        "roles": {"admin": "מנהל", "viewer": "צופה"},
    },
    "report": {
        "subject": "דוח מועמד: {candidate}",
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
        "subject": "דוח של כל המועמדים: {title}",
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
    "digest": {
        "subject": "סיכום הפעילות שלכם ב-prepza",
        "preheader": "מה קרה בחברות שלכם ב-24 השעות האחרונות.",
        "heading": "סיכום הפעילות שלכם",
        "lines": [
            "זה מה שקרה בחברות שלכם ב-prepza ב-24 השעות האחרונות.",
        ],
        "rows": {
            "candidate_finished": 'מועמדים שסיימו: {count} · "{title}"',
            "invite_undelivered": 'הזמנות שלא נמסרו: {count} · "{title}"',
            "ats_not_invited": "מועמדים מה-ATS שלא הוזמנו: {count}",
            "interview_ready": 'ראיון מוכן: "{title}"',
        },
        "button": "פתיחת prepza",
        "footer": (
            "הודעה זו נשלחה אל {email} כי אתם חברים בחברה ב-prepza ומקבלים את סיכום הפעילות שלה."
        ),
    },
    "low_credits": {
        "subject": "הקרדיטים שלכם עומדים להיגמר",
        "preheader": "טענו כדי להמשיך להזמין מועמדים.",
        "heading": "הקרדיטים עומדים להיגמר",
        "lines": [
            "לחברות האלה אין מספיק קרדיטים כדי להזמין עוד מועמד. טענו כדי להמשיך להזמין מועמדים.",
        ],
        "rows": {
            "company": "{company} · קרדיטים זמינים: {available}",
        },
        "button": "טעינה",
        "footer": MEMBER_FOOTER,
    },
    "no_candidates": {
        "subject": "ממתינים למועמדים",
        "preheader": "הזמינו מועמדים באימייל או שתפו את הקישור לראיון.",
        "heading": "ממתינים למועמדים",
        "lines": [
            (
                "הראיונות האלה מוכנים כבר כמה ימים, אבל עדיין לא הוזמן אף אחד. הזמינו "
                "מועמדים באימייל או שתפו את הקישור לראיון."
            ),
        ],
        "rows": {
            "interview": '"{title}" · {company}',
        },
        "button": "הזמנת מועמדים",
        "footer": MEMBER_FOOTER,
    },
    "review_waiting": {
        "subject": "הנושאים שלכם ממתינים לבדיקה",
        "preheader": "אשרו את הנושאים והשאלות ייווצרו.",
        "heading": "בדקו את הנושאים",
        "lines": [
            (
                "הנושאים של הראיונות שהתחלתם ממתינים לבדיקה שלכם. ברגע שתאשרו אותם, השאלות "
                "ייווצרו. בדיקה שנשארת פתוחה 14 ימים מבוטלת."
            ),
        ],
        "rows": {
            "interview": "{company} · ימי המתנה: {days}",
        },
        "button": "בדיקת הנושאים",
        "footer": MEMBER_FOOTER,
    },
    "top_up_failed": {
        "subject": "הטעינה האוטומטית נכשלה עבור {company}",
        "preheader": "לא ניתן היה לחייב את הכרטיס. טענו כדי להמשיך להזמין מועמדים.",
        "heading": "הטעינה האוטומטית נכשלה",
        "lines": [
            "הטעינה האוטומטית לא הצליחה לחייב את הכרטיס עבור {company}, ולכן לא נוספו קרדיטים.",
            "טענו כדי להמשיך להזמין מועמדים. הטעינה האוטומטית תנסה לחייב את הכרטיס שוב מאוחר יותר.",
        ],
        "button": "טעינה",
        "footer": (
            "הודעה זו נשלחה אל {email} כי יש לכם תפקיד של בעלים או מנהל ב-{company} "
            "ב-prepza. היא עוסקת בחיוב של החברה שלכם, ולכן נשלחת בלי קשר להגדרות האימייל "
            "שלכם."
        ),
    },
    "footer": "הודעה זו נשלחה אל {email} כי מישהו הזמין את הכתובת הזו ב-prepza. אם לא ציפית לה, "
    "אפשר להתעלם ממנה.",
    "paste_link": "או להדביק את הקישור הזה בדפדפן",
    # The footer's links: optional emails' unsubscribe and settings, and a candidate's own.
    "unsubscribe": "ביטול הרשמה",
    "email_settings": "שינוי הגדרות האימייל",
    "stop_reminders": "לא לשלוח לי תזכורות לראיון הזה",
    "stop_company": "לא לשלוח לי אימיילים מטעם {company}",
}
