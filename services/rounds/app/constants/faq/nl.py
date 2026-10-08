# The FAQ in nl; the {placeholders} are filled in by helpers/help.py (faq_values) with
# billing's prices and the number of languages. Questions not translated yet show in English
# (constants/faq/__init__.py).
FAQ = [
    {
        "key": "what",
        "question": "Wat is prepza?",
        "answer": "Een interview met tijdslimiet, gemaakt op basis van je functieomschrijving, voor elke functie. Gebruik het om kandidaten te screenen voordat je ze ontmoet, of als stap in de werving zelf: hoe dan ook zie je wie het vak echt kent.",
    },
    {
        "key": "roles",
        "question": "Voor welke functies kan ik werven?",
        "answer": "Elke functie waarin kennis telt: support, sales, financiën, zorg, technische vakken, engineering, marketing en meer. Als je de functie kunt beschrijven, kan prepza er een interview voor maken.",
    },
    {
        "key": "hiring",
        "question": "Hoe werkt het?",
        "answer": "Plak een functieomschrijving op de startpagina, geef je bedrijf een naam en controleer de onderwerpen die prepza voorstelt. Nodig daarna kandidaten uit: typ hun e-mailadressen, plak een lijst of upload een bestand. Kandidaten die na een paar dagen nog niet zijn begonnen, krijgen één herinnering. Elke kandidaat krijgt eigen vragen met een timer bij elke vraag, en je ziet hun score en elk antwoord zodra ze klaar zijn.",
    },
    {
        "key": "link",
        "question": "Kan ik een interview in een vacature zetten?",
        "answer": "Ja. Zet de deelbare link van het interview aan op het tabblad met kandidaten en plak hem in je vacature. Iedereen die hem opent, logt in en doet het interview, en je betaalt per persoon hetzelfde als voor een uitgenodigde kandidaat. De link gaat uit wanneer je het interview markeert als aangenomen.",
    },
    {
        "key": "preview",
        "question": "Kan ik een interview proberen voordat ik iemand uitnodig?",
        "answer": "Ja. Open je interview gratis als kandidaat vanaf de pagina ervan: voorbeelden verschijnen niet tussen je kandidaten of in de vraagstatistieken. Je kunt ook elk gratis oefeninterview doen.",
    },
    {
        "key": "cheating",
        "question": "Kunnen kandidaten AI gebruiken of de antwoorden opzoeken?",
        "answer": "Elke kandidaat krijgt eigen willekeurige vragen in een eigen volgorde, met een timer bij elke vraag die onze server bijhoudt, dus er is weinig tijd om antwoorden op te zoeken of het een AI te vragen. De resultaten laten ook zien wanneer een kandidaat de pagina verliet, tekst kopieerde of te snel antwoordde om de vraag te hebben gelezen.",
    },
    {
        "key": "cost",
        "question": "Wat kost het?",
        "answer": "Interviews genereren is gratis. Elke kandidaat die minstens één vraag beantwoordt, kost {candidate} credits ({candidate_dollars} $), en minder met credits uit grotere opwaarderingen, tot 1 $. Je eerste bedrijf krijgt {company} gratis credits, genoeg voor de eerste {company_candidates} kandidaten. De prijzenpagina toont elke prijs.",
    },
    {
        "key": "charged",
        "question": "Wanneer wordt er voor een kandidaat betaald?",
        "answer": "Alleen wanneer de kandidaat het interview afrondt en minstens één vraag heeft beantwoord. De credits worden gereserveerd wanneer je iemand uitnodigt en komen terug als je de uitnodiging intrekt, als de kandidaat nooit begint of niets beantwoordt.",
    },
    {
        "key": "compare_hiring",
        "question": "Hoe verhoudt de prijs zich tot andere assessmenttools?",
        "answer": "Veel assessmenttools worden verkocht als maand- of jaarabonnement, dat je ook betaalt als je niemand test. Bij prepza betaal je alleen per kandidaat: {candidate} credits ({candidate_dollars} $), zonder contract, zonder kosten per gebruiker en zonder te betalen voor het maken van een interview. Een bedrijf dat {example_candidates} kandidaten per maand uitnodigt, betaalt ongeveer {example_year_dollars} $ per jaar. Test je elke maand veel kandidaten, dan kan een abonnement goedkoper zijn, dus vergelijk met je eigen cijfers.",
    },
    {
        "key": "expire",
        "question": "Verlopen credits?",
        "answer": "Nee. Credits verlopen nooit, en er zijn geen abonnementen of verlengingen.",
    },
    {
        "key": "refunds",
        "question": "Kan ik mijn geld terugkrijgen?",
        "answer": "Ja, voor credits die je de afgelopen 14 dagen hebt gekocht en nog niet hebt besteed: via Paddle of door ons te schrijven. Gratis credits, zoals het welkomstcadeau, worden niet terugbetaald. De voorwaarden geven de details.",
    },
    {
        "key": "scorecards",
        "question": "Wat laat een scorekaart zien?",
        "answer": "Elk antwoord, of het goed was en hoe lang het duurde. Scores zijn groen of rood ten opzichte van de slaaggrens die je voor het interview hebt ingesteld. De scorekaart markeert ook antwoorden die te snel waren om de vraag te hebben gelezen, keren dat de kandidaat de pagina verliet, en kopieerpogingen.",
    },
    {
        "key": "reports",
        "question": "Kan ik resultaten delen met een hiring manager?",
        "answer": "Ja. Download een PDF-rapport voor één kandidaat of voor alle kandidaten van een interview, mail het rechtstreeks vanuit prepza, of stuur een korte samenvatting via WhatsApp, Telegram, Viber of LINE.",
    },
    {
        "key": "integrations",
        "question": "Werkt prepza met mijn ATS of andere tools?",
        "answer": "Ja, zonder extra kosten. Koppel Workable, Greenhouse, Teamtailor, Recruitee of Breezy HR op het tabblad Integraties van je bedrijf: kandidaten die je naar een fase verplaatst, krijgen het interview, en hun resultaten gaan terug naar het ATS. Slack kan de meldingen van je bedrijf in een kanaal plaatsen, en met de API kan je eigen platform kandidaten uitnodigen en hun resultaten ontvangen; zie de API-documentatie.",
    },
    {
        "key": "candidates",
        "question": "Wat zien kandidaten?",
        "answer": "De naam en het logo van je bedrijf, wat ze kunnen verwachten voordat ze beginnen, en daarna één vraag met tijdslimiet tegelijk. Ze zien nooit hun score of of een antwoord goed was.",
    },
    {
        "key": "verified",
        "question": "Wat betekent het verificatievinkje?",
        "answer": "Dat een eigenaar of beheerder van het bedrijf heeft ingelogd met een zakelijk e-mailadres op de website van het bedrijf, zoals you@acme.com, en dat ons team het bedrijf daarna heeft beoordeeld. Voeg de website toe met Verifiëren in de kop van je bedrijf; gratis e-maildiensten tellen niet mee. Zolang de beoordeling loopt, ziet je team een klokje naast de naam, en een nieuwe bedrijfsnaam stuurt het opnieuw ter beoordeling. Het vinkje staat naast de naam van je bedrijf, ook in uitnodigingen.",
    },
    {
        "key": "languages",
        "question": "Welke talen worden ondersteund?",
        "answer": "{count} talen, voor de site, de interviews en de e-mails. Kies de taal waarin een interview wordt geschreven, in welke taal de functieomschrijving ook is.",
    },
    {
        "key": "privacy",
        "question": "Wat gebeurt er met functieomschrijvingen en antwoorden?",
        "answer": "Functieomschrijvingen worden gebruikt om je interviews te maken, en de antwoorden van kandidaten om ze te beoordelen, alleen voor jouw bedrijf. Het privacybeleid legt uit wat we bewaren, hoe lang en welke rechten iedereen heeft.",
    },
    {
        "key": "delete",
        "question": "Kan ik mijn account verwijderen?",
        "answer": "Ja, in Instellingen. Je account en je gegevens worden verwijderd, en vooraf kun je een kopie van je gegevens downloaden.",
    },
]
