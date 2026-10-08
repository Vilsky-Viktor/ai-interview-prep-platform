# The FAQ in pl; the {placeholders} are filled in by helpers/help.py (faq_values) with
# billing's prices and the number of languages. Questions not translated yet show in English
# (constants/faq/__init__.py).
FAQ = [
    {
        "key": "what",
        "question": "Czym jest prepza?",
        "answer": "To rozmowa na czas stworzona z Twojego opisu stanowiska, dla dowolnej roli. Użyj jej do wstępnej selekcji kandydatów, zanim się z nimi spotkasz, albo jako etapu samej rekrutacji: tak czy inaczej zobaczysz, kto naprawdę zna się na rzeczy.",
    },
    {
        "key": "roles",
        "question": "Na jakie role mogę rekrutować?",
        "answer": "Na każdą rolę, w której liczy się wiedza: wsparcie klienta, sprzedaż, finanse, ochrona zdrowia, zawody techniczne, inżynieria, marketing i wiele innych. Jeśli potrafisz opisać stanowisko, prepza zbuduje do niego rozmowę.",
    },
    {
        "key": "hiring",
        "question": "Jak to działa?",
        "answer": "Wklej opis stanowiska na stronie głównej, podaj nazwę firmy i sprawdź tematy proponowane przez prepza. Potem zaproś kandydatów: wpisz ich adresy e-mail, wklej listę lub prześlij plik. Kandydaci, którzy po kilku dniach nie zaczęli, dostają jedno przypomnienie. Każdy kandydat dostaje własne pytania z limitem czasu na każde z nich, a Ty widzisz jego wynik i każdą odpowiedź, gdy tylko skończy.",
    },
    {
        "key": "link",
        "question": "Czy mogę umieścić rozmowę w ogłoszeniu o pracę?",
        "answer": "Tak. Włącz link do udostępnienia rozmowy na jej karcie kandydatów i wklej go do ogłoszenia. Każdy, kto go otworzy, loguje się i bierze udział w rozmowie, a za każdą osobę płacisz jak za zaproszonego kandydata. Link wyłącza się, gdy oznaczysz w rozmowie, że ktoś został zatrudniony.",
    },
    {
        "key": "preview",
        "question": "Czy mogę wypróbować rozmowę, zanim kogoś zaproszę?",
        "answer": "Tak. Otwórz swoją rozmowę jako kandydat z jej strony, bezpłatnie: podglądy nie pojawiają się wśród Twoich kandydatów ani w statystykach pytań. Możesz też odbyć dowolną z darmowych próbnych rozmów.",
    },
    {
        "key": "cheating",
        "question": "Czy kandydaci mogą korzystać z AI albo szukać odpowiedzi?",
        "answer": "Każdy kandydat dostaje własne losowe pytania we własnej kolejności, z limitem czasu na każde pytanie pilnowanym przez nasz serwer, więc zostaje niewiele czasu na szukanie odpowiedzi czy pytanie AI. Wyniki pokazują też, kiedy kandydat opuścił stronę, skopiował tekst albo odpowiedział zbyt szybko, by przeczytać pytanie.",
    },
    {
        "key": "cost",
        "question": "Ile to kosztuje?",
        "answer": "Generowanie rozmów jest darmowe. Każdy kandydat, który odpowie na co najmniej jedno pytanie, kosztuje {candidate} kredytów ({candidate_dollars} $), a mniej z kredytami z większych doładowań, nawet 1 $. Twoja pierwsza firma dostaje {company} darmowych kredytów, co wystarczy na pierwszych {company_candidates} kandydatów. Wszystkie ceny są na stronie cennika.",
    },
    {
        "key": "charged",
        "question": "Kiedy płacę za kandydata?",
        "answer": "Tylko wtedy, gdy kandydat ukończy rozmowę, odpowiadając na co najmniej jedno pytanie. Kredyty są rezerwowane, gdy go zapraszasz, i wracają, jeśli cofniesz zaproszenie, jeśli kandydat nigdy nie zacznie albo na nic nie odpowie.",
    },
    {
        "key": "compare_hiring",
        "question": "Jak cena wypada na tle innych narzędzi do oceny kandydatów?",
        "answer": "Wiele narzędzi do oceny kandydatów sprzedaje się w abonamencie miesięcznym lub rocznym, płatnym nawet wtedy, gdy nikogo nie testujesz. W prepza płacisz tylko za kandydatów: {candidate} kredytów ({candidate_dollars} $) za kandydata, bez umowy, bez opłat za użytkowników i bez płacenia za wygenerowanie rozmowy. Firma, która zaprasza {example_candidates} kandydatów miesięcznie, płaci około {example_year_dollars} $ rocznie. Jeśli co miesiąc testujesz wielu kandydatów, abonament może wyjść taniej, więc porównaj to ze swoimi liczbami.",
    },
    {
        "key": "expire",
        "question": "Czy kredyty wygasają?",
        "answer": "Nie. Kredyty nigdy nie wygasają i nie ma abonamentu ani odnowień.",
    },
    {
        "key": "refunds",
        "question": "Czy mogę dostać zwrot?",
        "answer": "Tak, za kredyty kupione w ciągu ostatnich 14 dni i jeszcze niewydane: przez Paddle lub pisząc do nas. Darmowe kredyty, takie jak prezent powitalny, nie podlegają zwrotowi. Szczegóły są w regulaminie.",
    },
    {
        "key": "scorecards",
        "question": "Co pokazują karty wyników?",
        "answer": "Każdą odpowiedź, czy była poprawna i ile trwała. Wyniki są oznaczone na zielono lub na czerwono względem progu zaliczenia ustawionego dla rozmowy. Karty wyników oznaczają też odpowiedzi zbyt szybkie, by przeczytać pytanie, opuszczenia strony i próby kopiowania.",
    },
    {
        "key": "reports",
        "question": "Czy mogę udostępnić wyniki menedżerowi rekrutującemu?",
        "answer": "Tak. Pobierz raport PDF dla jednego kandydata lub dla wszystkich kandydatów rozmowy, wyślij go e-mailem prosto z prepza albo prześlij krótkie podsumowanie przez WhatsApp, Telegram, Viber lub LINE.",
    },
    {
        "key": "integrations",
        "question": "Czy prepza działa z moim ATS lub innymi narzędziami?",
        "answer": "Tak, bez dodatkowych opłat. Połącz Workable, Greenhouse, Teamtailor, Recruitee lub Breezy HR w zakładce Integracje swojej firmy: kandydaci, których przeniesiesz do etapu, dostają rozmowę, a ich wyniki wracają do ATS. Slack może publikować powiadomienia firmy na kanale, a API pozwala Twojej własnej platformie zapraszać kandydatów i odbierać ich wyniki; zobacz: Dokumentacja API.",
    },
    {
        "key": "candidates",
        "question": "Co widzą kandydaci?",
        "answer": "Nazwę i logo Twojej firmy, przed startem informację, czego się spodziewać, a potem po jednym pytaniu z limitem czasu. Nigdy nie widzą swojego wyniku ani tego, czy odpowiedź była poprawna.",
    },
    {
        "key": "verified",
        "question": "Co oznacza znaczek weryfikacji?",
        "answer": "Że właściciel lub administrator firmy zalogował się służbowym e-mailem w domenie strony firmy, np. you@acme.com, a potem nasz zespół sprawdził firmę. Dodaj stronę przyciskiem Zweryfikuj w nagłówku firmy; darmowe usługi e-mail się nie liczą. Dopóki sprawdzenie trwa, Twój zespół widzi zegar obok nazwy, a zmiana nazwy firmy wysyła ją do ponownego sprawdzenia. Znaczek widać obok nazwy Twojej firmy, także w zaproszeniach.",
    },
    {
        "key": "languages",
        "question": "Jakie języki są obsługiwane?",
        "answer": "Liczba obsługiwanych języków: {count}, dla strony, rozmów i e-maili. Wybierz język, w którym ma być napisana rozmowa, niezależnie od języka opisu stanowiska.",
    },
    {
        "key": "privacy",
        "question": "Co dzieje się z opisami stanowisk i odpowiedziami?",
        "answer": "Opisy stanowisk służą do tworzenia Twoich rozmów, a odpowiedzi kandydatów do ich oceny, wyłącznie dla Twojej firmy. Polityka prywatności wyjaśnia, co przechowujemy, jak długo i jakie prawa przysługują każdemu.",
    },
    {
        "key": "delete",
        "question": "Czy mogę usunąć konto?",
        "answer": "Tak, w Ustawieniach. Twoje konto i dane zostają usunięte, a wcześniej możesz pobrać ich kopię.",
    },
]
