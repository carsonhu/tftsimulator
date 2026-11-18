// Runs set19/worker.js for real (Pyodide 0.27.6 from npm, the worker's pinned version) with fetch() served from
// the repo folder, and drives its RPCs the way app.js does. Adds a fake second build to the index to check that a
// build is fetched only when a request names it.
//     cd tools/browser_check && npm install && node worker_e2e.js     (repo root by default)
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const { loadPyodide } = require("pyodide");

const ROOT = process.argv[2] || path.resolve(__dirname, "..", "..");
const realIndex = JSON.parse(fs.readFileSync(path.join(ROOT, "builds/index.json"), "utf8"));
const newest = realIndex.builds[0];
const FAKE = { version: "rls-19.1.0.1111111.Set19.Shipping.pbe", install: "PBE", pak_mtime: "2026-11-16T09:05:00",
               file: "fake.json" };
const index = { builds: [...realIndex.builds, FAKE] };
const fetched = [];

function respond(text) {
  return { ok: true, status: 200, text: async () => text };
}

async function fakeFetch(p) {
  fetched.push(p);
  if (p === "builds/index.json") return respond(JSON.stringify(index));
  if (p === "builds/fake.json") {
    const d = JSON.parse(fs.readFileSync(path.join(ROOT, "builds", newest.file), "utf8"));
    d.meta.version = FAKE.version;
    d.champions.DA_Neeko19.ability.rows.DamageAP = [1, 2, 3]; // so a run on it is visibly different
    return respond(JSON.stringify(d));
  }
  const f = path.join(ROOT, p);
  if (!fs.existsSync(f)) return { ok: false, status: 404, text: async () => "" };
  return respond(fs.readFileSync(f, "utf8"));
}

const messages = [];
const waiters = new Map();
const ctx = {
  importScripts: () => {},
  loadPyodide: () => loadPyodide(),
  fetch: fakeFetch,
  performance,
  console,
  JSON,
  Map,
  Set,
  Promise,
  Error,
  String,
  Math,
  postMessage: (m) => {
    messages.push(m);
    if (m.id !== undefined && waiters.has(m.id)) waiters.get(m.id)(m);
  },
};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(ROOT, "worker.js"), "utf8"), ctx);

let nextId = 0;
function rpc(cmd, arg) {
  const id = nextId++;
  return new Promise((res) => {
    waiters.set(id, res);
    ctx.onmessage({ data: { id, cmd, arg } });
  });
}

let fails = 0;
function check(name, ok, detail) {
  console.log((ok ? "PASS " : "FAIL ") + name + (ok ? "" : "  " + detail));
  if (!ok) fails++;
}

(async () => {
  const cat = await rpc("catalog");
  check("boot", messages.some((m) => m.type === "ready"), JSON.stringify(messages.filter((m) => m.type)));
  check("catalog ok", cat.ok, cat.error);
  const c = JSON.parse(cat.data);
  check("catalog lists both builds, newest first", c.builds.map((b) => b.version).join() ===
        [newest.version, FAKE.version].join(), JSON.stringify(c.builds));
  console.log("  labels:", c.builds.map((b) => b.label));
  check("champions", c.champions.map((x) => x.name).join() === "Neeko", JSON.stringify(c.champions));
  check("boot fetched the index and only the newest build",
        fetched.includes("builds/" + newest.file) && !fetched.includes("builds/fake.json"), fetched.join());

  const cfg = { champ: "Neeko", level: 1, items: ["NoItem", "NoItem", "NoItem"], buffs: [],
                enemy: { hp: 1800, armor: 100, mr: 100 }, t: 30, slice: "Craftable", stage: "4-1",
                build: newest.version };
  const info = await rpc("champInfo", JSON.stringify(cfg));
  check("champInfo on the newest build", info.ok && JSON.parse(info.data).stats.build === newest.version,
        info.error || info.data.slice(0, 300));
  const run = await rpc("run", JSON.stringify(cfg));
  check("run on the newest build", run.ok && JSON.parse(run.data).rows.length > 0, run.error);
  const dpsNew = run.ok ? JSON.parse(run.data).rows[0].dps : null;
  console.log("  dps (newest):", JSON.stringify(dpsNew));

  const old = Object.assign({}, cfg, { build: FAKE.version });
  const info2 = await rpc("champInfo", JSON.stringify(old));
  check("another build loads on first use", info2.ok && JSON.parse(info2.data).stats.build === FAKE.version,
        info2.error || "");
  const run2 = await rpc("run", JSON.stringify(old));
  const dpsOld = run2.ok ? JSON.parse(run2.data).rows[0].dps : null;
  console.log("  dps (fake build, DamageAP 1/2/3):", JSON.stringify(dpsOld));
  check("its numbers are that build's", run2.ok && JSON.stringify(dpsOld) !== JSON.stringify(dpsNew), run2.error);
  await rpc("run", JSON.stringify(old));
  check("each build fetched once", fetched.filter((p) => p === "builds/fake.json").length === 1, fetched.join());

  const bad = await rpc("run", JSON.stringify(Object.assign({}, cfg, { build: "no-such-build" })));
  check("an unknown build fails with its name", !bad.ok && bad.error.includes("no-such-build"), bad.error);
  const none = Object.assign({}, cfg);
  delete none.build;
  const run3 = await rpc("run", JSON.stringify(none));
  check("no build named = the newest", run3.ok && JSON.stringify(JSON.parse(run3.data).rows[0].dps) ===
        JSON.stringify(dpsNew), run3.error);
  console.log(fails ? fails + " FAILED" : "all passed");
  process.exit(fails ? 1 : 0);
})();
