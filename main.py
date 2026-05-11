import re
from itertools import product

def parse_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    def clean_split(text):
        if not text: return set()
        return {s.strip() for s in text.split(',') if s.strip()}

    kp_match = re.search(r'Kp\s*=\s*(.*)', content)
    kn_match = re.search(r'Kn\s*=\s*(.*)', content)

    Kp = clean_split(kp_match.group(1)) if kp_match else set()
    Kn = clean_split(kn_match.group(1)) if kn_match else set()

    def extract_rules(pattern, content):
        rules_dict = {}
        match = re.search(pattern, content, re.DOTALL)
        if match:
            rules_block = match.group(1)
            rules_list = re.findall(r'(\w+)\s*:\s*([^=>\-]+)\s*[=-]>\s*([^,.\s}]+)', rules_block)
            for r_id, premises_raw, conclusion in rules_list:
                premises = tuple(p.strip() for p in premises_raw.split(',') if p.strip())
                rules_dict[r_id] = (premises, conclusion.strip())
        return rules_dict

    Rs = extract_rules(r'Rs\s*=\s*\{(.*?)\}', content)
    Rd = extract_rules(r'Rd\s*=\s*\{(.*?)\}', content)

    return Kn, Kp, Rs, Rd

def preferred(args_x, attacks_x):
    subsets = [[]]
    for element in args_x:
        new_subsets = []
        for current_subset in subsets:
            new_subsets.append(current_subset + [element])
        subsets.extend(new_subsets)

    dopuszczalne = []
    for subset in subsets:
        jest_ok = True
        for a in subset:
            for b in subset:
                if (a, b) in attacks_x:
                    jest_ok = False
                    break
            if not jest_ok: break
        if not jest_ok: continue

        czy_broni_wszystkich = True
        for element in subset:
            for atk_src, atk_target in attacks_x:
                if atk_target == element:
                    czy_odparty_atak = any((obronca, atk_src) in attacks_x for obronca in subset)
                    if not czy_odparty_atak:
                        czy_broni_wszystkich = False
                        break
            if not czy_broni_wszystkich: break
        if czy_broni_wszystkich: dopuszczalne.append(subset)

    wynik = []
    for s1 in dopuszczalne:
        if not any(set(s1).issubset(set(s2)) and len(s2) > len(s1) for s2 in dopuszczalne):
            if s1 not in wynik: wynik.append(s1)
    return wynik

def grounded(args_x, attacks_x):
    in_set = set()
    while True:
        candidates = set()
        for arg in args_x:
            if arg in in_set: continue
            attackers = [src for src, target in attacks_x if target == arg]
            if not attackers or all(any((obronca, atk) in attacks_x for obronca in in_set) for atk in attackers):
                candidates.add(arg)
        if not candidates: break
        in_set.update(candidates)
    return in_set

def aspic_algorithm(Kn={}, Kp={}, Rs={}, Rd={}):
    args = []
    for p in Kn: args.append({'id': 'A' + str(len(args)), 'wniosek': p, 'rules': set(), 'p': {p}, 'sub': []})
    for p in Kp: args.append({'id': 'A' + str(len(args)), 'wniosek': p, 'rules': set(), 'p': {p}, 'sub': []})

    rules = {**Rs, **Rd}
    changed = True
    while changed:
        changed = False
        for r_name, (przeslanki, wniosek) in rules.items():
            opcje = [[a for a in args if a['wniosek'] == p] for p in przeslanki]
            if all(opcje) and len(opcje) == len(przeslanki):
                for komb in product(*opcje):
                    nowe_reguly, nowe_przeslanki, sub_id = {r_name}, set(), []
                    for k in komb:
                        nowe_reguly.update(k['rules'])
                        nowe_przeslanki.update(k['p'])
                        sub_id.append(k['id'])
                    if not any(a['wniosek'] == wniosek and a['rules'] == nowe_reguly and a['p'] == nowe_przeslanki for a in args):
                        args.append({'id': 'A' + str(len(args)), 'wniosek': wniosek, 'rules': nowe_reguly, 'p': nowe_przeslanki, 'sub': sub_id})
                        changed = True

    attacks = []
    for a in args:
        for b in args:
            c1, c2 = a['wniosek'], b['wniosek']
            is_neg = (c1 == "~" + c2) or (c2 == "~" + c1)
            if is_neg:
                if any(r in Rd for r in b['rules']) or c2 in Kp: attacks.append((a['id'], b['id']))
            for p in b['p']:
                if c1 == "~" + p: attacks.append((a['id'], b['id']))
            for r in b['rules']:
                if c1 == "~" + r: attacks.append((a['id'], b['id']))
    return args, list(set(attacks))

def evaluate_abstract_semantics(aspic_args, aspic_attacks):
    args_abstract = {a['id'] for a in aspic_args}
    attacks_abstract = set(aspic_attacks)
    pref = preferred(args_abstract, attacks_abstract)
    ground = grounded(args_abstract, attacks_abstract)
    id_to_wn = {a['id']: a['wniosek'] for a in aspic_args}

    print("\n--- PREFERRED ---")
    for i, ext in enumerate(pref):
        print(f"{i + 1}: {sorted([id_to_wn[arg] for arg in ext])}")
    print("\n--- GROUNDED ---")
    print(f"{sorted([id_to_wn[arg] for arg in ground])}")


Kn = {'e'}
Kp = {'a', 'b', 'c', 'd'}
Rs = {'r1': (('e',), 'f')}
Rd = {'r2': (('a', 'b'), 'g'), 'r3': (('c',), '~g'), 'r4': (('c', 'd'), 'h'), 'r5': (('g', 'h'), 'w'), 'r6': (('f',), '~r3')}

Kn3 = {'pracownik'}
Kp3 = {'skarga_klienta', 'brak_dowodow', 'dobra_historia', 'wada_systemu'}
Rs3 = {'rs1': (('pracownik', 'zwolniony'), 'utrata_premii')}
Rd3 = {'r1': (('skarga_klienta',), 'winny'), 'r2': (('winny',), 'zwolniony'), 'r3': (('brak_dowodow',), '~winny'), 'r4': (('dobra_historia',), '~r2'), 'r5': (('wada_systemu',), '~skarga_klienta')}



try:
    Kn_f, Kp_f, Rs_f, Rd_f = parse_file('aspic-baza-wiedzy.bw')
    wynik_args, wynik_ataki = aspic_algorithm(Kn_f, Kp_f, Rs_f, Rd_f)

    print("--- ARGUMENTY ---")
    for a in wynik_args:
        print(f"{a['id']} | wniosek: {a['wniosek']} | reguły: {list(a['rules'])} | sub: {a['sub']}")

    print("\n--- ATAKI ---")
    for atk in wynik_ataki:
        print(f"{atk[0]} atakuje {atk[1]}")

    evaluate_abstract_semantics(wynik_args, wynik_ataki)
except FileNotFoundError:
    print("Plik 'dane.txt' nie istnieje. Stwórz go w formacie wskazanym w zadaniu.")