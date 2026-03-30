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
            print(f"Krok {krok}: Regula {i + 1}")
            print(f"  Warunki: {r['warunki']}")
            print(f"  Dodaje: \"{r['wniosek']}\"")
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
            print(f"Krok {krok}: Regula {i + 1}")
            if r["warunki"]:
                print(f"  Warunki: {r['warunki']}")
            print(f"  Negacja (NAF): {r['negacje']} - brak w faktach")
            print(f"  Dodaje: \"{r['wniosek']}\"")
            print()

print("Fakty koncowe:", fakty)
