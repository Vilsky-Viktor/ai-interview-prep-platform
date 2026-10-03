# Email texts in Korean. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "share": {
        "subject": "{inviter}님이 “{title}”에 초대했습니다",
        "preheader": "{email}(으)로 로그인하고 준비를 시작하세요.",
        "heading": "당신을 위한 준비",
        "lines": [
            "{inviter}님이 prepza에서 “{title}”(으)로 함께 준비하도록 초대했습니다.",
            "{email}(으)로 로그인하면 참여할 수 있습니다. 이 주소로만 초대를 수락할 수 있습니다.",
        ],
        "button": "초대 열기",
    },
    "candidate": {
        "subject": "{company}에서 면접에 초대했습니다",
        "preheader": "prepza에서 “{title}” 면접을 보세요. {email}(으)로 로그인하면 시작할 수 있습니다.",
        "heading": "면접 초대",
        "lines": [
            "{company}에서 prepza의 “{title}” 면접에 초대했습니다.",
            "{email}(으)로 로그인하면 시작할 수 있습니다. 이 주소로만 면접을 볼 수 있으며, 기회는 한 번뿐입니다.",
        ],
        "button": "초대 열기",
    },
    "footer": "prepza에서 누군가 이 주소를 초대하여 {email}(으)로 이 이메일이 발송되었습니다. 예상하지 못한 이메일이라면 무시하셔도 됩니다.",
    "paste_link": "또는 이 링크를 브라우저에 붙여 넣으세요",
}
