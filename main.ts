import { existsSync, readFileSync } from "node:fs";

type Rule = { id: string; pre: string[]; out: string };
type Arg = { id: string; out: string; rules: Set<string>; prem: Set<string>; sub: string[] };
type Attack = [string, string];

const FILE = "aspic-baza-wiedzy.bw";

const strip = (s: string) => s.trim().replace(/^["']|["']$/g, "").trim();
const clean = (s: string) => {
  let x = s.trim().replace(/[.;]+$/g, "").trim();
  const neg = x.startsWith("~");
  if (neg) x = x.slice(1).trim();
  return (neg ? "~" : "") + strip(x);
};
const split = (s = "") => s.split(",").map(clean).filter(Boolean);
const opposite = (s: string) => (s.startsWith("~") ? s.slice(1) : `~${s}`);
const fmt = (xs: Iterable<string>) => `[${[...xs].sort((a, b) => a.localeCompare(b)).join(", ")}]`;

function product<T>(groups: T[][]): T[][] {
  return groups.reduce<T[][]>((acc, group) => acc.flatMap((a) => group.map((x) => [...a, x])), [[]]);
}

function powerSet<T>(items: T[]): T[][] {
  const sets: T[][] = [[]];
  for (const item of items) {
    for (const set of [...sets]) sets.push([...set, item]);
  }
  return sets;
}

function same<T>(a: Set<T>, b: Set<T>) {
  return a.size === b.size && [...a].every((x) => b.has(x));
}

function readFacts(src: string, name: "Kn" | "Kp") {
  const m = src.match(new RegExp(`^[ \\t]*${name}[ \\t]*=[ \\t]*(.*)$`, "m"));
  return new Set(split(m?.[1]));
}

function readRules(src: string, name: "Rs" | "Rd") {
  const rules = new Map<string, Rule>();
  const block = src.match(new RegExp(`\\b${name}[ \\t]*=[ \\t]*\\{([\\s\\S]*?)\\}`));
  if (!block) return rules;

  const rx = /([A-Za-z_][\w-]*)\s*:\s*([\s\S]*?)\s*(?:=>|->)\s*([\s\S]*?)(?=(?:[.,;]\s*)?[A-Za-z_][\w-]*\s*:|$)/g;
  for (const m of block[1].matchAll(rx)) {
    rules.set(m[1], { id: m[1], pre: split(m[2]), out: clean(m[3]) });
  }
  return rules;
}

function parseBase(path: string) {
  const src = readFileSync(path, "utf8");
  return {
    kn: readFacts(src, "Kn"),
    kp: readFacts(src, "Kp"),
    rs: readRules(src, "Rs"),
    rd: readRules(src, "Rd"),
  };
}

function buildArgs(base: ReturnType<typeof parseBase>) {
  const args: Arg[] = [];
  const add = (out: string, rules = new Set<string>(), prem = new Set([out]), sub: string[] = []) =>
    args.push({ id: `A${args.length}`, out, rules, prem, sub });

  [...base.kn, ...base.kp].forEach((fact) => add(fact));

  const rules = [...base.rs.values(), ...base.rd.values()];
  let changed = true;
  while (changed) {
    changed = false;
    for (const rule of rules) {
      const options = rule.pre.map((p) => args.filter((a) => a.out === p));
      if (options.some((o) => o.length === 0)) continue;

      for (const combo of product(options)) {
        const used = new Set([rule.id, ...combo.flatMap((a) => [...a.rules])]);
        const prem = new Set(combo.flatMap((a) => [...a.prem]));
        const exists = args.some((a) => a.out === rule.out && same(a.rules, used) && same(a.prem, prem));
        if (!exists) {
          add(rule.out, used, prem, combo.map((a) => a.id));
          changed = true;
        }
      }
    }
  }
  return args;
}

function buildAttacks(args: Arg[], base: ReturnType<typeof parseBase>) {
  const attacks = new Map<string, Attack>();
  const add = (a: string, b: string) => attacks.set(`${a}->${b}`, [a, b]);

  for (const a of args) {
    for (const b of args) {
      const bIsDefeasible = [...b.rules].some((r) => base.rd.has(r)) || base.kp.has(b.out);
      if (opposite(a.out) === b.out && bIsDefeasible) add(a.id, b.id);
      for (const p of b.prem) if (a.out === opposite(p)) add(a.id, b.id);
      for (const r of b.rules) if (a.out === `~${r}`) add(a.id, b.id);
    }
  }

  return [...attacks.values()].sort((x, y) => x.join("").localeCompare(y.join("")));
}

function preferred(ids: string[], attacks: Attack[]) {
  const atk = new Set(attacks.map(([a, b]) => `${a}->${b}`));
  const admissible = powerSet(ids).filter((set) => {
    const conflict = set.some((a) => set.some((b) => atk.has(`${a}->${b}`)));
    if (conflict) return false;

    return set.every((arg) =>
      attacks
        .filter(([, target]) => target === arg)
        .every(([attacker]) => set.some((defender) => atk.has(`${defender}->${attacker}`))),
    );
  });

  return admissible.filter((a) => !admissible.some((b) => a.length < b.length && a.every((x) => b.includes(x))));
}

function grounded(ids: string[], attacks: Attack[]) {
  const accepted = new Set<string>();
  const atk = new Set(attacks.map(([a, b]) => `${a}->${b}`));

  while (true) {
    const next = ids.filter(
      (id) =>
        !accepted.has(id) &&
        attacks
          .filter(([, target]) => target === id)
          .every(([attacker]) => [...accepted].some((defender) => atk.has(`${defender}->${attacker}`))),
    );
    if (!next.length) break;
    next.forEach((id) => accepted.add(id));
  }

  return accepted;
}

function print(args: Arg[], attacks: Attack[]) {
  const ids = args.map((a) => a.id);
  const concl = new Map(args.map((a) => [a.id, a.out]));
  const byId = (id: string) => concl.get(id) ?? id;

  console.log("--- ARGUMENTY ---");
  for (const a of args) {
    console.log(`${a.id} > wniosek: ${a.out} > reguly: ${fmt(a.rules)} > sub: ${fmt(a.sub)}`);
  }

  console.log("\n--- ATAKI ---");
  attacks.length ? attacks.forEach(([a, b]) => console.log(`${a} atakuje ${b}`)) : console.log("brak");

  console.log("\n--- PREFERRED ---");
  preferred(ids, attacks).forEach((e, i) => console.log(`${i + 1}: ${fmt(e.map(byId))}`));

  console.log("\n--- GROUNDED ---");
  console.log(fmt([...grounded(ids, attacks)].map(byId)));
}

if (!existsSync(FILE)) throw new Error(`Brak pliku ${FILE}`);

console.log(`Wczytano baze wiedzy: ${FILE}\n`);
const base = parseBase(FILE);
const args = buildArgs(base);
const attacks = buildAttacks(args, base);
print(args, attacks);
