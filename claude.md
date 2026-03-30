# Co powiedziec prowadzacemu

## Baza wiedzy

Baza wiedzy dotyczy jazdy samochodem. Mamy 7 regul i 3 fakty poczatkowe.
Reguly mowia np. ze jesli jest ograniczenie do 50 i jedziesz ponizej 50 to masz prawidlowa predkosc.
Sa tez reguly z negacja - np. jesli NIE masz prawidlowej predkosci to nalezy zwolnic.
Fakty poczatkowe: ograniczenie do 50, szybkosc ponizej 50, mgla.

## Skrypt 1: Wnioskowanie w przod (wnioskowanie_w_przod.py)

Jak to dziala:
- Zaczynamy od faktow poczatkowych
- Lecimy po wszystkich regulach i sprawdzamy czy warunki sa spelnione
- Jesli tak to dodajemy wniosek do faktow
- Powtarzamy az nic nowego sie nie pojawi

Zrobilem to w dwoch etapach (stratyfikacja):
- Etap 1: odpalam tylko reguly BEZ negacji - zeby najpierw wyprowadzic wszystko co sie da
- Etap 2: odpalam reguly Z negacja - bo dopiero teraz wiem co jest a czego nie ma w faktach

Dlaczego stratyfikacja? Bo bez niej regula z negacja mogla odpalic za wczesnie - np. regula "jesli NIE ma trudnych warunkow to jedz jak chcesz" odpalilaby zanim wyprowadzilbym ze mgla daje trudne warunki.

Co wychodzi: z 3 faktow wyprowadzamy prawidlowa predkosc (regula 1), trudne warunki (regula 5, bo mgla), nalezy zwolnic (regula 3, bo prawidlowa predkosc + trudne warunki).

## Skrypt 2: Wnioskowanie wstecz (wnioskowanie_wstecz.py)

Jak to dziala:
- Zaczynamy od celu - np. "nalezy zwolnic"
- Szukamy reguly ktora ma ten cel jako wniosek
- Rekurencyjnie probujemy udowodnic kazdy warunek tej reguly
- Warunek jest prawdziwy jesli jest faktem ALBO da sie go wyprowadzic z innej reguly
- Dla negacji uzywam NAF - probuje udowodnic pozytywna wersje, jesli sie nie da to negacja jest prawdziwa

Mam 3 funkcje ktore sie nawzajem wywoluja rekurencyjnie:
- udowodnij() - glowna funkcja, sprawdza czy cel jest faktem, jesli nie to szuka reguly
- udowodnij_warunki() - bierze liste warunkow, udowadnia pierwszy, potem rekurencyjnie reszte
- udowodnij_negacje() - dla kazdej negacji sprawdza NAF

Przyklad dla celu "nalezy zwolnic":
- Najpierw probuje regule 2 (~prawidlowa predkosc -> nalezy zwolnic)
- NAF: probuje udowodnic prawidlowa predkosc -> udaje sie (regula 1) -> negacja FALSZ
- Regula 2 odpada
- Probuje regule 3 (prawidlowa predkosc && trudne warunki -> nalezy zwolnic)
- Rekurencyjnie udowadnia oba warunki -> SUKCES

## Skrypt 3: Negation as Failure (naf.py)

Czym jest NAF:
- To sposob na obsluge negacji w systemach regul
- Jesli chcemy sprawdzic czy ~X (nie X) to probujemy udowodnic X
- Jesli X sie nie da udowodnic to przyjmujemy ze ~X jest prawdziwe
- To nie jest klasyczna negacja - nie musimy UDOWADNIAC ze cos jest falszywe, wystarczy ze nie umiemy udowodnic ze jest prawdziwe

Skrypt testuje 3 przypadki:
- ~prawidlowa predkosc = FALSZ (bo da sie wyprowadzic z reguly 1)
- ~trudne warunki = FALSZ (bo da sie wyprowadzic z reguly 5, bo mgla)
- ~snieg = PRAWDA (bo snieg nie jest faktem i zadna regula go nie daje)

Na koniec pokazuje kontrprzyklad - co by bylo gdyby nie bylo mgly:
- Wtedy trudne warunki nie daloby sie wyprowadzic
- NAF mowi ze ~trudne_warunki = PRAWDA
- I regula 4 odpala -> jedz jak chcesz

## Jezyk naukowy na obrone

- wnioskowanie w przod = "forward chaining" = "data-driven reasoning" = od faktow do wnioskow
- wnioskowanie wstecz = "backward chaining" = "goal-driven reasoning" = od celu do faktow
- NAF = "negation as failure" = "closed world assumption" = czego nie mozna udowodnic jest falszywe
- stratyfikacja = dzielenie regul na warstwy zeby negacja dzialala poprawnie
