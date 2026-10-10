---
title: "Agenci AI, MCP i API: czym są i jak wykorzystać je w rekrutacji"
seoTitle: "Agenci AI, MCP i API w rekrutacji: czym są i jak z nich korzystać"
description: "Czym jest agent AI, do czego służą MCP i API, jak bezpiecznie korzystać z nich w rekrutacji i jak obsługiwać prepza przez jej agenta, z Claude i ChatGPT albo z własnej platformy."
updated: "2026-10-10"
---

# Agenci AI, MCP i API: czym są i jak wykorzystać je w rekrutacji

Większość z nas poznała AI jako okno czatu: pytasz, a ono odpowiada. Agent AI idzie o krok dalej. Potrafi sprawdzać informacje w Twoich narzędziach, a gdy go o to poprosisz, także coś w nich zrobić: utworzyć rozmowę, zaprosić listę kandydatów, powiedzieć Ci, kto w zeszłym tygodniu uzyskał najlepszy wynik. Model Context Protocol (MCP) to standard, dzięki któremu czat AI, z którego już korzystasz, na przykład Claude lub ChatGPT, może łączyć się z takimi narzędziami. A API to starszy i bardziej precyzyjny sposób, w jaki oprogramowanie komunikuje się z innym oprogramowaniem, bez AI po drodze.

Ten poradnik wyjaśnia prostym językiem wszystkie trzy: do czego przydają się w rekrutacji, na co uważać i jak korzystać z nich w prepza.

## Czym jest agent AI

Chatbot tylko pisze tekst. Agent to model językowy z **narzędziami**: małymi, jasno określonymi czynnościami, które może wywołać, na przykład „pokaż kandydatów tej rozmowy” albo „zaproś ten adres e-mail”. Gdy o coś pytasz, agent decyduje, z których narzędzi skorzystać, czyta, co zwracają, i odpowiada na tej podstawie, a nie z pamięci.

| Chatbot | Agent AI |
| --- | --- |
| Odpowiada na podstawie tego, czego nauczył się podczas trenowania | Odpowiada na podstawie Twoich aktualnych danych, odczytanych przez narzędzia |
| Może tylko opisać, jak coś zrobić | Może to zrobić, gdy poprosisz i na to zezwolisz |
| Zgaduje, gdy nie wie | Sprawdza albo mówi, że nie może |
| Działa w jednym oknie | Działa w narzędziach, z którymi go połączysz |

To narzędzia sprawiają, że agent jest przydatny, i to od nich zależy, czy jest bezpieczny. Dobry agent może używać tylko narzędzi, które dostał, tylko z Twoimi uprawnieniami, i robi tylko to, o co poprosisz.

## Czym jest MCP

Model Context Protocol to otwarty standard, który Anthropic przedstawił pod koniec 2024 roku i który obsługują dziś Claude, ChatGPT oraz wiele innych aplikacji AI i narzędzi dla programistów. Często porównuje się go do portu USB-C dla AI: zamiast tego, by każda aplikacja AI budowała własne połączenie z każdym narzędziem, narzędzie udostępnia jeden **serwer MCP**, a każda aplikacja AI, która obsługuje MCP, może z niego korzystać.

Serwer MCP przekazuje aplikacji AI trzy rzeczy:

1. **Jakie narzędzia są dostępne,** wraz z nazwą, opisem i danymi, których każde z nich potrzebuje.
2. **Które narzędzia tylko odczytują dane,** a które coś zmieniają, żeby aplikacja AI mogła zapytać Cię przed zmianą.
3. **Kim jesteś,** dzięki logowaniu, które zatwierdzasz raz, więc każde wywołanie działa w Twoim imieniu i z Twoimi uprawnieniami.

Dla Ciebie oznacza to, że możesz pracować z narzędziem z poziomu czatu, którego już używasz, bez kopiowania danych między oknami.

## Czym jest API i czym się różni

API (interfejs programowania aplikacji) to zestaw stałych żądań, które jeden program może wysłać do drugiego: „pokaż kandydatów tej rozmowy”, „zaproś ten adres e-mail”. Twoi programiści piszą kod, który je wysyła. Nie ma tu żadnej AI: to samo żądanie zawsze robi to samo, i właśnie tego oczekujesz od automatyzacji, która działa samodzielnie.

| | Agent AI (w aplikacji) | MCP (w Claude lub ChatGPT) | API |
| --- | --- | --- | --- |
| Kto z tego korzysta | Ty, w prepza | Ty, w swoim czacie AI | Kod Twojej platformy |
| Jak pytasz | Własnymi słowami | Własnymi słowami | Stałymi żądaniami, które pisze programista |
| Kto zatwierdza zmiany | Ty, na karcie | Ty, w swojej aplikacji AI | Twój kod, tak jak go napisano |
| Najlepsze do | Szybkich pytań i zadań | Łączenia prepza z innymi narzędziami i plikami | Automatyzacji, która działa bez nadzoru |
| Loguje się jako | Ty | Ty | Klucz firmy |

Korzystaj z agenta lub MCP, gdy w procesie uczestniczy człowiek. Korzystaj z API, gdy Twój własny system ma samodzielnie zapraszać kandydatów i zbierać wyniki, na przykład ze strony kariery albo wewnętrznego narzędzia HR.

## Do czego to się przydaje w rekrutacji

Rekrutacja składa się z wielu drobnych, powtarzalnych kroków rozproszonych po różnych narzędziach. Właśnie w nich agent sprawdza się najlepiej:

- **Pytania o Twój lejek rekrutacyjny.** „Którzy kandydaci na Senior Backend zaliczyli test w tym tygodniu?”, „Kto jeszcze nie zaczął rozmowy?”, „Jaki jest nasz średni wynik na stanowisku analityka danych?”
- **Konfiguracja.** „Utwórz rozmowę na podstawie tego opisu stanowiska”, „Ustaw próg zaliczenia na 70%”, „Daj temu kandydatowi 50% więcej czasu.”
- **Praca hurtowa.** „Zaproś tych 12 osób na rozmowę frontendową”, wklejone prosto z e-maila lub arkusza kalkulacyjnego.
- **Łączenie źródeł.** W Claude lub ChatGPT możesz łączyć prepza z innymi podłączonymi narzędziami i plikami: porównać opis stanowiska z Twoich dokumentów z tematami rozmowy albo przygotować wiadomość do kandydatów z krótkiej listy.

Czego agent nie powinien robić, to podejmować decyzji o zatrudnieniu. Wynik wspiera ocenę człowieka, ale jej nie zastępuje. Poproś agenta, żeby sortował, podsumowywał i przygotowywał, a decyzję zostaw człowiekowi. Zobacz [Czy rekrutacja z AI jest legalna w UE?](/guides/is-ai-hiring-legal-in-the-eu), aby dowiedzieć się, dlaczego ma to znaczenie także prawne.

## Na co uważać

Połączenie AI z danymi rekrutacyjnymi wymaga takiej samej ostrożności jak przyznanie dostępu współpracownikowi.

| Ryzyko | Co pomaga |
| --- | --- |
| Agent robi coś niezgodnego z Twoim zamiarem | Zmiany wymagają najpierw Twojego zatwierdzenia, a agent robi tylko to, o co poprosisz |
| Widzi więcej, niż powinien | Działa jako Ty: widzi to, co Ty, nic więcej |
| Instrukcje ukryte w danych | Imiona i nazwiska, odpowiedzi i dokumenty kandydatów to dane, nigdy instrukcje do wykonania |
| Poufne dane trafiają do czatu | Klucze API i hasła nigdy nie przechodzą przez czat |
| Nieodwracalne błędy | Usunięcie konta lub firmy pozostaje w aplikacji, za osobnym potwierdzeniem |
| Dane opuszczają Twoje narzędzia | Dane trafiają do aplikacji AI, którą podłączasz, na jej warunkach: podłączaj tylko aplikacje, na które pozwala Twoja firma |
| Niekontrolowane użycie | Limity liczby czynności wykonywanych w ciągu godziny |

Zanim połączysz jakąkolwiek aplikację AI z danymi służbowymi, sprawdź politykę firmy dotyczącą narzędzi AI i poinformuj kandydatów w klauzuli informacyjnej, które usługi przetwarzają ich dane.

## Trzy sposoby pracy z prepza poza jej stronami

### 1. Wbudowany agent

Wybierz **zapytaj agenta** w nagłówku dowolnej strony. Agent zna Twoje firmy, rozmowy, kandydatów, kredyty i integracje oraz wie, jak działa prepza. Odpowiada w Twoim języku, a Ty możesz pisać albo mówić.

- **Odpowiada na podstawie Twoich danych,** z takim samym widokiem jak Twój: administrator widzi to, co administrator, a obserwator to, co obserwator.
- **Przygotowuje zmiany, a Ty je potwierdzasz.** Poproszony o zaproszenie kandydatów pokazuje kartę z dokładnym opisem tego, co się stanie, na przykład „Zaproś 12 kandydatów na Backend developer”. Nic się nie wykona, dopóki nie wybierzesz Potwierdź.
- **Pokazuje źródła.** Pod odpowiedzią widzisz kandydatów lub rozmowy, z których skorzystał, i link do strony, z której pochodzą.
- **Trzyma się tematu.** Odpowiada na pytania o prepza i rekrutację z jej pomocą, a resztę odrzuca.

### 2. prepza w Claude lub ChatGPT, przez MCP

Jeśli Twój zespół już pracuje w Claude lub ChatGPT, możesz przenieść tam prepza. Serwer MCP prepza udostępnia te same narzędzia co wbudowany agent.

**Jak połączyć:**

1. W prepza otwórz zakładkę **Integracje** firmy i wybierz **Aplikacje AI**. Skopiuj adres serwera: `https://prepza.ai/mcp`.
2. **W Claude:** otwórz Ustawienia, potem Konektory, i dodaj własny konektor z tym adresem. **W Claude Code:** uruchom `claude mcp add --transport http prepza https://prepza.ai/mcp`. **W ChatGPT:** dodaj go jako własny konektor w ustawieniach aplikacji i konektorów.
3. Twoja aplikacja AI otworzy logowanie do prepza. Zaloguj się, sprawdź, która aplikacja prosi o dostęp, i wybierz **Zezwól**.

Od tej chwili pytaj w czacie tak, jak pytasz współpracownika: „Kto w prepza jest w pierwszej trójce kandydatów na Product designer?” Większość aplikacji AI pyta Cię przed zmianą i ostrzega przed wszystkim, czego nie da się cofnąć: prepza informuje je, które działania coś zmieniają lub usuwają.

**Co pozostaje takie samo jak w aplikacji:**

- **Twoje uprawnienia.** Działa jako Ty, w każdej firmie, do której należysz, z Twoją rolą w każdej z nich.
- **Kredyty i limity.** Zaproszenie kandydata kosztuje tyle samo co w aplikacji i obowiązują te same limity e-maili.
- **Ślad zmian.** Zmiany wprowadzone w ten sposób są oznaczane w dzienniku zdarzeń firmy, więc zespół widzi, skąd pochodzą.
- **Czego nie może.** Nie widzi Twojego hasła ani kluczy API i nie może usunąć Twojego konta ani firmy. To pozostaje w aplikacji.

**Aby odłączyć,** usuń konektor w swojej aplikacji AI albo wybierz **Odłącz** obok niego w sekcji **Aplikacje AI** w zakładce Integracje. Przestaje działać od razu.

### 3. Twoja własna platforma, przez API

Do automatyzacji bez AI prepza ma [API](/api-docs).

1. Właściciel lub administrator otwiera zakładkę **Integracje** firmy, potem **API**, i wybiera **Nowy klucz**. Nazwij go tak jak platformę, która będzie z niego korzystać, i wybierz, kiedy wygaśnie. Klucz jest wyświetlany tylko raz; przechowuj go w bezpiecznym miejscu.
2. Twoja platforma wysyła żądania z tym kluczem: pobiera listę rozmów firmy, pobiera listę kandydatów lub dane pojedynczego kandydata z wynikiem, informacją, czy zaliczył, i sygnałami nieuczciwości, oraz zaprasza kandydata e-mailem.
3. Dodaj **webhook**: adres na Twojej platformie, który prepza wywołuje z podpisem, gdy tylko kandydat skończy, więc nie musisz ciągle dopytywać.

Każdy kandydat ma link do swoich pełnych wyników w prepza, a dopóki nie skończy, także własny link z zaproszeniem, więc Twoja platforma może wysłać go we własnej wiadomości, jeśli wolisz. Obowiązuje ta sama zasada co wszędzie: wynik wspiera decyzję człowieka, więc nie odrzucaj kandydatów automatycznie na jego podstawie.

## Co wybrać i kiedy

Zacznij od tego, kto wykonuje pracę i jak często.

| Twoja sytuacja | Użyj |
| --- | --- |
| Jesteś w prepza i chcesz szybkiej odpowiedzi: kto zaliczył, kto nie zaczął, ile zostało kredytów | Wbudowanego agenta |
| Chcesz coś skonfigurować w kilku słowach: rozmowę z opisu stanowiska, próg zaliczenia, dodatkowy czas | Wbudowanego agenta |
| Cały dzień pracujesz w Claude lub ChatGPT i chcesz mieć tam też prepza | MCP |
| Zadanie wymaga prepza i czegoś jeszcze: Twoich dokumentów, szkiców e-maili, innego podłączonego narzędzia | MCP |
| Rekruter w drodze chce sprawdzić lejek rekrutacyjny w aplikacji AI na telefonie | MCP |
| Twoja strona kariery lub system HR ma samodzielnie zapraszać kandydatów, bez niczyich kliknięć | API |
| Wyniki mają trafiać do Twojej bazy danych lub dashboardu, gdy tylko kandydaci skończą | API z webhookiem |
| Twój ATS jest jednym z tych, z którymi łączy się prepza (Workable, Greenhouse, Teamtailor, Recruitee, Breezy HR) | Żadnego z nich: połącz ATS w zakładce Integracje. Zobacz [Jak połączyć testy umiejętności z ATS](/guides/ats-integration-skills-tests) |

Prosta zasada:

- **Człowiek pyta i sprawdza każdą zmianę:** agent w prepza albo MCP, jeśli ta osoba na co dzień pracuje w Claude lub ChatGPT.
- **Oprogramowanie działa samo, za każdym razem tak samo:** API.
- **Na początek:** wypróbuj najpierw wbudowanego agenta. Nie wymaga konfiguracji, a to, czego się nauczysz, przyda się przy MCP.

Mogą też działać razem. Zespół może wysyłać zaproszenia ze swojego systemu HR przez API, a rekruterzy pytają o wyniki agenta lub swój czat AI.

## Jak uzyskać dobre wyniki

- **Nazywaj rzeczy.** „Rozmowa Senior Backend” działa lepiej niż „tamta rozmowa”.
- **Proś o jeden krok naraz,** gdy to ważne. Sprawdź wynik, a potem poproś o następny.
- **Przeczytaj prośbę o zatwierdzenie, zanim zezwolisz.** Pokazuje dokładnie, co zostanie wykonane.
- **Pytaj, skąd wzięła się liczba.** Dobry agent potrafi wskazać kandydatów lub stronę, na których się opiera.
- **Decyzje zostaw ludziom.** Używaj agenta do wyszukiwania, sortowania i przygotowania; decyzję podejmuj samodzielnie.

## Cennik

Wbudowany agent, połączenie MCP i API są bezpłatne. Płacisz tylko za kandydatów, tak jak zawsze: za każdego kandydata, który odpowie na co najmniej jedno pytanie, bez subskrypcji. Zobacz [cennik](/pricing).

## Przeczytaj też

- [Jak połączyć testy umiejętności z ATS](/guides/ats-integration-skills-tests)
- [Rozmowy z programistami w erze AI](/guides/interviewing-in-the-age-of-ai)
- [Czy rekrutacja z AI jest legalna w UE?](/guides/is-ai-hiring-legal-in-the-eu)
