# Email texts in Japanese. Values are filled in with str.format; the HTML version escapes them.

# The footer of reminders to a company's owners and admins.
MEMBER_FOOTER = (
    "このメールは、prepza で会社の所有者または管理者であるため {email} に送信されました。"
)

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
    "member": {
        "subject": "{inviter}から prepza の{company}のチームへの招待が届いています",
        "preheader": "{role}として{company}のチームに参加できます。承諾するには {email} でサインインしてください。",
        "heading": "チームへの招待",
        "lines": [
            "{inviter}が、prepza の{company}のチームに{role}としてあなたを招待しています。",
            "招待を承諾するには {email} でサインインしてください。このアドレスでのみ招待を承諾できます。",
        ],
        "button": "招待を開く",
        # The role's name as the lines use it.
        "roles": {"admin": "管理者", "viewer": "閲覧者"},
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
    "digest": {
        "subject": "prepza のアクティビティのまとめ",
        "preheader": "過去24時間にあなたの会社で起きたこと。",
        "heading": "アクティビティのまとめ",
        "lines": [
            "過去24時間に prepza のあなたの会社で起きたことをお知らせします。",
        ],
        "rows": {
            "candidate_finished": "面接を完了した候補者：{count} · 「{title}」",
            "invite_undelivered": "届かなかった招待：{count} · 「{title}」",
            "ats_not_invited": "招待されなかった ATS の候補者：{count}",
            "interview_ready": "準備ができた面接：「{title}」",
        },
        "button": "prepza を開く",
        "footer": "このメールは、prepza の会社のメンバーとしてアクティビティのまとめを受け取っているため {email} に送信されました。",
    },
    "low_credits": {
        "subject": "クレジットが残りわずかです",
        "preheader": "候補者の招待を続けるにはチャージしてください。",
        "heading": "クレジットが残りわずかです",
        "lines": [
            "これらの会社には、候補者をもう1人招待するのに十分なクレジットがありません。候補者の招待を続けるにはチャージしてください。",
        ],
        "rows": {
            "company": "{company} · 利用可能なクレジット：{available}",
        },
        "button": "チャージする",
        "footer": MEMBER_FOOTER,
    },
    "no_candidates": {
        "subject": "候補者を待っています",
        "preheader": "メールで候補者を招待するか、面接のリンクを共有してください。",
        "heading": "候補者を待っています",
        "lines": [
            "これらの面接は数日前から準備ができていますが、まだ誰も招待されていません。メールで候補者を招待するか、面接のリンクを共有してください。",
        ],
        "rows": {
            "interview": "「{title}」 · {company}",
        },
        "button": "候補者を招待する",
        "footer": MEMBER_FOOTER,
    },
    "review_waiting": {
        "subject": "トピックの確認をお待ちしています",
        "preheader": "トピックを確定すると、問題が作られます。",
        "heading": "トピックを確認",
        "lines": [
            "作成を始めた面接のトピックが確認を待っています。確定すると問題が作られます。14日間確認されないままのものはキャンセルされます。",
        ],
        "rows": {
            "interview": "{company} · 待機日数：{days}",
        },
        "button": "トピックを確認する",
        "footer": MEMBER_FOOTER,
    },
    "top_up_failed": {
        "subject": "{company} の自動チャージに失敗しました",
        "preheader": "カードに請求できませんでした。候補者の招待を続けるにはチャージしてください。",
        "heading": "自動チャージに失敗しました",
        "lines": [
            "自動チャージで {company} のカードに請求できなかったため、クレジットは追加されていません。",
            "候補者の招待を続けるにはチャージしてください。自動チャージは後でもう一度カードへの請求を試みます。",
        ],
        "button": "チャージする",
        "footer": "このメールは、prepza で {company} の所有者または管理者であるため {email} に送信されました。会社の請求に関する内容のため、メール設定にかかわらず送信されます。",
    },
    "footer": "このメールは、prepza で誰かがこのアドレスを招待したため {email} に送信されました。心当たりがない場合は無視してください。",
    "paste_link": "または、このリンクをブラウザに貼り付けてください",
    # The footer's links: optional emails' unsubscribe and settings, and a candidate's own.
    "unsubscribe": "配信停止",
    "email_settings": "メール設定を変更",
    "stop_reminders": "この面接のリマインダーを受け取らない",
    "stop_company": "{company}からのメールを受け取らない",
}
