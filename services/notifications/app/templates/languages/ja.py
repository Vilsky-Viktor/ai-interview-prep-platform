# Email texts in Japanese. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "candidate": {
        "subject": "{company}から面接の招待が届いています",
        "preheader": "prepza で「{title}」を受けてください。開始するには {email} でサインインしてください。",
        "heading": "面接のご案内",
        "lines": [
            "{company}が、prepza の面接「{title}」にあなたを招待しています。",
            "開始するには {email} でサインインしてください。このアドレスでのみ、1回だけ面接を受けられます。",
        ],
        "button": "招待を開く",
    },
    "reminder": {
        "subject": "リマインダー: {company}の面接が未受験です",
        "preheader": "「{title}」はまだ受けられます。開始するには {email} でサインインしてください。",
        "heading": "未受験の面接があります",
        "lines": [
            "数日前、{company}が prepza の面接「{title}」にあなたを招待しましたが、まだ開始されていません。",
            "開始するには {email} でサインインしてください。このアドレスでのみ、1回だけ面接を受けられます。招待は送信から30日で期限切れになります。",
        ],
        "button": "招待を開く",
    },
    "report": {
        "subject": "候補者レポート: {candidate}",
        "preheader": "{candidate}さんが{company}の面接「{title}」を受けました。レポートを添付しています。",
        "heading": "候補者レポート",
        "lines": [
            "{company}の{sender}さんが、面接「{title}」の{candidate}さんのレポートを共有しました。",
            "1ページの PDF として添付しています: 総合スコア、各トピックのスコア、候補者のブラウザで記録された内容です。{sender}さんに返信するには、このメールに返信してください。",
        ],
        "button": "prepza にアクセス",
        "footer": "このメールは、{sender}さんが prepza でこのアドレスに候補者レポートを共有したため {email} に送信されました。心当たりがない場合は無視してください。",
    },
    "candidates": {
        "subject": "全候補者のレポート: {title}",
        "preheader": "{company}の「{title}」の全候補者です。レポートを添付しています。",
        "heading": "全候補者レポート",
        "lines": [
            "{company}の{sender}さんが、面接「{title}」の全候補者のレポートを共有しました。",
            "PDF として添付しています: 各候補者のスコア、進捗、ブラウザで記録された内容を、スコアの高い順に並べています。{sender}さんに返信するには、このメールに返信してください。",
        ],
        "button": "prepza にアクセス",
        "footer": "このメールは、{sender}さんが prepza でこのアドレスに全候補者のレポートを共有したため {email} に送信されました。心当たりがない場合は無視してください。",
    },
    "footer": "このメールは、prepza で誰かがこのアドレスを招待したため {email} に送信されました。心当たりがない場合は無視してください。",
    "paste_link": "または、このリンクをブラウザに貼り付けてください",
}
