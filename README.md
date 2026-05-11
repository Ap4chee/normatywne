# ASPIC w TypeScript

Program buduje argumenty na podstawie bazy wiedzy zapisanej w pliku `aspic-baza-wiedzy.bw`, wyznacza relacje ataku miedzy argumentami, a potem wypisuje wyniki dla semantyk `preferred` i `grounded`.

## Uruchomienie

```powershell
node main.ts
```

Program domyslnie czyta plik:

```txt
aspic-baza-wiedzy.bw
```

## Baza wiedzy

Aktualna baza ma postac:

```txt
Kp = a,b,c,d
Kn = e
Rs = {r1:e -> f}
Rd = {r2: a,b => g. r3: c => ~g. r4: c,d => h. r5: g,h => w, r6: f => ~r3}
```

Znaczenie elementow:

- `Kn` to fakty pewne, czyli wiedza niepodwazalna. W przykladzie jest to `e`.
- `Kp` to fakty zwykle, czyli takie, ktore moga byc podwazane. W przykladzie sa to `a`, `b`, `c`, `d`.
- `Rs` to reguly scisle. Regula `r1:e -> f` oznacza, ze z `e` wynika `f`.
- `Rd` to reguly domyslne/podwazalne. Na przyklad `r2: a,b => g` oznacza, ze z `a` oraz `b` mozna wyprowadzic `g`, ale taki wniosek moze zostac zaatakowany.
- Znak `~` oznacza negacje, np. `~g` znaczy "nie g", a `~r3` oznacza podwazenie reguly `r3`.

## Przykladowy output

Po uruchomieniu:

```powershell
node main.ts
```

program wypisuje:

```txt
Wczytano baze wiedzy: aspic-baza-wiedzy.bw

--- ARGUMENTY ---
A0 | wniosek: e | reguly: [] | sub: []
A1 | wniosek: a | reguly: [] | sub: []
A2 | wniosek: b | reguly: [] | sub: []
A3 | wniosek: c | reguly: [] | sub: []
A4 | wniosek: d | reguly: [] | sub: []
A5 | wniosek: f | reguly: [r1] | sub: [A0]
A6 | wniosek: g | reguly: [r2] | sub: [A1, A2]
A7 | wniosek: ~g | reguly: [r3] | sub: [A3]
A8 | wniosek: h | reguly: [r4] | sub: [A3, A4]
A9 | wniosek: w | reguly: [r2, r4, r5] | sub: [A6, A8]
A10 | wniosek: ~r3 | reguly: [r1, r6] | sub: [A5]

--- ATAKI ---
A10 atakuje A7
A6 atakuje A7
A7 atakuje A6

--- PREFERRED ---
1: [~r3, a, b, c, d, e, f, g, h, w]

--- GROUNDED ---
[~r3, a, b, c, d, e, f, g, h, w]
```

## Wyjasnienie sekcji `ARGUMENTY`

Kazda linia opisuje jeden argument:

```txt
A5 | wniosek: f | reguly: [r1] | sub: [A0]
```

Oznacza to, ze argument `A5` ma wniosek `f`, zostal zbudowany przy uzyciu reguly `r1` i korzysta z podargumentu `A0`.

Argumenty `A0`-`A4` nie maja zadnych regul ani podargumentow, poniewaz sa bezposrednio faktami z bazy wiedzy:

- `A0` to fakt `e` z `Kn`.
- `A1`, `A2`, `A3`, `A4` to fakty `a`, `b`, `c`, `d` z `Kp`.

Dalsze argumenty sa juz wyprowadzane z regul:

- `A5` wyprowadza `f` z `e` przez regule `r1`.
- `A6` wyprowadza `g` z `a` i `b` przez regule `r2`.
- `A7` wyprowadza `~g` z `c` przez regule `r3`.
- `A8` wyprowadza `h` z `c` i `d` przez regule `r4`.
- `A9` wyprowadza `w` z `g` i `h`, czyli korzysta z argumentow `A6` oraz `A8`.
- `A10` wyprowadza `~r3`, czyli podwaza regule `r3`.

## Wyjasnienie sekcji `ATAKI`

Ataki pokazuja konflikty miedzy argumentami.

```txt
A6 atakuje A7
A7 atakuje A6
```

Argument `A6` konczy sie wnioskiem `g`, a argument `A7` konczy sie wnioskiem `~g`. Sa to przeciwne wnioski, dlatego argumenty atakuja sie wzajemnie.

```txt
A10 atakuje A7
```

Argument `A10` ma wniosek `~r3`, czyli mowi, ze regula `r3` jest podwazona. Poniewaz argument `A7` zostal zbudowany wlasnie za pomoca reguly `r3`, argument `A10` atakuje `A7`.

## Wyjasnienie semantyk

Sekcja `PREFERRED` pokazuje maksymalne dopuszczalne zbiory argumentow. W tym przykladzie program znalazl jeden taki zbior:

```txt
[~r3, a, b, c, d, e, f, g, h, w]
```

W tym zbiorze znajduje sie `g`, ale nie ma `~g`. Wynika to z tego, ze argument za `~g` jest oslabiony przez `~r3`, czyli przez podwazenie reguly `r3`.

Sekcja `GROUNDED` pokazuje najbardziej ostrozny zbior zaakceptowanych wnioskow. W tym przykladzie wynik jest taki sam jak dla `preferred`, poniewaz konflikt `g` kontra `~g` zostaje rozstrzygniety przez dodatkowy argument `~r3`, ktory atakuje argument prowadzacy do `~g`.
