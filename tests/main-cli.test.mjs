import { mkdtemp, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";

test("main.ts reads the knowledge base path from the CLI argument", async () => {
  const dir = await mkdtemp(join(tmpdir(), "aspic-cli-"));
  const kb = join(dir, "custom.bw");
  await writeFile(kb, "Kp = x\nKn = y\nRs = {}\nRd = {}\n", "utf8");

  const result = spawnSync(process.execPath, ["--experimental-strip-types", "main.ts", kb], {
    cwd: new URL("..", import.meta.url),
    encoding: "utf8",
  });

  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, new RegExp(`Wczytano baze wiedzy: ${kb.replace(/[\\^$.*+?()[\]{}|]/g, "\\$&")}`));
  assert.match(result.stdout, /wniosek: x/);
  assert.match(result.stdout, /wniosek: y/);
});
