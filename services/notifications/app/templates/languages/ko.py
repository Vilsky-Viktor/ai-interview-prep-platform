# Email texts in Korean. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
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
    "reminder": {
        "subject": "알림: {company}에서 면접을 기다리고 있습니다",
        "preheader": "“{title}” 면접이 아직 열려 있습니다. {email}(으)로 로그인하면 시작할 수 있습니다.",
        "heading": "아직 응시하지 않은 면접이 있습니다",
        "lines": [
            "며칠 전 {company}에서 prepza의 “{title}” 면접에 초대했지만, 아직 시작하지 않으셨습니다.",
            "{email}(으)로 로그인하면 시작할 수 있습니다. 이 주소로만 면접을 볼 수 있으며, 기회는 한 번뿐입니다. 초대는 발송 후 30일이 지나면 만료됩니다.",
        ],
        "button": "초대 열기",
    },
    "report": {
        "subject": "지원자 보고서: {candidate}",
        "preheader": "{candidate} 님이 {company}의 “{title}” 면접을 봤습니다. 보고서가 첨부되어 있습니다.",
        "heading": "지원자 보고서",
        "lines": [
            "{company}의 {sender} 님이 “{title}” 면접에 대한 {candidate} 님의 보고서를 공유했습니다.",
            "한 페이지 PDF로 첨부되어 있습니다: 전체 점수, 주제별 점수, 지원자의 브라우저에 기록된 내용. {sender} 님에게 답하려면 이 이메일에 회신하세요.",
        ],
        "button": "prepza 방문",
        "footer": "{sender} 님이 prepza에서 이 주소로 지원자 보고서를 공유하여 {email}(으)로 이 이메일이 발송되었습니다. 예상하지 못한 이메일이라면 무시하셔도 됩니다.",
    },
    "candidates": {
        "subject": "전체 지원자 보고서: {title}",
        "preheader": "{company}의 “{title}” 면접 전체 지원자입니다. 보고서가 첨부되어 있습니다.",
        "heading": "전체 지원자 보고서",
        "lines": [
            "{company}의 {sender} 님이 “{title}” 면접의 전체 지원자 보고서를 공유했습니다.",
            "PDF로 첨부되어 있습니다: 각 지원자의 점수, 진행률, 브라우저에 기록된 내용이 점수가 높은 순으로 정리되어 있습니다. {sender} 님에게 답하려면 이 이메일에 회신하세요.",
        ],
        "button": "prepza 방문",
        "footer": "{sender} 님이 prepza에서 이 주소로 전체 지원자 보고서를 공유하여 {email}(으)로 이 이메일이 발송되었습니다. 예상하지 못한 이메일이라면 무시하셔도 됩니다.",
    },
    "footer": "prepza에서 누군가 이 주소를 초대하여 {email}(으)로 이 이메일이 발송되었습니다. 예상하지 못한 이메일이라면 무시하셔도 됩니다.",
    "paste_link": "또는 이 링크를 브라우저에 붙여 넣으세요",
}
