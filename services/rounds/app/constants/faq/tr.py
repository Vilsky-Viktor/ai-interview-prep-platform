# The FAQ in tr; the {placeholders} are filled in by helpers/help.py (faq_values) with
# billing's prices and the number of languages. Questions not translated yet show in English
# (constants/faq/__init__.py).
FAQ = [
    {
        "key": "what",
        "question": "prepza nedir?",
        "answer": "İş tanımınızdan hazırlanan, her pozisyon için süreli bir mülakat. Adayları onlarla tanışmadan önce elemek için ya da işe alımın bir adımı olarak kullanın: her iki durumda da işi gerçekten kimin bildiğini görürsünüz.",
    },
    {
        "key": "roles",
        "question": "Hangi pozisyonlar için işe alım yapabilirim?",
        "answer": "Bilginin önemli olduğu her pozisyon için: destek, satış, finans, sağlık, zanaat ve teknik meslekler, mühendislik, pazarlama ve daha fazlası. İşi tarif edebiliyorsanız prepza onun için bir mülakat hazırlayabilir.",
    },
    {
        "key": "hiring",
        "question": "Nasıl çalışır?",
        "answer": "Ana sayfaya bir iş tanımı yapıştırın, şirketinize ad verin ve prepza'nın önerdiği konuları kontrol edin. Ardından adayları davet edin: e-postalarını yazın, bir liste yapıştırın ya da dosya yükleyin. Birkaç gün içinde başlamayan adaylara bir hatırlatma gider. Her aday kendi sorularını alır ve her sorunun bir süresi vardır; adaylar bitirir bitirmez puanlarını ve tüm cevaplarını görürsünüz.",
    },
    {
        "key": "link",
        "question": "Bir mülakatı iş ilanına koyabilir miyim?",
        "answer": "Evet. Mülakatın Adaylar sekmesinden paylaşılabilir bağlantısını açın ve ilanınıza yapıştırın. Bağlantıyı açan herkes giriş yapar ve mülakata girer; her kişi, davet edilen bir aday gibi ücretlendirilir. Mülakatı İşe alındı olarak işaretlediğinizde bağlantı kapanır.",
    },
    {
        "key": "preview",
        "question": "Kimseyi davet etmeden önce bir mülakatı deneyebilir miyim?",
        "answer": "Evet. Mülakatınızı kendi sayfasından ücretsiz olarak aday gibi açın: önizlemeler adaylarınız arasında ya da soru istatistiklerinde görünmez. Ücretsiz pratik mülakatlardan herhangi birine de girebilirsiniz.",
    },
    {
        "key": "cheating",
        "question": "Adaylar yapay zekâ kullanabilir ya da cevapları arayabilir mi?",
        "answer": "Her aday kendi sırasında kendi rastgele sorularını alır ve her sorunun sunucumuzun tuttuğu bir süresi vardır, bu yüzden cevapları aramaya ya da yapay zekâya sormaya pek zaman kalmaz. Değerlendirme kartı ayrıca adayın sayfadan ne zaman ayrıldığını, metin kopyaladığını ya da soruyu okumuş olamayacak kadar hızlı cevap verdiğini gösterir.",
    },
    {
        "key": "cost",
        "question": "Ücreti ne kadar?",
        "answer": "Mülakat oluşturmak ücretsizdir. En az bir soruyu cevaplayan her aday {candidate} kredi ({candidate_dollars} $) tutar; daha büyük yüklemelerden gelen kredilerle daha az, 1 $'a kadar. İlk şirketiniz {company} ücretsiz kredi alır; bu, ilk {company_candidates} adayı için yeterlidir. Fiyatlar sayfasında tüm fiyatlar yer alır.",
    },
    {
        "key": "charged",
        "question": "Bir aday için ne zaman ücret alınır?",
        "answer": "Yalnızca en az bir soruyu cevaplayıp mülakatı bitirdiğinde. Krediler, adayı davet ettiğinizde ayrılır; daveti geri alırsanız, aday hiç başlamazsa ya da hiçbir şeyi cevaplamazsa geri gelir.",
    },
    {
        "key": "compare_hiring",
        "question": "Fiyat, diğer değerlendirme araçlarıyla nasıl karşılaştırılır?",
        "answer": "Birçok değerlendirme aracı, kimseyi test etmeseniz bile ödediğiniz aylık veya yıllık abonelikle satılır. prepza'da yalnızca aday başına ödersiniz: {candidate} kredi ({candidate_dollars} $); sözleşme, kullanıcı başı ücret ve mülakat oluşturma ücreti yoktur. Ayda {example_candidates} aday davet eden bir şirket yılda yaklaşık {example_year_dollars} $ öder. Her ay çok sayıda aday test ediyorsanız bir abonelik daha ucuz olabilir; kendi rakamlarınızla karşılaştırın.",
    },
    {
        "key": "expire",
        "question": "Kredilerin süresi dolar mı?",
        "answer": "Hayır. Kredilerin süresi asla dolmaz; ücretli abonelik yoktur. İsteğe bağlı otomatik yüklemeyi açarsanız Paddle kartınızı 0 $'lık bir abonelik olarak kaydeder; yalnızca yapılan yüklemeler için ödersiniz.",
    },
    {
        "key": "refunds",
        "question": "Para iadesi alabilir miyim?",
        "answer": "Evet, son 14 gün içinde satın aldığınız ve harcamadığınız krediler için: Paddle üzerinden veya bize yazarak. Hoş geldin hediyesi gibi ücretsiz krediler iade edilmez. Ayrıntılar koşullarda yer alır.",
    },
    {
        "key": "scorecards",
        "question": "Değerlendirme kartları neleri gösterir?",
        "answer": "Her cevabı, doğru olup olmadığını ve ne kadar sürdüğünü. Notlar, mülakat için belirlediğiniz geçme notuna göre yeşil ya da kırmızı görünür. Değerlendirme kartı ayrıca okunamayacak kadar hızlı verilen cevapları, adayın sayfadan ayrıldığı anları ve kopyalama girişimlerini işaretler.",
    },
    {
        "key": "reports",
        "question": "Sonuçları işe alım yöneticisiyle paylaşabilir miyim?",
        "answer": "Evet. Tek bir aday ya da bir mülakatın tüm adayları için PDF raporu indirin, doğrudan prepza'dan e-postayla gönderin ya da WhatsApp, Telegram, Viber veya LINE'da kısa bir özet gönderin.",
    },
    {
        "key": "integrations",
        "question": "prepza, ATS'imle veya diğer araçlarla çalışır mı?",
        "answer": "Evet, ek ücret olmadan. Workable, Greenhouse, Teamtailor, Recruitee veya Breezy HR'ı şirketinizin Entegrasyonlar sekmesinden bağlayın: bir aşamaya taşıdığınız adaylar mülakatı alır ve sonuçları ATS'ye geri gönderilir. Slack, şirketinizin bildirimlerini bir kanala gönderebilir; API ise kendi platformunuzun adayları davet etmesini ve sonuçlarını almasını sağlar. Ayrıntılar için API belgeleri sayfasına bakın.",
    },
    {
        "key": "ai_apps",
        "question": "prepza'yı Claude veya ChatGPT'den kullanabilir miyim?",
        "answer": "Evet. prepza'yı Claude veya ChatGPT'ye bağlayıcı olarak ekleyin (adımlar şirketinizin Entegrasyonlar sekmesinde) ve prepza'da izin verin. Uygulama bundan sonra sizin adınıza ve sizin yetkilerinizle şirketleriniz, mülakatlarınız ve adayların sonuçlarıyla çalışır ve bir şeyi değiştirmeden önce size sorar. Hesabınızı veya bir şirketi yalnızca prepza'da silebilirsiniz. Uygulamanın okuduğu veriler, o uygulamanın koşullarına göre sağlayıcısına ulaşır. Bağlantıyı istediğiniz zaman aynı sekmeden kesebilirsiniz.",
    },
    {
        "key": "candidates",
        "question": "Adaylar ne görür?",
        "answer": "Şirketinizin adını ve logosunu, başlamadan önce neyle karşılaşacaklarını, ardından her seferinde bir süreli soru. Puanlarını ya da bir cevabın doğru olup olmadığını asla görmezler.",
    },
    {
        "key": "verified",
        "question": "Doğrulandı işareti ne anlama gelir?",
        "answer": "Şirketin bir sahibinin ya da yöneticisinin, şirketin web sitesine ait bir iş e-postasıyla (ör. you@acme.com) giriş yaptığı ve ardından ekibimizin şirketi incelediği anlamına gelir. Web sitesini şirketinizin başlığındaki Doğrula ile ekleyin; ücretsiz e-posta servisleri sayılmaz. İnceleme beklerken ekibiniz adın yanında bir saat görür; şirketin adını değiştirmek onu yeniden incelemeye gönderir. İşaret, davetler dahil şirketinizin adının yanında görünür.",
    },
    {
        "key": "languages",
        "question": "Hangi diller destekleniyor?",
        "answer": "Site, mülakatlar ve e-postalar için {count} dil. İş tanımı hangi dilde olursa olsun, mülakatın hangi dilde yazılacağını siz seçersiniz.",
    },
    {
        "key": "privacy",
        "question": "İş tanımları ve cevaplara ne olur?",
        "answer": "İş tanımları mülakatlarınızı hazırlamak, adayların cevapları ise onları puanlamak için yalnızca şirketiniz adına kullanılır. Gizlilik politikası neleri, ne kadar süre sakladığımızı ve herkesin haklarını açıklar.",
    },
    {
        "key": "emails",
        "question": "prepza hangi e-postaları gönderir ve bunları nasıl durdururum?",
        "answer": 'Davetler, raporlar, ödeme sorunları ve koşullarımızdaki değişiklikler gibi hizmet e-postaları her zaman gönderilir. Günlük etkinlik özeti, hatırlatmalar ve ürün güncellemeleri gibi diğerlerini Ayarlar\'da, E-postalar bölümünde seçebilir ya da her e-postadaki "Abonelikten çık" bağlantısıyla durdurabilirsiniz. Adaylar, davet ve hatırlatma e-postalarındaki bağlantılarla şirketinizin e-postalarını ya da bir mülakatın hatırlatmalarını durdurabilir.',
    },
    {
        "key": "delete",
        "question": "Hesabımı silebilir miyim?",
        "answer": "Evet, Ayarlar'dan. Hesabınız ve verileriniz silinir; öncesinde verilerinizin bir kopyasını indirebilirsiniz.",
    },
]
