# Email texts in Turkish. Values are filled in with str.format; the HTML version escapes them.

# The footer of reminders to a company's owners and admins.
MEMBER_FOOTER = (
    "Bu e-posta {email} adresine, prepza'da bir şirketin sahibi veya yöneticisi olduğunuz "
    "için gönderildi."
)

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
        "subject": "Aday raporu: {candidate}",
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
        "subject": "Tüm adayların raporu: {title}",
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
    "digest": {
        "subject": "prepza etkinlik özetiniz",
        "preheader": "Son 24 saatte şirketlerinizde olanlar.",
        "heading": "Etkinlik özetiniz",
        "lines": [
            "Son 24 saatte prepza'daki şirketlerinizde olanlar şunlar.",
        ],
        "rows": {
            "candidate_finished": "Mülakatı tamamlayan adaylar: {count} · “{title}”",
            "invite_undelivered": "İletilemeyen davetler: {count} · “{title}”",
            "ats_not_invited": "Davet edilmeyen ATS adayları: {count}",
            "interview_ready": "Hazır mülakat: “{title}”",
        },
        "button": "prepza'yı aç",
        "footer": (
            "Bu e-posta {email} adresine, prepza'da bir şirketin üyesi olduğunuz ve "
            "etkinlik özetini aldığınız için gönderildi."
        ),
    },
    "low_credits": {
        "subject": "Kredileriniz azalıyor",
        "preheader": "Aday davet etmeye devam etmek için kredi yükleyin.",
        "heading": "Krediler azalıyor",
        "lines": [
            (
                "Bu şirketlerin bir aday daha davet etmeye yetecek kredisi yok. Aday davet "
                "etmeye devam etmek için kredi yükleyin."
            ),
        ],
        "rows": {
            "company": "{company} · kullanılabilir kredi: {available}",
        },
        "button": "Kredi yükle",
        "footer": MEMBER_FOOTER,
    },
    "no_candidates": {
        "subject": "Adaylar bekleniyor",
        "preheader": "Adayları e-postayla davet edin veya mülakatın bağlantısını paylaşın.",
        "heading": "Adaylar bekleniyor",
        "lines": [
            (
                "Bu mülakatlar birkaç gündür hazır, ancak henüz kimse davet edilmedi. "
                "Adayları e-postayla davet edin veya mülakatın bağlantısını paylaşın."
            ),
        ],
        "rows": {
            "interview": "“{title}” · {company}",
        },
        "button": "Adayları davet et",
        "footer": MEMBER_FOOTER,
    },
    "review_waiting": {
        "subject": "Konularınız incelemenizi bekliyor",
        "preheader": "Konuları onaylayın, sorular oluşturulsun.",
        "heading": "Konularınızı inceleyin",
        "lines": [
            (
                "Başlattığınız mülakatların konuları incelemenizi bekliyor. Onayladığınızda"
                " sorular oluşturulur. 14 gün açık kalan bir inceleme iptal edilir."
            ),
        ],
        "rows": {
            "interview": "{company} · bekleme süresi (gün): {days}",
        },
        "button": "Konuları incele",
        "footer": MEMBER_FOOTER,
    },
    "top_up_failed": {
        "subject": "{company} için otomatik yükleme başarısız oldu",
        "preheader": "Karttan ödeme alınamadı. Aday davet etmeye devam etmek için kredi yükleyin.",
        "heading": "Otomatik yükleme başarısız oldu",
        "lines": [
            "Otomatik yükleme {company} için karttan ödeme alamadı, bu yüzden kredi eklenmedi.",
            (
                "Aday davet etmeye devam etmek için kredi yükleyin. Otomatik yükleme kartı "
                "daha sonra yeniden deneyecek."
            ),
        ],
        "button": "Kredi yükle",
        "footer": (
            "Bu e-posta {email} adresine, prepza'da {company} şirketinin sahibi veya "
            "yöneticisi olduğunuz için gönderildi. Şirketinizin faturalandırmasıyla ilgili "
            "olduğundan e-posta ayarlarınızdan bağımsız olarak gönderilir."
        ),
    },
    "footer": "Bu e-posta {email} adresine, biri bu adresi prepza'ya davet ettiği için "
    "gönderildi. Beklemiyorsanız görmezden gelebilirsiniz.",
    "paste_link": "Ya da bu bağlantıyı tarayıcınıza yapıştırın",
    # The footer's links: optional emails' unsubscribe and settings, and a candidate's own.
    "unsubscribe": "Abonelikten çık",
    "email_settings": "E-posta ayarlarını değiştir",
    "stop_reminders": "Bu mülakat için bana hatırlatma gönderme",
    "stop_company": "{company} adına bana e-posta gönderme",
}
