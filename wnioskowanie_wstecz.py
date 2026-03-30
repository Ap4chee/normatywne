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


def udowodnij(cel, sciezka, poziom):
    wcięcie = "  " * poziom

    if cel in fakty:
        print(f"{wcięcie}\"{cel}\" jest faktem -> PRAWDA")
        return True

    if cel in sciezka:
        return False

    for i, r in enumerate(reguly):
        if r["wniosek"] != cel:
            continue

        print(f"{wcięcie}Probuje regule {i + 1} dla \"{cel}\"")

        ok = True
        for w in r["warunki"]:
            if not udowodnij(w, sciezka + [cel], poziom + 1):
                ok = False
                break

        if ok:
            for n in r["negacje"]:
                print(f"{wcięcie}  NAF: czy \"{n}\" da sie udowodnic?")
                if udowodnij(n, sciezka + [cel], poziom + 2):
                    print(f"{wcięcie}  NAF: tak -> ~\"{n}\" FALSZ")
                    ok = False
                    break
                else:
                    print(f"{wcięcie}  NAF: nie -> ~\"{n}\" PRAWDA")

        if ok:
            print(f"{wcięcie}Regula {i + 1} SUKCES -> \"{cel}\"")
            return True

    print(f"{wcięcie}\"{cel}\" - nie da sie udowodnic")
    return False


print("=== WNIOSKOWANIE WSTECZ ===")
print("Fakty:", fakty)
print()

cele = ["nalezy zwolnic", "jedz jak chcesz"]

for cel in cele:
    print(f"--- Cel: \"{cel}\" ---")
    wynik = udowodnij(cel, [], 0)
    print(f"Wynik: {wynik}")
    print()
