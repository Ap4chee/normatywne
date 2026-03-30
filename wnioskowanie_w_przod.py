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

reguly_bez_negacji = [r for r in reguly if not r["negacje"]]
reguly_z_negacja = [r for r in reguly if r["negacje"]]

print("=== WNIOSKOWANIE W PRZOD ===")
print("Fakty poczatkowe:", fakty)
print()

krok = 0

print("--- Etap 1: reguly bez negacji ---")
zmiana = True
while zmiana:
    zmiana = False
    for i, r in enumerate(reguly):
        if r["negacje"]:
            continue
        warunki_ok = all(w in fakty for w in r["warunki"])
        if warunki_ok and r["wniosek"] not in fakty:
            krok += 1
            fakty.append(r["wniosek"])
            zmiana = True
            print(f"Krok {krok}: Uzyta regula {i + 1}")
            print(f"  Spelnione warunki: {r['warunki']}")
            print(f"  Nowy fakt: \"{r['wniosek']}\"")
            print()

print("--- Etap 2: reguly z negacja (NAF) ---")
zmiana = True
while zmiana:
    zmiana = False
    for i, r in enumerate(reguly):
        if not r["negacje"]:
            continue
        warunki_ok = all(w in fakty for w in r["warunki"])
        negacje_ok = all(n not in fakty for n in r["negacje"])
        if warunki_ok and negacje_ok and r["wniosek"] not in fakty:
            krok += 1
            fakty.append(r["wniosek"])
            zmiana = True
            print(f"Krok {krok}: Uzyta regula {i + 1}")
            if r["warunki"]:
                print(f"  Spelnione warunki: {r['warunki']}")
            print(f"  Brak w faktach (NAF): {r['negacje']}")
            print(f"  Nowy fakt: \"{r['wniosek']}\"")
            print()

print("Fakty koncowe:", fakty)
