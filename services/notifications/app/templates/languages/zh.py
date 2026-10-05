# Email texts in Chinese (Simplified). Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "candidate": {
        "subject": "{company} 邀请你参加面试",
        "preheader": "在 prepza 上完成“{title}”。使用 {email} 登录即可开始。",
        "heading": "面试邀请",
        "lines": [
            "{company} 邀请你在 prepza 上参加“{title}”面试。",
            "使用 {email} 登录即可开始。只有这个邮箱地址可以参加面试，并且只有一次机会。",
        ],
        "button": "打开邀请",
    },
    "reminder": {
        "subject": "提醒：{company} 正在等你参加面试",
        "preheader": "“{title}”仍然开放。使用 {email} 登录即可开始。",
        "heading": "你的面试在等你",
        "lines": [
            "{company} 几天前邀请你在 prepza 上参加“{title}”面试，你还没有开始。",
            "使用 {email} 登录即可开始。只有这个邮箱地址可以参加面试，并且只有一次机会。邀请在发送 30 天后失效。",
        ],
        "button": "打开邀请",
    },
    "report": {
        "subject": "{sender} 分享了一份候选人报告：{candidate}",
        "preheader": "{candidate} 参加了 {company} 的“{title}”。报告已附上。",
        "heading": "候选人报告",
        "lines": [
            "{company} 的 {sender} 分享了 {candidate} 在“{title}”面试中的报告。",
            "报告以一页 PDF 附上：总成绩、每个主题的分数，以及候选人浏览器记录的情况。直接回复此邮件即可回复 {sender}。",
        ],
        "button": "访问 prepza",
        "footer": "这封邮件发送到 {email}，因为 {sender} 在 prepza 上与这个地址分享了一份候选人报告。如果你没有预期收到它，可以忽略。",
    },
    "candidates": {
        "subject": "{sender} 分享了一份全部候选人的报告：{title}",
        "preheader": "{company} 的“{title}”的全部候选人。报告已附上。",
        "heading": "全部候选人报告",
        "lines": [
            "{company} 的 {sender} 分享了“{title}”面试全部候选人的报告。",
            "报告以 PDF 附上：每位候选人的成绩、进度以及浏览器记录的情况，按成绩从高到低排列。直接回复此邮件即可回复 {sender}。",
        ],
        "button": "访问 prepza",
        "footer": "这封邮件发送到 {email}，因为 {sender} 在 prepza 上与这个地址分享了一份全部候选人的报告。如果你没有预期收到它，可以忽略。",
    },
    "footer": "这封邮件发送到 {email}，因为有人在 prepza 上邀请了这个地址。如果你没有预期收到它，可以忽略。",
    "paste_link": "或者将此链接粘贴到浏览器中",
}
