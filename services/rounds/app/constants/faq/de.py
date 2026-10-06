# The FAQ in de; the {placeholders} are filled in by helpers/help.py (faq_values) with
# billing's prices and the number of languages. Questions not translated yet show in English
# (constants/faq/__init__.py).
FAQ = [
    {
        "key": "what",
        "question": "Was ist prepza?",
        "answer": "Ein Interview mit Zeitlimit, erstellt aus deiner Stellenbeschreibung, für jede Rolle. Nutze es, um Kandidaten zu prüfen, bevor du sie triffst, oder als eigenen Schritt im Einstellungsprozess: So oder so siehst du, wer den Job wirklich beherrscht.",
    },
    {
        "key": "roles",
        "question": "Für welche Rollen kann ich einstellen?",
        "answer": "Für jede Rolle, in der Wissen zählt: Support, Vertrieb, Finanzen, Gesundheitswesen, Handwerk, Technik, Marketing und mehr. Wenn du den Job beschreiben kannst, kann prepza ein Interview dafür erstellen.",
    },
    {
        "key": "hiring",
        "question": "Wie funktioniert es?",
        "answer": "Füge auf der Startseite eine Stellenbeschreibung ein, gib den Namen deines Unternehmens an und prüfe die Themen, die prepza vorschlägt. Dann lade Kandidaten ein: Tippe ihre E-Mail-Adressen ein, füge eine Liste ein oder lade eine Datei hoch. Kandidaten, die nach ein paar Tagen noch nicht angefangen haben, bekommen eine Erinnerung. Jeder Kandidat bekommt eigene Fragen mit einem Zeitlimit für jede, und du siehst sein Ergebnis und jede Antwort, sobald er fertig ist.",
    },
    {
        "key": "link",
        "question": "Kann ich ein Interview in eine Stellenanzeige setzen?",
        "answer": "Ja. Schalte den teilbaren Link des Interviews im Tab Kandidaten ein und füge ihn in deine Anzeige ein. Jeder, der ihn öffnet, meldet sich an und macht das Interview, und jede Person wird wie ein eingeladener Kandidat berechnet. Der Link wird abgeschaltet, wenn du das Interview als eingestellt markierst.",
    },
    {
        "key": "preview",
        "question": "Kann ich ein Interview ausprobieren, bevor ich jemanden einlade?",
        "answer": "Ja. Öffne dein Interview über seine Seite als Kandidat, kostenlos: Vorschauen erscheinen weder bei deinen Kandidaten noch in der Fragenstatistik. Du kannst auch jedes der kostenlosen Übungsinterviews machen.",
    },
    {
        "key": "cheating",
        "question": "Können Kandidaten KI nutzen oder die Antworten nachschlagen?",
        "answer": "Jeder Kandidat bekommt eigene, zufällige Fragen in eigener Reihenfolge, mit einem Zeitlimit für jede Frage, das unser Server überwacht, also bleibt wenig Zeit, Antworten nachzuschlagen oder eine KI zu fragen. Die Auswertung zeigt außerdem, wann ein Kandidat die Seite verlassen, Text kopiert oder zu schnell geantwortet hat, um die Frage gelesen zu haben.",
    },
    {
        "key": "cost",
        "question": "Was kostet es?",
        "answer": "Interviews zu generieren ist kostenlos. Jeder Kandidat, der mindestens eine Frage beantwortet, kostet {candidate} Credits ({candidate_dollars} $), mit Credits aus größeren Aufladungen weniger, bis hinunter auf 1 $. Dein erstes Unternehmen bekommt {company} kostenlose Credits, genug für seine ersten {company_candidates} Kandidaten. Auf der Preisseite stehen alle Preise.",
    },
    {
        "key": "charged",
        "question": "Wann wird ein Kandidat berechnet?",
        "answer": "Nur wenn er das Interview beendet und dabei mindestens eine Frage beantwortet hat. Seine Credits werden bei der Einladung zurückgelegt und kommen zurück, wenn du die Einladung widerrufst, wenn er nie anfängt oder wenn er nichts beantwortet.",
    },
    {
        "key": "compare_hiring",
        "question": "Wie ist der Preis im Vergleich zu anderen Bewertungstools?",
        "answer": "Die meisten Plattformen für Eignungstests kosten 100–215 $ im Monat im Jahresabo oder 7–20 $ pro Kandidat. Bei prepza kostet ein Kandidat {candidate} Credits ({candidate_dollars} $), ohne Vertrag, ohne Gebühren pro Nutzer und ohne Kosten für das Generieren eines Interviews. Ein Unternehmen, das {example_candidates} Kandidaten im Monat einlädt, zahlt etwa {example_year_dollars} $ im Jahr, gegenüber 1.200–2.580 $ für ein Jahresabo. Ab etwa 50 Kandidaten im Monat können manche Flatrates günstiger sein.",
    },
    {
        "key": "expire",
        "question": "Verfallen Credits?",
        "answer": "Nein. Credits verfallen nie, und es gibt keine Abos oder Verlängerungen.",
    },
    {
        "key": "refunds",
        "question": "Kann ich mein Geld zurückbekommen?",
        "answer": "Ja, für Credits, die du in den letzten 14 Tagen gekauft und noch nicht ausgegeben hast: über Paddle oder indem du uns schreibst. Gratis-Credits wie das Willkommensgeschenk werden nicht erstattet. Details stehen in den Bedingungen.",
    },
    {
        "key": "scorecards",
        "question": "Was zeigen die Auswertungen?",
        "answer": "Jede Antwort, ob sie richtig war und wie lange sie gedauert hat. Noten erscheinen grün oder rot, gemessen an der Bestehensgrenze, die du für das Interview festgelegt hast. Außerdem markieren die Auswertungen Antworten, die zu schnell waren, um die Frage gelesen zu haben, wann der Kandidat die Seite verlassen hat und Kopierversuche.",
    },
    {
        "key": "reports",
        "question": "Kann ich Ergebnisse mit einer Führungskraft im Recruiting teilen?",
        "answer": "Ja. Lade einen PDF-Bericht für einen Kandidaten oder für alle Kandidaten eines Interviews herunter, sende ihn direkt aus prepza per E-Mail oder schick eine kurze Zusammenfassung über WhatsApp oder Telegram.",
    },
    {
        "key": "candidates",
        "question": "Was sehen Kandidaten?",
        "answer": "Den Namen und das Logo deines Unternehmens, vor dem Start, was sie erwartet, dann jeweils eine Frage mit Zeitlimit. Sie sehen nie ihr Ergebnis oder ob eine Antwort richtig war.",
    },
    {
        "key": "verified",
        "question": "Was bedeutet das Verifiziert-Häkchen?",
        "answer": "Dass sich ein Inhaber oder Admin des Unternehmens mit einer Arbeits-E-Mail auf der Website des Unternehmens angemeldet hat, etwa du@acme.com, und unser Team das Unternehmen danach geprüft hat. Füge die Website über Verifizieren im Kopfbereich deines Unternehmens hinzu; kostenlose E-Mail-Dienste zählen nicht. Solange die Prüfung aussteht, sieht dein Team eine Uhr neben dem Namen, und eine Umbenennung schickt das Unternehmen erneut zur Prüfung. Das Häkchen erscheint neben dem Namen deines Unternehmens, auch in Einladungen.",
    },
    {
        "key": "languages",
        "question": "Welche Sprachen werden unterstützt?",
        "answer": "{count} Sprachen, für die Website, die Interviews und die E-Mails. Wähle die Sprache, in der ein Interview geschrieben wird, egal in welcher Sprache die Stellenbeschreibung ist.",
    },
    {
        "key": "privacy",
        "question": "Was passiert mit Stellenbeschreibungen und Antworten?",
        "answer": "Stellenbeschreibungen werden genutzt, um deine Interviews zu erstellen, und die Antworten der Kandidaten, um sie zu bewerten, nur für dein Unternehmen. Die Datenschutzerklärung erklärt, was wir speichern, wie lange und welche Rechte alle haben.",
    },
    {
        "key": "delete",
        "question": "Kann ich mein Konto löschen?",
        "answer": "Ja, in den Einstellungen. Dein Konto und deine Daten werden gelöscht, und vorher kannst du eine Kopie deiner Daten herunterladen.",
    },
]
