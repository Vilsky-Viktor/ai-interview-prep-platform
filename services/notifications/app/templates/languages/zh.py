# Email texts in Chinese (Simplified). Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "share": {
        "subject": "{inviter} 邀请你加入“{title}”",
        "preheader": "使用 {email} 登录，开始准备。",
        "heading": "为你准备的学习包",
        "lines": [
            "{inviter} 邀请你在 prepza 上使用“{title}”进行准备。",
            "使用 {email} 登录即可加入。只有这个邮箱地址可以接受邀请。",
        ],
        "button": "打开邀请",
    },
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
    "footer": "这封邮件发送到 {email}，因为有人在 prepza 上邀请了这个地址。如果你没有预期收到它，可以忽略。",
    "paste_link": "或者将此链接粘贴到浏览器中",
}
