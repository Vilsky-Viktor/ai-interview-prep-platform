# The FAQ in fil; the {placeholders} are filled in by helpers/help.py (faq_values) with
# billing's prices and the number of languages. Questions not translated yet show in English
# (constants/faq/__init__.py).
FAQ = [
    {
        "key": "what",
        "question": "Ano ang prepza?",
        "answer": "Isang timed interview mula sa iyong job description, para sa kahit anong role. Gamitin ito para i-screen ang mga kandidato bago mo sila makilala, o bilang mismong hakbang ng hiring: alinman dito, makikita mo kung sino ang talagang marunong sa trabaho.",
    },
    {
        "key": "roles",
        "question": "Para sa aling mga role ako puwedeng mag-hire?",
        "answer": "Kahit anong role kung saan mahalaga ang kaalaman: support, sales, finance, healthcare, trades, engineering, marketing at iba pa. Kung kaya mong ilarawan ang trabaho, kayang gumawa ng prepza ng interview para dito.",
    },
    {
        "key": "hiring",
        "question": "Paano ito gumagana?",
        "answer": "Mag-paste ng job description sa home page, pangalanan ang iyong kumpanya at tingnan ang mga topic na iminumungkahi ng prepza. Pagkatapos ay mag-imbita ng mga kandidato: i-type ang kanilang mga email, mag-paste ng listahan o mag-upload ng file. Ang mga kandidatong hindi pa nagsisimula pagkalipas ng ilang araw ay makakatanggap ng isang paalala. Bawat kandidato ay may sariling mga tanong at timer sa bawat isa, at makikita mo ang kanilang score at bawat sagot sa sandaling matapos sila.",
    },
    {
        "key": "link",
        "question": "Puwede ko bang ilagay ang interview sa isang job ad?",
        "answer": "Oo. I-on ang shareable link ng interview sa tab nitong Mga kandidato at i-paste ito sa iyong ad. Ang sinumang magbukas nito ay magsa-sign in at sasagot sa interview, at sinisingil ang bawat tao tulad ng isang inimbitahang kandidato. Mag-o-off ang link kapag minarkahan mo ang interview bilang na-hire.",
    },
    {
        "key": "preview",
        "question": "Puwede ko bang subukan ang interview bago mag-imbita ng kahit sino?",
        "answer": "Oo. Buksan ang iyong interview bilang kandidato mula sa page nito, nang libre: hindi lumalabas ang mga preview sa iyong mga kandidato o sa statistics ng mga tanong. Puwede mo ring sagutan ang alinman sa mga libreng practice interview.",
    },
    {
        "key": "cheating",
        "question": "Puwede bang gumamit ng AI ang mga kandidato o hanapin ang mga sagot?",
        "answer": "Bawat kandidato ay may sariling random na mga tanong sa sarili nilang pagkakasunod-sunod, may timer sa bawat tanong na binabantayan ng aming server, kaya kaunti lang ang oras para maghanap ng sagot o magtanong sa AI. Ipinapakita rin ng mga resulta ng kandidato kung kailan umalis ang kandidato sa page, kumopya ng text, o sumagot nang masyadong mabilis para nabasa ang tanong.",
    },
    {
        "key": "cost",
        "question": "Magkano ito?",
        "answer": "Libre ang paggawa ng interview. Bawat kandidatong sumagot ng kahit isang tanong ay {candidate} credits (${candidate_dollars}), at mas mura gamit ang credits mula sa mas malalaking top-up, hanggang $1. Makakatanggap ang iyong unang kumpanya ng {company} libreng credits, sapat para sa unang {company_candidates} kandidato nito. Nakalista sa pricing page ang bawat presyo.",
    },
    {
        "key": "charged",
        "question": "Kailan sinisingil ang isang kandidato?",
        "answer": "Kapag natapos lang nila ang interview nang nakasagot ng kahit isang tanong. Itinatabi ang kanilang credits kapag inimbitahan mo sila, at ibinabalik kung babawiin mo ang imbitasyon, kung hindi sila kailanman nagsimula, o kung wala silang sinagot.",
    },
    {
        "key": "compare_hiring",
        "question": "Paano maihahambing ang presyo sa ibang assessment tool?",
        "answer": "Karamihan sa mga assessment platform ay $100–215 kada buwan sa annual plan, o $7–20 bawat kandidato. Sa prepza, ang isang kandidato ay {candidate} credits (${candidate_dollars}), walang kontrata, walang bayad kada user, at walang bayad sa paggawa ng interview. Ang kumpanyang nag-iimbita ng {example_candidates} kandidato kada buwan ay nagbabayad ng mga ${example_year_dollars} kada taon, kumpara sa $1,200–2,580 para sa annual plan. Mula mga 50 kandidato kada buwan, may ilang unlimited plan na mas mura.",
    },
    {
        "key": "expire",
        "question": "Nag-e-expire ba ang credits?",
        "answer": "Hindi. Hindi kailanman nag-e-expire ang credits, at walang subscription o renewal.",
    },
    {
        "key": "refunds",
        "question": "Puwede ba akong ma-refund?",
        "answer": "Oo, para sa credits na binili mo sa nakaraang 14 na araw at hindi pa nagagastos: sa Paddle o sa pagsulat sa amin. Hindi nire-refund ang libreng credits, gaya ng welcome gift. Nasa terms ang mga detalye.",
    },
    {
        "key": "scorecards",
        "question": "Ano ang ipinapakita ng mga resulta ng kandidato?",
        "answer": "Bawat sagot, kung tama ito at gaano katagal ito. Berde o pula ang mga grado batay sa passing grade na itinakda mo para sa interview. Nagfa-flag din ang mga resulta ng mga sagot na masyadong mabilis para nabasa ang tanong, mga pagkakataong umalis ang kandidato sa page, at mga pagtatangkang mangopya.",
    },
    {
        "key": "reports",
        "question": "Puwede ko bang i-share ang mga resulta sa isang hiring manager?",
        "answer": "Oo. Mag-download ng PDF report para sa isang kandidato o para sa lahat ng kandidato ng isang interview, i-email ito direkta mula sa prepza, o magpadala ng maikling buod sa WhatsApp o Telegram.",
    },
    {
        "key": "candidates",
        "question": "Ano ang nakikita ng mga kandidato?",
        "answer": "Ang pangalan at logo ng iyong kumpanya, kung ano ang aasahan bago sila magsimula, pagkatapos ay isang timed na tanong sa bawat pagkakataon. Hindi nila kailanman nakikita ang kanilang score o kung tama ang isang sagot.",
    },
    {
        "key": "verified",
        "question": "Ano ang ibig sabihin ng verified check?",
        "answer": "Na nag-sign in ang isang owner o admin ng kumpanya gamit ang work email sa website ng kumpanya, gaya ng you@acme.com, at sinuri ng aming team ang kumpanya pagkatapos. Idagdag ang website gamit ang I-verify sa header ng iyong kumpanya; hindi binibilang ang mga libreng email service. Habang naghihintay ng review, may orasan sa tabi ng pangalan na nakikita ng iyong team, at ang pagpapalit ng pangalan ng kumpanya ay nagpapadala ulit nito para sa review. Lumalabas ang check sa tabi ng pangalan ng iyong kumpanya, pati sa mga invite.",
    },
    {
        "key": "languages",
        "question": "Aling mga wika ang suportado?",
        "answer": "{count} wika, para sa site, sa mga interview at sa mga email. Piliin ang wika ng interview, anuman ang wika ng job description.",
    },
    {
        "key": "privacy",
        "question": "Ano ang nangyayari sa mga job description at mga sagot?",
        "answer": "Ginagamit ang mga job description para buuin ang iyong mga interview, at ang mga sagot ng kandidato para i-score ang mga ito, para sa iyong kumpanya lang. Ipinapaliwanag ng privacy policy kung ano ang itinatago namin, gaano katagal, at ang mga karapatan ng lahat.",
    },
    {
        "key": "delete",
        "question": "Puwede ko bang burahin ang account ko?",
        "answer": "Oo, sa Settings. Buburahin ang account at data mo, at puwede mo munang i-download ang kopya ng data mo.",
    },
]
