# Email texts in Turkish. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "share": {
        "subject": "{inviter} sizi “{title}” hazırlığına davet ediyor",
        "preheader": "Hazırlanmaya başlamak için {email} ile giriş yapın.",
        "heading": "Sizin için bir hazırlık",
        "lines": [
            "{inviter} sizi prepza'da “{title}” ile hazırlanmaya davet ediyor.",
            "Katılmak için {email} ile giriş yapın. Daveti yalnızca bu adres kabul edebilir.",
        ],
        "button": "Daveti aç",
    },
    "candidate": {
        "subject": "{company} sizi bir mülakata davet ediyor",
        "preheader": "prepza'da “{title}” mülakatına katılın. Başlamak için {email} "
        "ile giriş yapın.",
        "heading": "Mülakat daveti",
        "lines": [
            "{company} sizi prepza'daki “{title}” mülakatına davet ediyor.",
            (
                "Başlamak için {email} ile giriş yapın. Mülakata yalnızca bu adres "
                "katılabilir ve tek bir hakkınız var."
            ),
        ],
        "button": "Daveti aç",
    },
    "footer": "Bu e-posta {email} adresine, biri bu adresi prepza'ya davet ettiği için "
    "gönderildi. Beklemiyorsanız görmezden gelebilirsiniz.",
    "paste_link": "Ya da bu bağlantıyı tarayıcınıza yapıştırın",
}
