# Email texts in Turkish. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
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
    "reminder": {
        "subject": "Hatırlatma: {company} mülakatınızı bekliyor",
        "preheader": "“{title}” hâlâ açık. Başlamak için {email} ile giriş yapın.",
        "heading": "Mülakatınız sizi bekliyor",
        "lines": [
            (
                "{company} birkaç gün önce sizi prepza'daki “{title}” mülakatına davet etti "
                "ve henüz başlamadınız."
            ),
            (
                "Başlamak için {email} ile giriş yapın. Mülakata yalnızca bu adres katılabilir "
                "ve tek bir hakkınız var. Davet, gönderildikten 30 gün sonra geçerliliğini yitirir."
            ),
        ],
        "button": "Daveti aç",
    },
    "report": {
        "subject": "{sender} bir aday raporu paylaştı: {candidate}",
        "preheader": "{candidate}, {company} şirketinde “{title}” mülakatına girdi. Rapor ektedir.",
        "heading": "Aday raporu",
        "lines": [
            "{company} şirketinden {sender}, “{title}” mülakatı için {candidate} adlı adayın raporunu paylaştı.",
            (
                "Rapor tek sayfalık bir PDF olarak ektedir: genel not, her konunun puanı ve "
                "adayın tarayıcısının gösterdikleri. {sender} kişisine yanıt vermek için bu "
                "e-postayı yanıtlayın."
            ),
        ],
        "button": "prepza'yı ziyaret et",
        "footer": "Bu e-posta {email} adresine, {sender} prepza'da bu adresle bir aday raporu "
        "paylaştığı için gönderildi. Beklemiyorsanız görmezden gelebilirsiniz.",
    },
    "candidates": {
        "subject": "{sender} tüm adayların raporunu paylaştı: {title}",
        "preheader": "{company} şirketinde “{title}” için tüm adaylar. Rapor ektedir.",
        "heading": "Adaylar raporu",
        "lines": [
            "{company} şirketinden {sender}, “{title}” mülakatının tüm adaylarının raporunu paylaştı.",
            (
                "Rapor PDF olarak ektedir: her adayın notu, ilerlemesi ve tarayıcısının "
                "gösterdikleri, en iyiden başlayarak. {sender} kişisine yanıt vermek için bu "
                "e-postayı yanıtlayın."
            ),
        ],
        "button": "prepza'yı ziyaret et",
        "footer": "Bu e-posta {email} adresine, {sender} prepza'da bu adresle bir aday raporu "
        "paylaştığı için gönderildi. Beklemiyorsanız görmezden gelebilirsiniz.",
    },
    "footer": "Bu e-posta {email} adresine, biri bu adresi prepza'ya davet ettiği için "
    "gönderildi. Beklemiyorsanız görmezden gelebilirsiniz.",
    "paste_link": "Ya da bu bağlantıyı tarayıcınıza yapıştırın",
}
