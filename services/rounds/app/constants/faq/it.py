# The FAQ in it; the {placeholders} are filled in by helpers/help.py (faq_values) with
# billing's prices and the number of languages. Questions not translated yet show in English
# (constants/faq/__init__.py).
FAQ = [
    {
        "key": "what",
        "question": "Cos'è prepza?",
        "answer": "Un colloquio a tempo creato dalla tua descrizione del ruolo, per qualsiasi ruolo. Usalo per selezionare i candidati prima di incontrarli, o come fase vera e propria dell'assunzione: in entrambi i casi vedi chi conosce davvero il lavoro.",
    },
    {
        "key": "roles",
        "question": "Per quali ruoli posso assumere?",
        "answer": "Qualsiasi ruolo in cui contano le conoscenze: assistenza, vendite, finanza, sanità, mestieri tecnici, ingegneria, marketing e altro. Se puoi descrivere il lavoro, prepza può creare un colloquio per esso.",
    },
    {
        "key": "hiring",
        "question": "Come funziona?",
        "answer": "Incolla una descrizione del ruolo nella home page, indica il nome della tua azienda e controlla gli argomenti che propone prepza. Poi invita i candidati: scrivi le loro email, incolla un elenco o carica un file. I candidati che non hanno iniziato dopo qualche giorno ricevono un promemoria. Ogni candidato riceve domande tutte sue, ciascuna con un timer, e vedi il suo punteggio e ogni risposta appena finisce.",
    },
    {
        "key": "link",
        "question": "Posso mettere un colloquio in un annuncio di lavoro?",
        "answer": "Sì. Attiva il link condivisibile del colloquio nella sua scheda Candidati e incollalo nel tuo annuncio. Chiunque lo apra accede e svolge il colloquio, e ogni persona viene addebitata come un candidato invitato. Il link si disattiva quando segni il colloquio come assunto.",
    },
    {
        "key": "preview",
        "question": "Posso provare un colloquio prima di invitare qualcuno?",
        "answer": "Sì. Apri il tuo colloquio come candidato dalla sua pagina, gratis: le anteprime non compaiono tra i tuoi candidati né nelle statistiche delle domande. Puoi anche fare uno qualsiasi dei colloqui di pratica gratuiti.",
    },
    {
        "key": "cheating",
        "question": "I candidati possono usare l'IA o cercare le risposte?",
        "answer": "Ogni candidato riceve domande casuali tutte sue, in un ordine tutto suo, con un timer su ogni domanda gestito dal nostro server, quindi non c'è tempo per chiedere a un'IA. I risultati mostrano anche quando un candidato ha lasciato la pagina, copiato del testo o risposto troppo in fretta per aver letto la domanda.",
    },
    {
        "key": "cost",
        "question": "Quanto costa?",
        "answer": "Generare colloqui è gratis. Ogni candidato che risponde ad almeno una domanda costa {candidate} crediti ({candidate_dollars} $), e meno con i crediti di ricariche più grandi, fino a 1 $. La tua prima azienda riceve {company} crediti gratuiti, sufficienti per i suoi primi {company_candidates} candidati. La pagina dei prezzi elenca ogni prezzo.",
    },
    {
        "key": "charged",
        "question": "Quando viene addebitato un candidato?",
        "answer": "Solo quando termina il colloquio dopo aver risposto ad almeno una domanda. I suoi crediti vengono accantonati quando lo inviti e ti tornano se revochi l'invito, se non inizia mai o se non risponde a nulla.",
    },
    {
        "key": "compare_hiring",
        "question": "Come si confronta il prezzo con altri strumenti di valutazione?",
        "answer": "La maggior parte delle piattaforme di valutazione costa 100–215 $ al mese con piano annuale, oppure 7–20 $ per candidato. Con prepza un candidato costa {candidate} crediti ({candidate_dollars} $), senza contratto, senza costi per utente e senza pagare per generare un colloquio. Un’azienda che invita {example_candidates} candidati al mese paga circa {example_year_dollars} $ all’anno, contro 1.200–2.580 $ di un piano annuale. Da circa 50 candidati al mese, alcuni piani illimitati costano meno.",
    },
    {
        "key": "expire",
        "question": "I crediti scadono?",
        "answer": "No. I crediti non scadono mai, e non ci sono abbonamenti né rinnovi.",
    },
    {
        "key": "refunds",
        "question": "Posso avere un rimborso?",
        "answer": "Sì, per i crediti acquistati negli ultimi 14 giorni e non ancora spesi: tramite Paddle o scrivendoci. I crediti gratuiti, come il regalo di benvenuto, non sono rimborsabili. I termini riportano i dettagli.",
    },
    {
        "key": "scorecards",
        "question": "Cosa mostrano i risultati dei candidati?",
        "answer": "Ogni risposta, se era giusta e quanto tempo ha richiesto. I voti compaiono in verde o in rosso rispetto alla soglia che hai impostato per il colloquio. I risultati segnalano anche risposte troppo veloci per aver letto la domanda, le uscite dalla pagina e i tentativi di copia.",
    },
    {
        "key": "reports",
        "question": "Posso condividere i risultati con un responsabile delle assunzioni?",
        "answer": "Sì. Scarica un report PDF per un candidato o per tutti i candidati di un colloquio, invialo via email direttamente da prepza, oppure manda un breve riepilogo su WhatsApp o Telegram.",
    },
    {
        "key": "candidates",
        "question": "Cosa vedono i candidati?",
        "answer": "Il nome e il logo della tua azienda, cosa aspettarsi prima di iniziare, poi una domanda a tempo alla volta. Non vedono mai il punteggio né se una risposta era giusta.",
    },
    {
        "key": "talent",
        "question": "Cosa sono i suggerimenti di talenti?",
        "answer": "Le persone si esercitano sui colloqui di pratica gratuiti di prepza, e chi sceglie di essere suggerito lascia un link LinkedIn. Quando crei un colloquio, i migliori punteggi per un ruolo simile compaiono nella sua scheda Talenti suggeriti, con nome, punteggio e LinkedIn. Conta solo il loro primo tentativo, puoi nascondere chiunque non sia adatto, e i suggerimenti sono gratis.",
    },
    {
        "key": "verified",
        "question": "Cosa significa la spunta di verifica?",
        "answer": "Che un proprietario o un amministratore dell'azienda ha effettuato l'accesso con un'email di lavoro sul sito dell'azienda, ad esempio tu@acme.com. Aggiungi il sito con Verifica nell'intestazione della tua azienda; i servizi email gratuiti non contano. La spunta compare accanto al nome della tua azienda, anche negli inviti.",
    },
    {
        "key": "languages",
        "question": "Quali lingue sono supportate?",
        "answer": "{count} lingue, per il sito, i colloqui e le email. Scegli la lingua in cui è scritto un colloquio, qualunque sia la lingua della descrizione del ruolo.",
    },
    {
        "key": "privacy",
        "question": "Cosa succede alle descrizioni dei ruoli e alle risposte?",
        "answer": "Le descrizioni dei ruoli servono a creare i tuoi colloqui, e le risposte dei candidati a valutarli, solo per la tua azienda. L'informativa sulla privacy spiega cosa conserviamo, per quanto tempo e i diritti di ciascuno.",
    },
    {
        "key": "delete",
        "question": "Posso eliminare il mio account?",
        "answer": "Sì, nelle Impostazioni. Il tuo account e i tuoi dati vengono eliminati, e prima puoi scaricarne una copia.",
    },
]
