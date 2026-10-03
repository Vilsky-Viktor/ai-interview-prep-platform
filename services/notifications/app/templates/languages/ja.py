# Email texts in Japanese. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "share": {
        "subject": "{inviter}さんから「{title}」への招待が届いています",
        "preheader": "準備を始めるには {email} でサインインしてください。",
        "heading": "あなたのための準備",
        "lines": [
            "{inviter}さんが、prepza の「{title}」で一緒に準備するようあなたを招待しています。",
            "参加するには {email} でサインインしてください。招待を承認できるのはこのアドレスだけです。",
        ],
        "button": "招待を開く",
    },
    "candidate": {
        "subject": "{company}から面接の招待が届いています",
        "preheader": "prepza で「{title}」を受けてください。開始するには {email} でサインインしてください。",
        "heading": "面接のご案内",
        "lines": [
            "{company}が、prepza の面接「{title}」にあなたを招待しています。",
            "開始するには {email} でサインインしてください。面接を受けられるのはこのアドレスだけで、受験は1回のみです。",
        ],
        "button": "招待を開く",
    },
    "footer": "このメールは、prepza で誰かがこのアドレスを招待したため {email} に送信されました。心当たりがない場合は無視してください。",
    "paste_link": "または、このリンクをブラウザに貼り付けてください",
}
