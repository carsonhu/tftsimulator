// worker.js
//
// The only place Python runs in the v2 frontend. Boots Pyodide (no packages
// -- the sim is pure stdlib, which is the entire speed story vs stlite),
// mounts the repo's .py files into the virtual FS, and serves three RPCs
// over postMessage: catalog / champInfo / run. Payloads cross the boundary
// as JSON strings so no PyProxy ever leaks to the page.

// Pinned to the same Pyodide the stlite build has been running this exact
// source under (stlite 0.85.1 bundles 0.27.6), so the interpreter is a
// known quantity. Bump deliberately, not incidentally.
const PYODIDE_BASE = "https://cdn.jsdelivr.net/pyodide/v0.27.6/full/";
importScripts(PYODIDE_BASE + "pyodide.js");

// Destination inside the Pyodide FS -> the file's path on the site, which is
// also its path in the repo: this page is served from the repo root, so it
// fetches the very same .py files the tests exercise. Nothing is duplicated,
// so the simulator on the page cannot drift from the one under test.
const PY_FILES = [
  "build_champion.py",
  "buildstore.py",
  "champion.py",
  "effects.py",
  "events.py",
  "layout.py",
  "helpers/__init__.py",
  "helpers/display_name.py",
  "item.py",
  "items/__init__.py",
  "items/artifacts.py",
  "items/base.py",
  "items/craftables.py",
  "items/debuffs.py",
  "items/radiants.py",
  "registry.py",
  "set19buffs.py",
  "set19champs.py",
  "set19items.py",
  "sim_core.py",
  "sim_entry.py",
  "simulator.py",
  "stats.py",
  "timing.py",
  "traits/__init__.py",
  "traits/arcanist.py",
  "traits/base.py",
  "traits/encore.py",
  "traits/heartsteel.py",
  "traits/hitmaker.py",
  "traits/hyperpop.py",
  "traits/illbeats.py",
  "traits/ionic_spark.py",
  "traits/kda.py",
  "traits/swiftstriker.py",
  "traits/trickshot.py",
  "traits/true_damage.py",
  "traits/prodigy.py",
  "traits/pentakill.py",
  "traits/composer.py",
];

async function boot() {
  const t0 = performance.now();
  // Runtime download and source fetches overlap; the sources are ~300 KB
  // total so the runtime dominates.
  const [pyodide, sources] = await Promise.all([
    loadPyodide({ indexURL: PYODIDE_BASE }),
    Promise.all(
      // "no-cache" means revalidate, not bypass: the browser still keeps the
      // file and still gets a 304 when it hasn't moved, so this costs one
      // conditional request per source against a boot the Pyodide runtime
      // download already dominates.
      //
      // Without it these are the one thing on the page that can go stale
      // invisibly. Nothing here is content-hashed, so a plain fetch() is
      // served straight from cache with no request at all -- a local edit
      // never appears no matter how many times the server restarts, and in
      // production a returning visitor inside the 10-minute max-age can pair
      // a fresh worker.js with a stale set19champs.py, which is worse than
      // stale: it is two halves of different builds.
      PY_FILES.map(async (path) => {
        const resp = await fetch(path, { cache: "no-cache" });
        if (!resp.ok) throw new Error("fetch " + path + ": HTTP " + resp.status);
        return [path, await resp.text()];
      })
    ),
  ]);

  for (const [path, text] of sources) {
    // /app itself, and the package folder of a module like items/base.py.
    pyodide.FS.mkdirTree("/app/" + path.slice(0, path.lastIndexOf("/") + 1));
    pyodide.FS.writeFile("/app/" + path, text);
  }
  // Client builds (ledger B9): buildstore.py reads builds/index.json and
  // builds/<file> next to itself, so they go to /app/builds. The index and the
  // newest build (the default) load now; any other build the first time a
  // request names it (ensureBuild). A build file never changes once written
  // (snapshots are immutable), so each is fetched at most once per page.
  pyodide.FS.mkdirTree("/app/builds");
  buildIndex = await fetchText("builds/index.json");
  pyodide.FS.writeFile("/app/builds/index.json", buildIndex);
  buildFiles = new Map(
    JSON.parse(buildIndex).builds.map((b) => [b.version, b.file])
  );
  const newest = JSON.parse(buildIndex).builds[0];
  if (newest) await loadBuild(pyodide, newest.version);

  pyodide.runPython('import sys; sys.path.insert(0, "/app")');
  const entry = pyodide.pyimport("sim_entry");
  postMessage({ type: "ready", bootMs: Math.round(performance.now() - t0) });
  return { pyodide, entry };
}

let buildIndex = null;
let buildFiles = new Map(); // version -> file name in builds/
const loadedBuilds = new Set();

async function fetchText(path) {
  const resp = await fetch(path, { cache: "no-cache" });
  if (!resp.ok) throw new Error("fetch " + path + ": HTTP " + resp.status);
  return resp.text();
}

async function loadBuild(pyodide, version) {
  if (loadedBuilds.has(version)) return;
  const file = buildFiles.get(version);
  if (!file) throw new Error("build " + version + " is not in builds/index.json");
  pyodide.FS.writeFile("/app/builds/" + file, await fetchText("builds/" + file));
  loadedBuilds.add(version);
}

// A champInfo/run config may name a build (cfg.build); load it before Python
// asks for it. No build named = the newest, already loaded at boot.
async function ensureBuild(pyodide, configJson) {
  const version = JSON.parse(configJson).build;
  if (version) await loadBuild(pyodide, version);
}

const entryPromise = boot();
entryPromise.catch((err) => {
  postMessage({
    type: "boot-error",
    error: String((err && err.stack) || err),
  });
});

onmessage = async (event) => {
  const { id, cmd, arg } = event.data;
  try {
    const { pyodide, entry } = await entryPromise;
    let result;
    if (cmd === "catalog") {
      result = entry.catalog_json();
    } else if (cmd === "champInfo") {
      await ensureBuild(pyodide, arg);
      result = entry.champ_info_json(arg);
    } else if (cmd === "run") {
      await ensureBuild(pyodide, arg);
      result = entry.run_json(arg);
    } else {
      throw new Error("unknown cmd: " + cmd);
    }
    postMessage({ id, ok: true, data: result });
  } catch (err) {
    postMessage({ id, ok: false, error: String((err && err.stack) || err) });
  }
};
