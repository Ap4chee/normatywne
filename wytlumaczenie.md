# Wyjasnienie kodu `main.ts`

Ten program czyta baze wiedzy ASPIC z pliku `.bw`, buduje z niej argumenty, wyznacza ataki miedzy argumentami, a potem wypisuje wyniki dla semantyk `preferred` i `grounded`.

Nie chodzi tu o zwykle sprawdzenie jednej reguly. Program najpierw tworzy wszystkie argumenty, ktore da sie wyprowadzic z faktow i regul, a dopiero potem patrzy, ktore z nich sie ze soba kloca.

## Co jest w bazie wiedzy

Baza wiedzy jest podzielona na cztery czesci:

- `Kn` - fakty pewne, czyli niepodwazalne.
- `Kp` - fakty zwykle, czyli takie, ktore mozna pozniej podwazyc.
- `Rs` - reguly scisle, zapisywane przez `->`.
- `Rd` - reguly domyslne/podwazalne, zapisywane przez `=>`.

Znak `~` oznacza negacje. Na przyklad `~g` znaczy "nie g", a `~r3` znaczy, ze podwazana jest regula `r3`.

## Glowne typy danych

`Rule` opisuje jedna regule. Ma identyfikator, liste przeslanek i wniosek.

`Arg` opisuje argument. Argument ma swoje ID, wniosek, zbior uzytych regul, zbior pierwotnych przeslanek oraz liste podargumentow.

`Attack` to para argumentow. Pierwszy argument z pary atakuje drugi.

## Funkcje pomocnicze

Na poczatku sa male funkcje do porzadkowania tekstu:

- `strip` usuwa spacje i cudzyslowy z poczatku oraz konca tekstu.
- `clean` normalizuje symbole, np. usuwa koncowe kropki i sredniki, ale zachowuje negacje `~`.
- `split` dzieli liste symboli po przecinkach.
- `opposite` zwraca przeciwienstwo symbolu, czyli z `g` robi `~g`, a z `~g` robi `g`.
- `fmt` formatuje zbiory do ladnego wypisania w konsoli.

Sa tez dwie funkcje techniczne:

- `product` tworzy wszystkie kombinacje argumentow dla przeslanek reguly.
- `powerSet` tworzy wszystkie podzbiory argumentow, co jest potrzebne przy semantyce `preferred`.

## Wczytywanie bazy wiedzy

Za wczytanie pliku odpowiada `parseBase`.

Ta funkcja czyta plik jako tekst, a potem korzysta z dwoch mniejszych funkcji:

- `readFacts` wyciaga fakty z sekcji `Kn` albo `Kp`.
- `readRules` wyciaga reguly z sekcji `Rs` albo `Rd`.

Efektem jest obiekt, w ktorym osobno trzymane sa fakty pewne, fakty podwazalne, reguly scisle i reguly podwazalne.

## Budowanie argumentow

Najwazniejsza czesc programu to `buildArgs`.

Najpierw program bierze wszystkie fakty z `Kn` i `Kp` i tworzy z nich najprostsze argumenty. Taki argument nie uzywa jeszcze zadnej reguly, bo jest po prostu faktem z bazy.

Potem program przechodzi po regulach. Dla kazdej reguly sprawdza, czy istnieja juz argumenty, ktore udowadniaja jej przeslanki. Jesli tak, to z tych argumentow budowany jest nowy argument z wnioskiem tej reguly.

Przyklad:

```txt
r2: a,b => g
```

Jesli program ma juz argument za `a` i argument za `b`, to moze zbudowac nowy argument za `g`.

Petla dziala tak dlugo, jak dlugo udaje sie dodac cos nowego. Dzieki temu mozna budowac argumenty wieloetapowo, np. najpierw `f` z `e`, a potem `~r3` z `f`.

Program pilnuje tez, zeby nie dodawac drugi raz takiego samego argumentu. Sprawdza wniosek, uzyte reguly i przeslanki.

## Budowanie atakow

Za ataki odpowiada `buildAttacks`.

Program porownuje kazda pare argumentow i sprawdza, czy jeden moze zaatakowac drugi. Sa trzy glowne przypadki:

1. Przeciwny wniosek.

   Jesli jeden argument konczy sie `g`, a drugi `~g`, to jest konflikt. Taki atak ma sens szczegolnie wtedy, gdy atakowany argument opiera sie na wiedzy podwazalnej.

2. Podwazenie przeslanki.

   Jesli argument uzywa jako przeslanki `p`, a inny argument daje `~p`, to ten drugi atakuje pierwszy.

3. Podwazenie reguly.

   Jesli argument zostal zbudowany przez regule `r3`, a inny argument ma wniosek `~r3`, to znaczy, ze atakuje uzycie tej reguly.

Ataki sa przechowywane w mapie, zeby nie bylo duplikatow.

## Semantyka preferred

Funkcja `preferred` szuka maksymalnych zbiorow argumentow, ktore da sie zaakceptowac razem.

Program robi to w kilku krokach:

1. Tworzy wszystkie mozliwe podzbiory argumentow.
2. Odrzuca zbiory, w ktorych argumenty atakuja sie nawzajem.
3. Sprawdza, czy kazdy argument w zbiorze jest broniony przed atakami z zewnatrz.
4. Zostawia tylko zbiory maksymalne, czyli takie, ktorych nie da sie juz powiekszyc bez zepsucia warunkow.

To podejscie jest proste i czytelne. Przy bardzo duzych bazach byloby kosztowne, ale dla tej bazy wiedzy jest wystarczajace.

## Semantyka grounded

Funkcja `grounded` liczy bardziej ostrozny wynik.

Program zaczyna od pustego zbioru zaakceptowanych argumentow. Potem krok po kroku dodaje tylko te argumenty, ktore nie sa atakowane albo ktorych atakujacy sa juz odparci przez zaakceptowane argumenty.

Proces konczy sie wtedy, gdy w kolejnej rundzie nie da sie dodac nic nowego.

W praktyce `grounded` daje najbardziej ostrozny zestaw wnioskow, czyli taki, ktory nie wymaga wybierania jednej z kilku rownie mozliwych stron konfliktu.

## Wypisywanie wyniku

Funkcja `print` odpowiada tylko za pokazanie wyniku w konsoli.

Wypisuje kolejno:

1. Wszystkie zbudowane argumenty.
2. Wszystkie ataki.
3. Wynik semantyki `preferred`.
4. Wynik semantyki `grounded`.

Dla semantyk program wypisuje juz nie same ID argumentow, ale ich wnioski, bo to jest czytelniejsze.

## Start programu

Na koncu pliku program wybiera plik bazy wiedzy.

Jesli podamy sciezke w argumencie, np.:

```powershell
node --experimental-strip-types main.ts .\aspic-baza-wiedzy.bw
```

to program uzyje tej sciezki. Jesli nie podamy argumentu, uzyje domyslnie `aspic-baza-wiedzy.bw`.

Potem program:

1. Sprawdza, czy plik istnieje.
2. Parsuje baze wiedzy.
3. Buduje argumenty.
4. Buduje ataki.
5. Wypisuje wynik.

## Calosc jednym zdaniem

Program zamienia baze wiedzy na graf argumentow i atakow, a potem sprawdza, ktore wnioski da sie zaakceptowac wedlug semantyk `preferred` i `grounded`.
