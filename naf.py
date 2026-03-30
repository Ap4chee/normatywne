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

def wyprowadz_fakty(lista_faktow):
    zmiana = True
    while zmiana:
        zmiana = False
        for r in reguly:
            if r["wniosek"] not in lista_faktow:
                war_ok = all(w in lista_faktow for w in r["warunki"])
                neg_ok = all(n not in lista_faktow for n in r["negacje"])
                if war_ok and neg_ok:
                    lista_faktow.append(r["wniosek"])
                    zmiana = True
    return lista_faktow

def sprawdz_naf(fakt, lista_faktow):
    print(f"  Probuje udowodnic \"{fakt}\"...")
    kopia = list(lista_faktow)
    wyprowadzone = wyprowadz_fakty(kopia)
    if fakt in wyprowadzone:
        print(f"  \"{fakt}\" da sie wyprowadzic z faktow")
        print(f"  NAF: ~\"{fakt}\" jest FALSZYWE")
        return False
    else:
        print(f"  \"{fakt}\" NIE da sie wyprowadzic z faktow")
        print(f"  NAF: ~\"{fakt}\" jest PRAWDZIWE (bo brak dowodu na \"{fakt}\")")
        return True


print("=== NEGATION AS FAILURE (NAF) ===")
print("Fakty poczatkowe:", fakty)
print()

print("--- Test 1: ~\"prawidlowa predkosc\" ---")
wynik1 = sprawdz_naf("prawidlowa predkosc", fakty)
print(f"Wynik: ~\"prawidlowa predkosc\" = {wynik1}")
print()

print("--- Test 2: ~\"trudne warunki\" ---")
wynik2 = sprawdz_naf("trudne warunki", fakty)
print(f"Wynik: ~\"trudne warunki\" = {wynik2}")
print()

print("--- Test 3: ~\"snieg\" ---")
wynik3 = sprawdz_naf("snieg", fakty)
print(f"Wynik: ~\"snieg\" = {wynik3}")
print()

print("=== Wnioskowanie z NAF ===")
print()
print("Fakty:", fakty)

wyprowadzone = wyprowadz_fakty(list(fakty))
print("Po wnioskowanie:", wyprowadzone)
print()

print("Regula 2: ~\"prawidlowa predkosc\" -> \"nalezy zwolnic\"")
if "prawidlowa predkosc" not in wyprowadzone:
    print("  \"prawidlowa predkosc\" brak w faktach -> NAF potwierdza negacje")
    print("  Wniosek: \"nalezy zwolnic\"")
else:
    print("  \"prawidlowa predkosc\" jest w faktach -> NAF nie potwierdza negacji")
    print("  Regula 2 NIE odpala")
print()

print("Regula 4: \"prawidlowa predkosc\" && ~\"trudne warunki\" -> \"jedz jak chcesz\"")
if "prawidlowa predkosc" in wyprowadzone and "trudne warunki" not in wyprowadzone:
    print("  Oba warunki spelnione -> Wniosek: \"jedz jak chcesz\"")
elif "prawidlowa predkosc" not in wyprowadzone:
    print("  \"prawidlowa predkosc\" brak -> regula NIE odpala")
else:
    print("  \"trudne warunki\" jest w faktach -> NAF nie potwierdza ~\"trudne warunki\"")
    print("  Regula 4 NIE odpala")
