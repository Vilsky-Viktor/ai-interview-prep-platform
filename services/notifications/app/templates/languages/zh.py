# Email texts in Chinese (Simplified). Values are filled in with str.format; the HTML version escapes them.

# The footer of reminders to a company's owners and admins.
MEMBER_FOOTER = "这封邮件发送到 {email}，因为你是 prepza 上某家公司的所有者或管理员。"

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
        "heading": "你的面试尚未开始",
        "lines": [
            "{company} 几天前邀请你在 prepza 上参加“{title}”面试，你还没有开始。",
            "使用 {email} 登录即可开始。只有这个邮箱地址可以参加面试，并且只有一次机会。邀请在发送 30 天后失效。",
        ],
        "button": "打开邀请",
    },
    "member": {
        "subject": "{inviter} 邀请你加入 prepza 上的 {company} 团队",
        "preheader": "以{role}身份加入 {company} 团队。使用 {email} 登录即可接受邀请。",
        "heading": "团队邀请",
        "lines": [
            "{inviter} 邀请你以{role}身份加入 prepza 上的 {company} 团队。",
            "使用 {email} 登录即可接受邀请。只有这个邮箱地址可以接受邀请。",
        ],
        "button": "打开邀请",
        # The role's name as the lines use it.
        "roles": {"admin": "管理员", "viewer": "查看者"},
    },
    "report": {
        "subject": "候选人报告：{candidate}",
        "preheader": "{candidate} 参加了 {company} 的“{title}”。报告已附上。",
        "heading": "候选人报告",
        "lines": [
            "{company} 的 {sender} 分享了 {candidate} 在“{title}”面试中的报告。",
            "报告以一页 PDF 附上：总成绩、每个主题的分数，以及候选人浏览器记录的情况。直接回复此邮件即可回复 {sender}。",
        ],
        "button": "访问 prepza",
        "footer": "这封邮件发送到 {email}，因为 {sender} 在 prepza 上与这个地址分享了一份候选人报告。如果这封邮件与你无关，可以忽略。",
    },
    "candidates": {
        "subject": "全部候选人报告：{title}",
        "preheader": "{company} 的“{title}”的全部候选人。报告已附上。",
        "heading": "全部候选人报告",
        "lines": [
            "{company} 的 {sender} 分享了“{title}”面试全部候选人的报告。",
            "报告以 PDF 附上：每位候选人的成绩、进度以及浏览器记录的情况，按成绩从高到低排列。直接回复此邮件即可回复 {sender}。",
        ],
        "button": "访问 prepza",
        "footer": "这封邮件发送到 {email}，因为 {sender} 在 prepza 上与这个地址分享了一份全部候选人的报告。如果这封邮件与你无关，可以忽略。",
    },
    "digest": {
        "subject": "你在 prepza 的动态摘要",
        "preheader": "过去 24 小时你的公司里发生的事。",
        "heading": "你的动态摘要",
        "lines": [
            "以下是过去 24 小时你在 prepza 上的公司里发生的事。",
        ],
        "rows": {
            "candidate_finished": "已完成面试的候选人：{count} · “{title}”",
            "invite_undelivered": "未送达的邀请：{count} · “{title}”",
            "ats_not_invited": "未被邀请的 ATS 候选人：{count}",
            "interview_ready": "已就绪的面试：“{title}”",
        },
        "button": "打开 prepza",
        "footer": "这封邮件发送到 {email}，因为你是 prepza 上某家公司的成员，并接收它的动态摘要。",
    },
    "low_credits": {
        "subject": "你的点数即将用完",
        "preheader": "充值后才能继续邀请候选人。",
        "heading": "点数即将用完",
        "lines": [
            "这些公司的点数已不够再邀请一位候选人。充值后才能继续邀请候选人。",
        ],
        "rows": {
            "company": "{company} · 可用点数：{available}",
        },
        "button": "充值",
        "footer": MEMBER_FOOTER,
    },
    "no_candidates": {
        "subject": "等待候选人",
        "preheader": "通过邮件邀请候选人，或分享面试链接。",
        "heading": "等待候选人",
        "lines": [
            "这些面试已就绪好几天了，但还没有邀请任何人。通过邮件邀请候选人，或分享面试链接。",
        ],
        "rows": {
            "interview": "“{title}” · {company}",
        },
        "button": "邀请候选人",
        "footer": MEMBER_FOOTER,
    },
    "review_waiting": {
        "subject": "你的主题正在等待审阅",
        "preheader": "确认主题后即会生成题目。",
        "heading": "审阅你的主题",
        "lines": [
            "你开始创建的面试的主题正在等待你审阅。确认后即会生成题目。审阅保持未完成满 14 天将被取消。",
        ],
        "rows": {
            "interview": "{company} · 已等待天数：{days}",
        },
        "button": "审阅主题",
        "footer": MEMBER_FOOTER,
    },
    "top_up_failed": {
        "subject": "{company} 的自动充值失败",
        "preheader": "无法从银行卡扣款。充值后才能继续邀请候选人。",
        "heading": "自动充值失败",
        "lines": [
            "自动充值无法从 {company} 的银行卡扣款，因此没有添加点数。",
            "充值后才能继续邀请候选人。自动充值稍后会再次尝试扣款。",
        ],
        "button": "充值",
        "footer": "这封邮件发送到 {email}，因为你是 prepza 上 {company} 的所有者或管理员。它与你公司的账单有关，因此无论你的邮件设置如何都会发送。",
    },
    "footer": "这封邮件发送到 {email}，因为有人在 prepza 上邀请了这个地址。如果这封邮件与你无关，可以忽略。",
    "paste_link": "或者将此链接粘贴到浏览器中",
    # The footer's links: optional emails' unsubscribe and settings, and a candidate's own.
    "unsubscribe": "退订",
    "email_settings": "更改邮件设置",
    "stop_reminders": "不再给我发送此面试的提醒",
    "stop_company": "不再给我发送来自 {company} 的邮件",
}
