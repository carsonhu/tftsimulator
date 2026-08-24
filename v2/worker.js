// v2/worker.js
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

// Destination inside the Pyodide FS -> sibling file relative to the site
// root (this worker lives in v2/, the sources one level up). Same idea as
// the stlite index.html manifest: the deployed site serves the same .py
// files the droplet runs, so nothing is duplicated.
const PY_FILES = [
  "champion.py",
  "helpers/__init__.py",
  "helpers/display_name.py",
  "item.py",
  "role.py",
  "set18buffs.py",
  "set18champs.py",
  "set18items.py",
  "set18roles.py",
  "sim_core.py",
  "sim_entry.py",
  "simulator.py",
  "stats.py",
  "status.py",
  "utils.py",
];

async function boot() {
  const t0 = performance.now();
  // Runtime download and source fetches overlap; the sources are ~300 KB
  // total so the runtime dominates.
  const [pyodide, sources] = await Promise.all([
    loadPyodide({ indexURL: PYODIDE_BASE }),
    Promise.all(
      PY_FILES.map(async (path) => {
        const resp = await fetch("../" + path);
        if (!resp.ok) throw new Error("fetch " + path + ": HTTP " + resp.status);
        return [path, await resp.text()];
      })
    ),
  ]);

  pyodide.FS.mkdirTree("/app/helpers");
  for (const [path, text] of sources) {
    pyodide.FS.writeFile("/app/" + path, text);
  }
  pyodide.runPython('import sys; sys.path.insert(0, "/app")');
  const entry = pyodide.pyimport("sim_entry");
  postMessage({ type: "ready", bootMs: Math.round(performance.now() - t0) });
  return entry;
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
    const entry = await entryPromise;
    let result;
    if (cmd === "catalog") {
      result = entry.catalog_json();
    } else if (cmd === "champInfo") {
      result = entry.champ_info_json(arg);
    } else if (cmd === "run") {
      result = entry.run_json(arg);
    } else {
      throw new Error("unknown cmd: " + cmd);
    }
    postMessage({ id, ok: true, data: result });
  } catch (err) {
    postMessage({ id, ok: false, error: String((err && err.stack) || err) });
  }
};
