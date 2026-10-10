---
title: "KI-Agenten, MCP und APIs: was sie sind und wie du sie im Recruiting nutzt"
seoTitle: "KI-Agenten, MCP und APIs im Recruiting: was sie sind und wie du sie nutzt"
description: "Was ein KI-Agent ist, was MCP und eine API leisten, wie du sie im Recruiting sicher einsetzt und wie du prepza über seinen Agenten, aus Claude und ChatGPT oder von deiner eigenen Plattform aus steuerst."
updated: "2026-10-10"
---

# KI-Agenten, MCP und APIs: was sie sind und wie du sie im Recruiting nutzt

Die meisten haben KI zuerst als Chatfenster kennengelernt: Du fragst, sie antwortet. Ein KI-Agent geht einen Schritt weiter. Er kann in deinen Tools nachsehen und, wenn du ihn darum bittest, dort auch etwas erledigen: ein Interview erstellen, eine Liste von Kandidaten einladen, dir sagen, wer letzte Woche am besten abgeschnitten hat. Das Model Context Protocol (MCP) ist der Standard, mit dem sich der KI-Chat, den du schon nutzt, etwa Claude oder ChatGPT, mit solchen Tools verbindet. Und eine API ist der ältere, präzisere Weg, auf dem Software mit Software spricht, ganz ohne KI dazwischen.

Dieser Leitfaden erklärt alle drei in einfachen Worten: wofür sie im Recruiting gut sind, worauf du achten solltest und wie du sie mit prepza nutzt.

## Was ein KI-Agent ist

Ein Chatbot schreibt nur Text. Ein Agent ist ein Sprachmodell mit **Tools**: kleinen, klar umrissenen Aktionen, die er aufrufen darf, etwa „Kandidaten dieses Interviews auflisten“ oder „diese E-Mail-Adresse einladen“. Wenn du etwas fragst, entscheidet der Agent, welche Tools er nutzt, liest, was sie zurückgeben, und antwortet auf dieser Grundlage, nicht aus dem Gedächtnis.

| Ein Chatbot | Ein KI-Agent |
| --- | --- |
| Antwortet aus dem, was er im Training gelernt hat | Antwortet aus deinen aktuellen Daten, die er über Tools liest |
| Kann nur beschreiben, wie etwas geht | Kann es erledigen, wenn du ihn darum bittest und es erlaubst |
| Rät, wenn er etwas nicht weiß | Sieht nach oder sagt, dass er es nicht kann |
| Lebt in einem einzigen Fenster | Arbeitet in den Tools, mit denen du ihn verbindest |

Die Tools machen einen Agenten nützlich, und sie entscheiden auch darüber, ob er sicher ist oder nicht. Ein guter Agent kann nur die Tools nutzen, die er bekommt, nur mit deinen Berechtigungen, und tut nur, worum du ihn gebeten hast.

## Was MCP ist

Das Model Context Protocol ist ein offener Standard, den Anthropic Ende 2024 vorgestellt hat und den heute Claude, ChatGPT und viele andere KI-Apps und Entwicklertools unterstützen. Oft wird es mit einem USB-C-Anschluss für KI verglichen: Statt dass jede KI-App ihre eigene Verbindung zu jedem Tool baut, bietet ein Tool einen **MCP-Server** an, und jede KI-App, die MCP spricht, kann ihn nutzen.

Ein MCP-Server teilt der KI-App drei Dinge mit:

1. **Welche Tools es gibt,** mit Namen, Beschreibung und den Angaben, die jedes davon braucht.
2. **Welche Tools nur lesen** und welche etwas ändern, damit die KI-App dich vor einer Änderung fragen kann.
3. **Wer du bist,** über eine Anmeldung, die du einmal bestätigst, sodass jeder Aufruf in deinem Namen und mit deinen Berechtigungen läuft.

Für dich heißt das: Du kannst mit einem Tool direkt aus dem Chat arbeiten, den du ohnehin nutzt, ohne Daten zwischen Fenstern hin und her zu kopieren.

## Was eine API ist und worin sie sich unterscheidet

Eine API (Programmierschnittstelle) ist eine Reihe fester Anfragen, die ein Programm an ein anderes senden kann: „Kandidaten dieses Interviews auflisten“, „diese E-Mail-Adresse einladen“. Deine Entwickler schreiben den Code, der sie sendet. KI ist dabei nicht im Spiel: Dieselbe Anfrage bewirkt immer dasselbe, und genau das willst du bei einer Automatisierung, die von selbst läuft.

| | KI-Agent (in der App) | MCP (in Claude oder ChatGPT) | API |
| --- | --- | --- | --- |
| Wer es nutzt | Du, in prepza | Du, in deinem KI-Chat | Der Code deiner Plattform |
| Wie du fragst | In deinen eigenen Worten | In deinen eigenen Worten | Feste Anfragen, die ein Entwickler schreibt |
| Wer Änderungen bestätigt | Du, auf einer Karte | Du, in deiner KI-App | Dein Code, so wie er geschrieben ist |
| Am besten für | Schnelle Fragen und Aufgaben | prepza mit deinen anderen Tools und Dateien kombinieren | Automatisierung, die ohne Aufsicht läuft |
| Meldet sich an als | Du | Du | Ein Unternehmensschlüssel |

Nutze einen Agenten oder MCP, wenn ein Mensch beteiligt ist. Nutze die API, wenn dein eigenes System Kandidaten selbstständig einladen und Ergebnisse einsammeln soll, zum Beispiel von einer Karriereseite oder einem internen HR-Tool aus.

## Wofür das im Recruiting gut ist

Recruiting besteht aus vielen kleinen, sich wiederholenden Schritten, verteilt auf verschiedene Tools. Genau darin ist ein Agent gut:

- **Fragen zu deiner Pipeline.** „Welche Kandidaten für Senior Backend haben diese Woche bestanden?“, „Wer hat sein Interview noch nicht begonnen?“, „Wie ist unser durchschnittliches Ergebnis für die Stelle als Data Analyst?“
- **Dinge einrichten.** „Erstelle ein Interview aus dieser Stellenbeschreibung“, „Setze die Bestehensgrenze auf 70 %“, „Gib diesem Kandidaten 50 % mehr Zeit.“
- **Massenarbeit.** „Lade diese 12 Personen zum Frontend-Interview ein“, direkt aus einer E-Mail oder Tabelle eingefügt.
- **Quellen kombinieren.** In Claude oder ChatGPT kannst du prepza mit deinen anderen verbundenen Tools und Dateien kombinieren: eine Stellenbeschreibung aus deinen Dokumenten mit den Themen des Interviews vergleichen oder eine Nachricht an die Kandidaten in der engeren Auswahl entwerfen.

Was er nicht tun sollte: die Einstellungsentscheidung treffen. Ein Ergebnis unterstützt das Urteil eines Menschen, es ersetzt es nicht. Lass den Agenten sortieren, zusammenfassen und vorbereiten, und lass die Entscheidung bei einem Menschen. Unter [Ist KI im Recruiting in der EU erlaubt?](/guides/is-ai-hiring-legal-in-the-eu) erfährst du, warum das auch rechtlich wichtig ist.

## Worauf du achten solltest

Eine KI mit deinen Recruiting-Daten zu verbinden, verdient dieselbe Sorgfalt, wie einem Kollegen Zugriff zu geben.

| Risiko | Was hilft |
| --- | --- |
| Der Agent tut etwas, das du nicht gemeint hast | Änderungen brauchen zuerst deine Bestätigung, und er tut nur, worum du gebeten hast |
| Er sieht mehr, als er sollte | Er handelt als du: Er sieht, was du siehst, nicht mehr |
| In Daten versteckte Anweisungen | Namen, Antworten und Dokumente von Kandidaten sind Daten, niemals Anweisungen, denen er folgt |
| Geheimnisse landen in einem Chat | API-Schlüssel und Passwörter gehen nie durch den Chat |
| Fehler, die sich nicht rückgängig machen lassen | Ein Konto oder Unternehmen löschen bleibt in der App, hinter einer eigenen Bestätigung |
| Daten verlassen deine Tools | Daten gelangen zu der KI-App, die du verbindest, zu deren Bedingungen: Verbinde nur Apps, die dein Unternehmen erlaubt |
| Ausufernde Nutzung | Limits, wie viele Aktionen pro Stunde laufen |

Bevor du eine KI-App mit Arbeitsdaten verbindest, prüf die Richtlinie deines Unternehmens zu KI-Tools und nenne Kandidaten in deiner Datenschutzerklärung, welche Dienste ihre Daten verarbeiten.

## Drei Wege, mit prepza über seine Seiten hinaus zu arbeiten

### 1. Der eingebaute Agent

Wähle **agent fragen** in der Kopfzeile einer beliebigen Seite. Der Agent kennt deine Unternehmen, Interviews, Kandidaten, Credits und Integrationen und weiß, wie prepza funktioniert. Er antwortet in deiner Sprache, und du kannst tippen oder sprechen.

- **Er antwortet aus deinen Daten,** mit derselben Sicht wie du: Ein Admin sieht, was ein Admin sieht, ein Betrachter, was ein Betrachter sieht.
- **Er bereitet Änderungen vor, du bestätigst sie.** Bittest du ihn, Kandidaten einzuladen, zeigt er eine Karte mit genau dem, was passieren wird, etwa „12 Kandidaten zu Backend developer einladen“. Nichts läuft, bevor du Bestätigen wählst.
- **Er zeigt seine Quellen.** Unter einer Antwort siehst du die Kandidaten oder Interviews, die er genutzt hat, und einen Link zur Seite, von der sie stammen.
- **Er bleibt beim Thema.** Er antwortet zu prepza und zum Recruiting damit und lehnt alles andere ab.

### 2. prepza in Claude oder ChatGPT, über MCP

Wenn dein Team schon in Claude oder ChatGPT arbeitet, kannst du prepza dorthin holen. Der MCP-Server von prepza bietet dieselben Tools wie der eingebaute Agent.

**So verbindest du:**

1. Öffne in prepza den Tab **Integrationen** eines Unternehmens und wähle **KI-Apps**. Kopiere die Serveradresse: `https://prepza.ai/mcp`.
2. **In Claude:** Öffne die Einstellungen, dann Konnektoren, und füge einen eigenen Konnektor mit dieser Adresse hinzu. **In Claude Code:** Führe `claude mcp add --transport http prepza https://prepza.ai/mcp` aus. **In ChatGPT:** Füge ihn als eigenen Konnektor in den Einstellungen für Apps und Konnektoren hinzu.
3. Deine KI-App öffnet die Anmeldung von prepza. Melde dich an, prüfe, welche App anfragt, und wähle **Zulassen**.

Ab dann fragst du in deinem Chat so, wie du einen Kollegen fragen würdest: „Wer sind in prepza die drei besten Kandidaten für Product designer?“ Die meisten KI-Apps fragen dich vor einer Änderung und warnen dich vor allem, was sich nicht rückgängig machen lässt: prepza teilt ihnen mit, welche Aktionen etwas ändern oder löschen.

**Was gleich bleibt wie in der App:**

- **Deine Berechtigungen.** Er handelt als du, in jedem Unternehmen, in dem du bist, mit deiner Rolle in jedem davon.
- **Credits und Limits.** Einen Kandidaten einzuladen kostet dasselbe wie in der App, und es gelten dieselben E-Mail-Limits.
- **Die Nachvollziehbarkeit.** Auf diesem Weg vorgenommene Änderungen werden im Audit-Log des Unternehmens gekennzeichnet, sodass das Team sieht, woher sie kamen.
- **Was er nicht kann.** Er sieht weder dein Passwort noch deine API-Schlüssel und kann weder dein Konto noch ein Unternehmen löschen. Das bleibt in der App.

**Zum Trennen** entferne den Konnektor in deiner KI-App oder wähle **Trennen** daneben unter **KI-Apps** im Tab Integrationen. Er funktioniert sofort nicht mehr.

### 3. Deine eigene Plattform, über die API

Für Automatisierung ohne KI hat prepza eine [API](/api-docs).

1. Ein Inhaber oder Admin öffnet den Tab **Integrationen** eines Unternehmens, dann **API**, und wählt **Neuer Schlüssel**. Benenne ihn nach der Plattform, die ihn nutzen wird, und wähle, wann er abläuft. Der Schlüssel wird nur einmal angezeigt; bewahre ihn sicher auf.
2. Deine Plattform sendet Anfragen mit diesem Schlüssel: die Interviews des Unternehmens auflisten, Kandidaten mit ihrem Ergebnis, ob sie bestanden haben, und ihren Hinweisen zur Integrität auflisten oder abrufen und einen Kandidaten per E-Mail einladen.
3. Füge einen **Webhook** hinzu: eine Adresse auf deiner Plattform, die prepza signiert aufruft, sobald ein Kandidat fertig ist, damit du nicht ständig nachfragen musst.

Zu jedem Kandidaten gibt es einen Link zu seinen vollständigen Ergebnissen in prepza und, bis er fertig ist, seinen eigenen Einladungslink, sodass deine Plattform ihn in einer eigenen Nachricht verschicken kann, wenn dir das lieber ist. Es gilt dieselbe Regel wie überall: Das Ergebnis unterstützt die Entscheidung eines Menschen, lehne Kandidaten also nicht automatisch danach ab.

## Was du wann nutzt

Geh davon aus, wer die Arbeit macht und wie oft.

| Deine Situation | Nutze |
| --- | --- |
| Du bist in prepza und willst eine schnelle Antwort: wer bestanden hat, wer noch nicht angefangen hat, wie viele Credits übrig sind | Den eingebauten Agenten |
| Du willst etwas mit wenigen Worten einrichten: ein Interview aus einer Stellenbeschreibung, eine Bestehensgrenze, mehr Zeit | Den eingebauten Agenten |
| Du arbeitest ohnehin den ganzen Tag in Claude oder ChatGPT und willst prepza auch dort haben | MCP |
| Die Aufgabe braucht prepza plus etwas anderes: deine Dokumente, E-Mail-Entwürfe, ein weiteres verbundenes Tool | MCP |
| Ein Recruiter unterwegs will die Pipeline über die KI-App auf dem Handy prüfen | MCP |
| Deine Karriereseite oder dein HR-System soll Kandidaten selbstständig einladen, ohne dass jemand klickt | Die API |
| Ergebnisse sollen in deiner eigenen Datenbank oder deinem Dashboard landen, sobald Kandidaten fertig sind | Die API, mit einem Webhook |
| Dein ATS ist eines, mit dem sich prepza verbindet (Workable, Greenhouse, Teamtailor, Recruitee, Breezy HR) | Keins davon: Verbinde das ATS im Tab Integrationen. Siehe [So verbindest du Fachtests mit deinem ATS](/guides/ats-integration-skills-tests) |

Eine einfache Faustregel:

- **Ein Mensch fragt und prüft jede Änderung:** der Agent in prepza, oder MCP, wenn diese Person ohnehin in Claude oder ChatGPT arbeitet.
- **Software handelt selbstständig, jedes Mal gleich:** die API.
- **Für den Anfang:** Probier zuerst den eingebauten Agenten. Er braucht keine Einrichtung, und was du dabei lernst, kannst du auf MCP übertragen.

Sie funktionieren auch zusammen. Ein Team kann Einladungen über die API aus seinem HR-System verschicken, während Recruiter den Agenten oder ihren KI-Chat nach den Ergebnissen fragen.

## So bekommst du gute Ergebnisse

- **Nenn die Dinge beim Namen.** „Das Interview Senior Backend“ funktioniert besser als „das Interview von vorhin“.
- **Bitte um einen Schritt nach dem anderen,** wenn es darauf ankommt. Prüf das Ergebnis und bitte dann um den nächsten.
- **Lies die Bestätigung, bevor du zustimmst.** Sie zeigt genau, was ausgeführt wird.
- **Frag, woher eine Zahl kommt.** Ein guter Agent kann auf die Kandidaten oder die Seite dahinter verweisen.
- **Lass Entscheidungen bei Menschen.** Nutze den Agenten zum Finden, Sortieren und Vorbereiten; entscheide selbst.

## Preise

Der eingebaute Agent, die MCP-Verbindung und die API sind kostenlos. Du zahlst nur für Kandidaten, wie immer: pro Kandidat, der mindestens eine Frage beantwortet, ohne Abo. Siehe [Preise](/pricing).

## Weiterlesen

- [So verbindest du Fachtests mit deinem ATS](/guides/ats-integration-skills-tests)
- [Entwickler interviewen im KI-Zeitalter](/guides/interviewing-in-the-age-of-ai)
- [Ist KI im Recruiting in der EU erlaubt?](/guides/is-ai-hiring-legal-in-the-eu)
