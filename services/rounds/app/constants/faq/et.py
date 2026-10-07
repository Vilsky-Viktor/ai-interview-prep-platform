# The FAQ in et; the {placeholders} are filled in by helpers/help.py (faq_values) with
# billing's prices and the number of languages. Questions not translated yet show in English
# (constants/faq/__init__.py).
FAQ = [
    {
        "key": "what",
        "question": "Mis on prepza?",
        "answer": "Ajapiiranguga intervjuu sinu töökuulutuse põhjal, mis tahes rolli jaoks. Kasuta seda kandidaatide sõelumiseks enne, kui nendega kohtud, või värbamise omaette sammuna: mõlemal juhul näed, kes tööd päriselt tunneb.",
    },
    {
        "key": "roles",
        "question": "Milliste rollide jaoks saan värvata?",
        "answer": "Iga rolli jaoks, kus teadmised loevad: klienditugi, müük, rahandus, tervishoid, oskustööd, inseneeria, turundus ja palju muud. Kui oskad tööd kirjeldada, oskab prepza selle jaoks intervjuu teha.",
    },
    {
        "key": "hiring",
        "question": "Kuidas see töötab?",
        "answer": "Kleebi avalehele töökuulutus, anna oma ettevõttele nimi ja vaata üle teemad, mida prepza pakub. Seejärel kutsu kandidaadid: kirjuta nende e-posti aadressid, kleebi nimekiri või laadi üles fail. Kandidaadid, kes pole mõne päeva jooksul alustanud, saavad ühe meeldetuletuse. Iga kandidaat saab oma küsimused, igal küsimusel on ajapiirang, ja sa näed tema tulemust ning kõiki vastuseid kohe, kui ta lõpetab.",
    },
    {
        "key": "link",
        "question": "Kas saan intervjuu töökuulutusse panna?",
        "answer": "Jah. Lülita intervjuu vahekaardil Kandidaadid sisse jagatav link ja kleebi see oma kuulutusse. Igaüks, kes selle avab, logib sisse ja teeb intervjuu, ning iga inimese eest võetakse tasu nagu kutsutud kandidaadi eest. Link lülitub välja, kui märgid intervjuu palgatuks.",
    },
    {
        "key": "preview",
        "question": "Kas saan intervjuud proovida enne, kui kedagi kutsun?",
        "answer": "Jah. Ava oma intervjuu selle lehelt kandidaadina, tasuta: eelvaated ei ilmu sinu kandidaatide hulka ega küsimuste statistikasse. Võid teha ka ükskõik millise tasuta harjutusintervjuu.",
    },
    {
        "key": "cheating",
        "question": "Kas kandidaadid saavad kasutada tehisaru või vastuseid otsida?",
        "answer": "Iga kandidaat saab oma juhuslikud küsimused oma järjekorras ja igal küsimusel on ajapiirang, mida jälgib meie server, nii et vastuste otsimiseks või tehisarult küsimiseks jääb vähe aega. Kandidaadi tulemused näitavad ka, millal kandidaat lehelt lahkus, teksti kopeeris või vastas liiga kiiresti, et küsimust lugeda.",
    },
    {
        "key": "cost",
        "question": "Kui palju see maksab?",
        "answer": "Intervjuude loomine on tasuta. Iga kandidaat, kes vastab vähemalt ühele küsimusele, maksab {candidate} krediiti ({candidate_dollars} $), ja suuremate laadimiste krediitidega vähem, kuni 1 $. Sinu esimene ettevõte saab {company} tasuta krediiti, millest piisab tema esimese {company_candidates} kandidaadi jaoks. Hinnalehel on kõik hinnad.",
    },
    {
        "key": "charged",
        "question": "Millal kandidaadi eest tasu võetakse?",
        "answer": "Ainult siis, kui ta lõpetab intervjuu ja on vastanud vähemalt ühele küsimusele. Tema krediidid pannakse kõrvale, kui ta kutsud, ja tulevad tagasi, kui tühistad kutse, kui ta kunagi ei alusta või kui ta ei vasta millelegi.",
    },
    {
        "key": "compare_hiring",
        "question": "Kuidas hind võrdub teiste hindamisvahenditega?",
        "answer": "Paljusid hindamisvahendeid müüakse kuu- või aastatellimusena, mille eest maksad ka siis, kui kedagi ei testi. prepzas maksad ainult kandidaatide eest: {candidate} krediiti ({candidate_dollars} $) kandidaadi kohta, ilma lepingu, kasutajatasude ja intervjuu loomise tasuta. Ettevõte, kes kutsub {example_candidates} kandidaati kuus, maksab umbes {example_year_dollars} $ aastas. Kui testid igal kuul palju kandidaate, võib tellimus olla odavam, nii et võrdle oma numbritega.",
    },
    {
        "key": "expire",
        "question": "Kas krediidid aeguvad?",
        "answer": "Ei. Krediidid ei aegu kunagi ning tellimusi ega pikendamisi pole.",
    },
    {
        "key": "refunds",
        "question": "Kas saan raha tagasi?",
        "answer": "Jah, viimase 14 päeva jooksul ostetud ja kulutamata krediitide eest: Paddle'i kaudu või meile kirjutades. Tasuta krediite, näiteks tervituskingitust, ei hüvitata. Üksikasjad on tingimustes.",
    },
    {
        "key": "scorecards",
        "question": "Mida kandidaatide tulemused näitavad?",
        "answer": "Iga vastust, kas see oli õige ja kui kaua see aega võttis. Hinded on rohelised või punased vastavalt läbimise lävele, mille intervjuule määrasid. Tulemused märgivad ka vastused, mis anti liiga kiiresti, et küsimust lugeda, korrad, kui kandidaat lehelt lahkus, ja kopeerimiskatsed.",
    },
    {
        "key": "reports",
        "question": "Kas saan tulemusi värbamisjuhiga jagada?",
        "answer": "Jah. Laadi alla PDF-aruanne ühe kandidaadi või intervjuu kõigi kandidaatide kohta, saada see e-postiga otse prepzast või saada lühike kokkuvõte WhatsAppis või Telegramis.",
    },
    {
        "key": "candidates",
        "question": "Mida kandidaadid näevad?",
        "answer": "Sinu ettevõtte nime ja logo, enne alustamist seda, mida oodata, ja seejärel ühe ajapiiranguga küsimuse korraga. Nad ei näe kunagi oma tulemust ega seda, kas vastus oli õige.",
    },
    {
        "key": "verified",
        "question": "Mida kinnitusmärk tähendab?",
        "answer": "Seda, et ettevõtte omanik või administraator logis sisse ettevõtte veebilehe domeeni töömeiliga, näiteks you@acme.com, ja meie meeskond vaatas ettevõtte seejärel üle. Lisa veebileht oma ettevõtte päises nupuga Kinnita; tasuta e-postiteenused ei sobi. Kuni ülevaatus on ootel, näeb su meeskond nime kõrval kella, ja ettevõtte ümbernimetamine saadab selle uuesti ülevaatusele. Märk on näha ettevõtte nime kõrval, ka kutsetes.",
    },
    {
        "key": "languages",
        "question": "Milliseid keeli toetatakse?",
        "answer": "{count} keelt saidi, intervjuude ja e-kirjade jaoks. Vali, mis keeles intervjuu kirjutatakse, olenemata sellest, mis keeles on töökuulutus.",
    },
    {
        "key": "privacy",
        "question": "Mis saab töökuulutustest ja vastustest?",
        "answer": "Töökuulutusi kasutatakse sinu intervjuude loomiseks ja kandidaatide vastuseid nende hindamiseks, ainult sinu ettevõtte jaoks. Privaatsuspoliitika selgitab, mida me säilitame, kui kaua ja millised on kõigi õigused.",
    },
    {
        "key": "delete",
        "question": "Kas saan oma konto kustutada?",
        "answer": "Jah, seadetes. Sinu konto ja andmed kustutatakse ning enne seda saad oma andmetest koopia alla laadida.",
    },
]
