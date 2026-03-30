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


def wyprowadz_wszystko(lista_faktow):
    zmiana = True
    while zmiana:
        zmiana = False
        for r in reguly:
            if r["negacje"]:
                continue
            war_ok = all(w in lista_faktow for w in r["warunki"])
            if war_ok and r["wniosek"] not in lista_faktow:
                lista_faktow.append(r["wniosek"])
                zmiana = True
    zmiana = True
    while zmiana:
        zmiana = False
        for r in reguly:
            if not r["negacje"]:
                continue
            war_ok = all(w in lista_faktow for w in r["warunki"])
            neg_ok = all(n not in lista_faktow for n in r["negacje"])
            if war_ok and neg_ok and r["wniosek"] not in lista_faktow:
                lista_faktow.append(r["wniosek"])
                zmiana = True
    return lista_faktow


def naf(fakt):
    print(f"NAF: Czy ~\"{fakt}\" jest prawdziwe?")
    print(f"  Probuje udowodnic \"{fakt}\" z bazy wiedzy...")
    wszystkie = wyprowadz_wszystko(list(fakty))
    if fakt in wszystkie:
        print(f"  \"{fakt}\" UDOWODNIONE -> ~\"{fakt}\" = FALSZ")
        return False
    else:
        print(f"  \"{fakt}\" NIEUDOWODNIONE -> ~\"{fakt}\" = PRAWDA")
        return True


print("=== NEGATION AS FAILURE ===")
print("Fakty:", fakty)
print()

naf("prawidlowa predkosc")
print()
naf("trudne warunki")
print()
naf("snieg")
print()

print("=== Jak NAF wplywa na reguly ===")
print()
wszystkie = wyprowadz_wszystko(list(fakty))
print("Wyprowadzone fakty:", wszystkie)
print()

print("Regula 2: ~prawidlowa_predkosc -> nalezy zwolnic")
print(f"  prawidlowa predkosc jest w faktach -> NAF: negacja FALSZYWA")
print(f"  Regula 2 NIE odpala")
print()

print("Regula 4: prawidlowa_predkosc && ~trudne_warunki -> jedz jak chcesz")
print(f"  trudne warunki sa w faktach -> NAF: negacja FALSZYWA")
print(f"  Regula 4 NIE odpala")
print()

print("=== Kontrprzyklad: bez mgly ===")
fakty2 = ["ograniczenie do 50", "szybkosc ponizej 50"]
wszystkie2 = wyprowadz_wszystko(list(fakty2))
print(f"Fakty: {fakty2}")
print(f"Wyprowadzone: {wszystkie2}")
print(f"~trudne_warunki = PRAWDA (bo nie ma mgly ani sniegu)")
print(f"Regula 4 ODPALA -> jedz jak chcesz")
