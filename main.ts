import { existsSync, readFileSync } from "node:fs";

type Literal = string;
type RuleKind = "strict" | "defeasible";
type Attack = readonly [string, string];

interface Rule {
  name: string;
  premises: Literal[];
  conclusion: Literal;
  kind: RuleKind;
}

interface KnowledgeBase {
  strictFacts: Set<Literal>;
  defeasibleFacts: Set<Literal>;
  strictRules: Map<string, Rule>;
  defeasibleRules: Map<string, Rule>;
}

interface ArgumentNode {
  id: string;
  conclusion: Literal;
  usedRules: Set<string>;
  basePremises: Set<Literal>;
  subarguments: string[];
}

function stripQuotes(value: string): string {
  const text = value.trim();
  const first = text[0];
  const last = text[text.length - 1];

  if ((first === `"` && last === `"`) || (first === `'` && last === `'`)) {
    return text.slice(1, -1).trim();
  }

  return text;
}

function cleanLiteral(raw: string): Literal {
  let value = raw.trim().replace(/[.;]+$/g, "").trim();
  let negated = false;

  if (value.startsWith("~")) {
    negated = true;
    value = value.slice(1).trim();
  }

  const literal = stripQuotes(value);
  return negated ? `~${literal}` : literal;
}

function oppositeOf(literal: Literal): Literal {
  return literal.startsWith("~") ? literal.slice(1).trim() : `~${literal}`;
}

function areOpposite(left: Literal, right: Literal): boolean {
  return oppositeOf(left) === right || oppositeOf(right) === left;
}

function splitList(text: string): string[] {
  const parts: string[] = [];
  let buffer = "";
  let quote: string | null = null;

  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    const nextTwo = text.slice(i, i + 2);

    if (quote) {
      buffer += char;
      if (char === quote) {
        quote = null;
      }
      continue;
    }

    if (char === `"` || char === `'`) {
      quote = char;
      buffer += char;
      continue;
    }

    if (char === "," || nextTwo === "&&") {
      const item = buffer.trim();
      if (item) {
        parts.push(item);
      }
      buffer = "";
      if (nextTwo === "&&") {
        i += 1;
      }
      continue;
    }

    buffer += char;
  }

  const item = buffer.trim();
  if (item) {
    parts.push(item);
  }

  return parts;
}

function parseLiteralSet(raw: string | undefined): Set<Literal> {
  if (!raw) {
    return new Set();
  }

  return new Set(splitList(raw).map(cleanLiteral).filter(Boolean));
}

function makeRuleName(rawName: string, rules: Map<string, Rule>): string {
  const normalized = rawName.trim();
  const base = /^\d+$/.test(normalized) ? `r${normalized}` : normalized;

  if (!rules.has(base)) {
    return base;
  }

  let suffix = 2;
  while (rules.has(`${base}_${suffix}`)) {
    suffix += 1;
  }

  return `${base}_${suffix}`;
}

function parseAspicStyle(content: string): KnowledgeBase | null {
  if (!/\b(?:Kn|Kp|Rs|Rd)\s*=/.test(content)) {
    return null;
  }

  const readFactLine = (name: "Kn" | "Kp"): Set<Literal> => {
    const match = content.match(new RegExp(`\\b${name}\\s*=\\s*([^\\r\\n}]*)`));
    return parseLiteralSet(match?.[1]);
  };

  const readRuleBlock = (name: "Rs" | "Rd", kind: RuleKind): Map<string, Rule> => {
    const rules = new Map<string, Rule>();
    const block = content.match(new RegExp(`\\b${name}\\s*=\\s*\\{([\\s\\S]*?)\\}`, "m"));

    if (!block) {
      return rules;
    }

    const rulePattern =
      /([A-Za-z_][\w-]*)\s*:\s*([\s\S]*?)\s*(?:=>|->)\s*([\s\S]*?)(?=(?:[.,;]\s*)?[A-Za-z_][\w-]*\s*:|$)/g;
    let match: RegExpExecArray | null;

    while ((match = rulePattern.exec(block[1])) !== null) {
      const nameFromFile = match[1];
      const ruleName = makeRuleName(nameFromFile, rules);
      const premises = splitList(match[2]).map(cleanLiteral).filter(Boolean);
      const conclusion = cleanLiteral(match[3]);

      rules.set(ruleName, { name: ruleName, premises, conclusion, kind });
    }

    return rules;
  };

  return {
    strictFacts: readFactLine("Kn"),
    defeasibleFacts: readFactLine("Kp"),
    strictRules: readRuleBlock("Rs", "strict"),
    defeasibleRules: readRuleBlock("Rd", "defeasible"),
  };
}

function parseSimpleRuleFile(content: string): KnowledgeBase {
  const strictRules = new Map<string, Rule>();
  const defeasibleRules = new Map<string, Rule>();
  const facts = new Set<Literal>();

  for (const line of content.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed) {
      continue;
    }

    const factsMatch = trimmed.match(/^Fakty\s*:\s*(.+)$/i);
    if (factsMatch) {
      for (const fact of parseLiteralSet(factsMatch[1])) {
        facts.add(fact);
      }
      continue;
    }

    const ruleMatch = trimmed.match(/^([^:#]+)\s*:\s*(.+?)\s*->\s*(.+)$/);
    if (!ruleMatch) {
      continue;
    }

    const ruleName = makeRuleName(ruleMatch[1], defeasibleRules);
    defeasibleRules.set(ruleName, {
      name: ruleName,
      premises: splitList(ruleMatch[2]).map(cleanLiteral).filter(Boolean),
      conclusion: cleanLiteral(ruleMatch[3]),
      kind: "defeasible",
    });
  }

  return {
    strictFacts: new Set(),
    defeasibleFacts: facts,
    strictRules,
    defeasibleRules,
  };
}

function parseKnowledgeBase(content: string): KnowledgeBase {
  return parseAspicStyle(content) ?? parseSimpleRuleFile(content);
}

function demoKnowledgeBase(): KnowledgeBase {
  return {
    strictFacts: new Set(["e"]),
    defeasibleFacts: new Set(["a", "b", "c", "d"]),
    strictRules: new Map([
      ["r1", { name: "r1", premises: ["e"], conclusion: "f", kind: "strict" }],
    ]),
    defeasibleRules: new Map([
      ["r2", { name: "r2", premises: ["a", "b"], conclusion: "g", kind: "defeasible" }],
      ["r3", { name: "r3", premises: ["c"], conclusion: "~g", kind: "defeasible" }],
      ["r4", { name: "r4", premises: ["c", "d"], conclusion: "h", kind: "defeasible" }],
      ["r5", { name: "r5", premises: ["g", "h"], conclusion: "w", kind: "defeasible" }],
      ["r6", { name: "r6", premises: ["f"], conclusion: "~r3", kind: "defeasible" }],
    ]),
  };
}

function unionSets<T>(...sets: Set<T>[]): Set<T> {
  const result = new Set<T>();

  for (const set of sets) {
    for (const item of set) {
      result.add(item);
    }
  }

  return result;
}

function sameSet<T>(left: Set<T>, right: Set<T>): boolean {
  if (left.size !== right.size) {
    return false;
  }

  for (const value of left) {
    if (!right.has(value)) {
      return false;
    }
  }

  return true;
}

function cartesianProduct<T>(groups: T[][]): T[][] {
  if (groups.length === 0) {
    return [[]];
  }

  return groups.reduce<T[][]>(
    (partial, group) => partial.flatMap((prefix) => group.map((item) => [...prefix, item])),
    [[]],
  );
}

function buildArguments(base: KnowledgeBase): ArgumentNode[] {
  const argumentsList: ArgumentNode[] = [];

  const addBaseArgument = (literal: Literal): void => {
    argumentsList.push({
      id: `A${argumentsList.length}`,
      conclusion: literal,
      usedRules: new Set(),
      basePremises: new Set([literal]),
      subarguments: [],
    });
  };

  for (const literal of base.strictFacts) {
    addBaseArgument(literal);
  }

  for (const literal of base.defeasibleFacts) {
    addBaseArgument(literal);
  }

  const allRules = [...base.strictRules.values(), ...base.defeasibleRules.values()];
  let changed = true;

  while (changed) {
    changed = false;

    for (const rule of allRules) {
      const matchingArguments = rule.premises.map((premise) =>
        argumentsList.filter((argument) => argument.conclusion === premise),
      );

      if (matchingArguments.some((group) => group.length === 0)) {
        continue;
      }

      for (const variant of cartesianProduct(matchingArguments)) {
        const usedRules = unionSets(new Set([rule.name]), ...variant.map((argument) => argument.usedRules));
        const basePremises = unionSets(...variant.map((argument) => argument.basePremises));
        const subarguments = variant.map((argument) => argument.id);

        const alreadyExists = argumentsList.some(
          (argument) =>
            argument.conclusion === rule.conclusion &&
            sameSet(argument.usedRules, usedRules) &&
            sameSet(argument.basePremises, basePremises),
        );

        if (!alreadyExists) {
          argumentsList.push({
            id: `A${argumentsList.length}`,
            conclusion: rule.conclusion,
            usedRules,
            basePremises,
            subarguments,
          });
          changed = true;
        }
      }
    }
  }

  return argumentsList;
}

function buildAttacks(argumentsList: ArgumentNode[], base: KnowledgeBase): Attack[] {
  const attacks = new Map<string, Attack>();

  const rememberAttack = (source: string, target: string): void => {
    attacks.set(`${source}->${target}`, [source, target]);
  };

  const isRuleDefeasible = (ruleName: string): boolean => base.defeasibleRules.has(ruleName);

  for (const source of argumentsList) {
    for (const target of argumentsList) {
      if (
        areOpposite(source.conclusion, target.conclusion) &&
        ([...target.usedRules].some(isRuleDefeasible) || base.defeasibleFacts.has(target.conclusion))
      ) {
        rememberAttack(source.id, target.id);
      }

      for (const premise of target.basePremises) {
        if (source.conclusion === oppositeOf(premise)) {
          rememberAttack(source.id, target.id);
        }
      }

      for (const ruleName of target.usedRules) {
        if (source.conclusion === `~${ruleName}`) {
          rememberAttack(source.id, target.id);
        }
      }
    }
  }

  return [...attacks.values()].sort((left, right) => left[0].localeCompare(right[0]) || left[1].localeCompare(right[1]));
}

function powerSet<T>(items: T[]): T[][] {
  const result: T[][] = [[]];

  for (const item of items) {
    const additions = result.map((subset) => [...subset, item]);
    result.push(...additions);
  }

  return result;
}

function isSubset<T>(small: T[], big: T[]): boolean {
  const bigSet = new Set(big);
  return small.every((item) => bigSet.has(item));
}

function preferredExtensions(argumentIds: string[], attacks: Attack[]): string[][] {
  const attackKeys = new Set(attacks.map(([source, target]) => `${source}->${target}`));
  const admissible: string[][] = [];

  for (const subset of powerSet(argumentIds)) {
    let conflictFree = true;

    for (const left of subset) {
      for (const right of subset) {
        if (attackKeys.has(`${left}->${right}`)) {
          conflictFree = false;
        }
      }
    }

    if (!conflictFree) {
      continue;
    }

    let defended = true;
    for (const member of subset) {
      const attackers = attacks.filter(([, target]) => target === member).map(([source]) => source);
      const everyAttackAnswered = attackers.every((attacker) =>
        subset.some((defender) => attackKeys.has(`${defender}->${attacker}`)),
      );

      if (!everyAttackAnswered) {
        defended = false;
        break;
      }
    }

    if (defended) {
      admissible.push(subset);
    }
  }

  return admissible.filter(
    (candidate) => !admissible.some((other) => candidate.length < other.length && isSubset(candidate, other)),
  );
}

function groundedExtension(argumentIds: string[], attacks: Attack[]): Set<string> {
  const accepted = new Set<string>();
  const attackKeys = new Set(attacks.map(([source, target]) => `${source}->${target}`));

  while (true) {
    const nextRound = new Set<string>();

    for (const argumentId of argumentIds) {
      if (accepted.has(argumentId)) {
        continue;
      }

      const attackers = attacks.filter(([, target]) => target === argumentId).map(([source]) => source);
      const defended =
        attackers.length === 0 ||
        attackers.every((attacker) => [...accepted].some((defender) => attackKeys.has(`${defender}->${attacker}`)));

      if (defended) {
        nextRound.add(argumentId);
      }
    }

    if (nextRound.size === 0) {
      break;
    }

    for (const argumentId of nextRound) {
      accepted.add(argumentId);
    }
  }

  return accepted;
}

function printableSet(values: Iterable<string>): string {
  return `[${[...values].sort((left, right) => left.localeCompare(right)).join(", ")}]`;
}

function showResult(argumentsList: ArgumentNode[], attacks: Attack[]): void {
  const argumentIds = argumentsList.map((argument) => argument.id);
  const conclusionById = new Map(argumentsList.map((argument) => [argument.id, argument.conclusion]));

  console.log("--- ARGUMENTY ---");
  for (const argument of argumentsList) {
    console.log(
      `${argument.id} | wniosek: ${argument.conclusion} | reguly: ${printableSet(argument.usedRules)} | sub: ${printableSet(argument.subarguments)}`,
    );
  }

  console.log("\n--- ATAKI ---");
  if (attacks.length === 0) {
    console.log("brak");
  } else {
    for (const [source, target] of attacks) {
      console.log(`${source} atakuje ${target}`);
    }
  }

  console.log("\n--- PREFERRED ---");
  preferredExtensions(argumentIds, attacks).forEach((extension, index) => {
    const conclusions = extension.map((id) => conclusionById.get(id) ?? id);
    console.log(`${index + 1}: ${printableSet(conclusions)}`);
  });

  console.log("\n--- GROUNDED ---");
  const grounded = groundedExtension(argumentIds, attacks);
  console.log(printableSet([...grounded].map((id) => conclusionById.get(id) ?? id)));
}

function loadKnowledgeBase(): KnowledgeBase {
  const filesFromCommandLine = process.argv
    .slice(2)
    .filter((path) => path.toLowerCase().endsWith(".bw"));

  const candidates = [
    ...filesFromCommandLine,
    "aspic-baza-wiedzy.bw",
  ].filter((path): path is string => Boolean(path));

  for (const path of candidates) {
    if (existsSync(path)) {
      console.log(`Wczytano baze wiedzy: ${path}\n`);
      return parseKnowledgeBase(readFileSync(path, "utf8"));
    }
  }

  console.log("Nie znaleziono pliku .bw, uruchamiam dane demonstracyjne.\n");
  return demoKnowledgeBase();
}

const knowledgeBase = loadKnowledgeBase();
const argumentsList = buildArguments(knowledgeBase);
const attacks = buildAttacks(argumentsList, knowledgeBase);

showResult(argumentsList, attacks);
