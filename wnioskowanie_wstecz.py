reguly = [
    {"warunki": ["ograniczenie do 50", "szybkosc ponizej 50"], "negacje": [], "wniosek": "prawidlowa predkosc"},
    {"warunki": [], "negacje": ["prawidlowa predkosc"], "wniosek": "nalezy zwolnic"},
    {"warunki": ["prawidlowa predkosc", "trudne warunki"], "negacje": [], "wniosek": "nalezy zwolnic"},
    {"warunki": ["prawidlowa predkosc"], "negacje": ["trudne warunki"], "wniosek": "jedz jak chcesz"},
    {"warunki": ["mgla"], "negacje": [], "wniosek": "trudne warunki"},
    {"warunki": ["snieg"], "negacje": [], "wniosek": "trudne warunki"},
    {"warunki": ["ograniczenie do 90", "szybkosc ponizej 90"], "negacje": [], "wniosek": "prawidlowa predkosc"},
]

fakty = ["ograniczenie do 50", "szybkosc ponizej 50", "mgla"]

odwiedzone = set()

def udowodnij(cel, poziom=0):
    wcięcie = "  " * poziom
    print(f"{wcięcie}Cel: \"{cel}\"")

    if cel in fakty:
        print(f"{wcięcie}-> \"{cel}\" jest w faktach")
        return True

    if cel in odwiedzone:
        print(f"{wcięcie}-> juz sprawdzane, nie udalo sie")
        return False
    odwiedzone.add(cel)

    for i, r in enumerate(reguly):
        if r["wniosek"] == cel:
            print(f"{wcięcie}Probuje regule {i + 1}: {r['warunki']} + ~{r['negacje']} -> \"{r['wniosek']}\"")

            wszystko_ok = True

            for w in r["warunki"]:
                if not udowodnij(w, poziom + 1):
                    wszystko_ok = False
                    break

            if wszystko_ok:
                for n in r["negacje"]:
                    print(f"{wcięcie}  Sprawdzam czy NIE da sie udowodnic: \"{n}\"")
                    if udowodnij(n, poziom + 1):
                        print(f"{wcięcie}  \"{n}\" udowodnione -> negacja NIESPELNIONA")
                        wszystko_ok = False
                        break
                    else:
                        print(f"{wcięcie}  \"{n}\" nieudowodnione -> negacja SPELNIONA (NAF)")

            if wszystko_ok:
                print(f"{wcięcie}-> Regula {i + 1} SUKCES: udowodniono \"{cel}\"")
                fakty.append(cel)
                return True

    print(f"{wcięcie}-> Nie udalo sie udowodnic \"{cel}\"")
    return False


print("=== WNIOSKOWANIE WSTECZ ===")
print("Fakty poczatkowe:", fakty)
print()

cele = ["nalezy zwolnic", "jedz jak chcesz", "trudne warunki", "prawidlowa predkosc"]

for cel in cele:
    odwiedzone.clear()
    print(f"--- Czy mozna udowodnic: \"{cel}\"? ---")
    wynik = udowodnij(cel)
    print(f"Wynik: {wynik}")
    print()
