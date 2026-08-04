# stlite build (browser-native, zero server cost)

The canonical build lives at **`../index.html`** (the repo/Pages root), not
in this folder — it needs to be at the root so `tftsimulator.app` can serve
it directly at `/`. This folder is now just docs plus a redirect stub
(`index.html` here forwards to `../`) so the earlier local-test URL
(`http://localhost:8000/stlite_app/`) keeps working.

`../index.html` runs the same app as the droplet — `app.py` and everything
it imports — entirely in the visitor's browser via
[stlite](https://github.com/whitphx/stlite) (Streamlit on
Pyodide/WebAssembly). No server, no droplet bill.

Nothing there is a copy: it fetches `app.py`, `champion.py`,
`pages/ChampionSelector.py`, etc. from this same repo at load time (see the
`SOURCE_FILES` list in `../index.html`). Edit the real source and the stlite
build picks it up automatically — there is no second copy to keep in sync.

## Status

Verified working: both pages, several code paths (basic champ, Ezreal's
takedowns branch which is the one with sim_core.py-specific logic, the
data_editor "To Plot" checkbox column). Auto-deploys to GitHub Pages on push
to `main`. **The droplet at `tftsimulator.app` remains the live, primary
URL** until DNS is deliberately repointed — see "Cutting over the domain"
below for the actual steps when you're ready.

## What's deliberately excluded

- `sim_api.py`, `fastapi`, `uvicorn`, `pydantic` — the API-offload server.
  Nothing here calls it; `SIM_API_URL` is simply unset in the browser, so
  every simulation runs locally, in-page.
- `xlsxwriter`, `requests` — not installed. Both are already guarded in the
  app code (`xlsxwriter` is a local import inside the two functions that use
  it, `requests` fails over to `None` when absent), so their absence doesn't
  break anything; it just means the two Excel-export helpers and the
  API-offload path are unreachable here, which is correct for a
  server-less build.

## Test locally

Browsers block ES module `<script>` tags and cross-origin `fetch()` on
`file://` URLs, so opening `index.html` by double-clicking it will not work
— you need a static file server, started from **`set18/`** (the repo root,
so relative fetches resolve):

```bash
cd set18
python -m http.server 8000
```

Then open **http://localhost:8000/** (or the old `.../stlite_app/` URL,
which just redirects there now).

First load pulls the Pyodide runtime plus numpy/pandas/plotly. Measured cold:
~180s and at least 11MB transferred (that's a floor, not a ceiling — stlite
runs Python inside a Web Worker, and that number only counts what the main
page's network tab sees, not the worker's own fetches). Everything is served
with long-lived `immutable` cache headers, so repeat visits should be much
faster; this wasn't re-measured end-to-end with a genuinely warm profile, so
treat "much faster" as directionally true rather than a hard number.

## Known-benign console noise

Chrome intermittently logs one `Failed to load resource: 404` during boot.
It reproduces inconsistently, doesn't correlate with anything actually
breaking, and its exact URL couldn't be pinned down across three separate
capture attempts (page-level and browser-context-level network listeners).
Likely a micropip/Pyodide package probe that doesn't 404 every run, happening
inside the Web Worker where stlite actually runs Python — the same place
Playwright's page/context-level network APIs can't see or control requests
(this also blocked slow-motion-testing the boot-overlay fix below). Not
investigated further since it has no observed effect.

## The boot-overlay timing bug (found and fixed)

The loading screen used to hide as soon as `#root` got its first child —
which happens as soon as Streamlit's own app shell mounts, *before* Pyodide
finishes installing numpy/pandas/plotly. That revealed stlite's own
"Mounting files." / "Unpacking archives." / "Mocking some packages." /
"Installing packages." toasts mid-install, unstyled relative to the rest of
the page. Caught this via a real screenshot, not by inspection.

Fixed by waiting for both "`#root` has content" and "none of those toast
phrases are still visible" (`document.body.innerText`, not `textContent` —
`textContent` would match the fix's own source comments describing the
phrases, since script tag contents count as `textContent` but not
`innerText`; caught that regression before it shipped). A five-minute
ceiling means a future stlite wording change degrades this to "hides a bit
early" again, not "hides never."

**Verification is partial, on purpose disclosed rather than hidden:**
confirmed the new logic runs without erroring and resolves correctly under
normal conditions; confirmed the self-match bug is actually gone. Could
*not* get an automated slow-motion repro of "toasts visible, overlay
correctly stays, then reveals" in one continuous run — every attempt to
artificially slow the install (CDP bandwidth throttling, per-request delay
via `page.route()`) failed to affect it, because that traffic happens inside
the Web Worker, outside what Playwright's page-level tools can reach. The
fix is grounded in the real observed strings and correct DOM semantics, not
guessed, but hasn't been watched happening end-to-end by anything other
than a human loading the page on a slow connection.

## What was checked before calling this production-ready

- `st.data_editor` + `st.column_config.CheckboxColumn` — confirmed rendering
  and confirmed *interactive* (clicked the actual checkbox cell via canvas
  coordinates, watched the plot appear) on both ChampionSelector and
  ManaGeneration. `class_utilities.plot_df()` tries this for real everywhere
  now, including under stlite; `checkbox_select_fallback` only fires if it
  actually throws — it shouldn't in normal use anymore.
- No missing imports: every local module `app.py`/the pages/`class_utilities.py`
  import resolves to something already in `SOURCE_FILES`; `core/` is empty
  and unreferenced; `download_map.py`/`download_reference_data.py` are
  one-off utility scripts, not imported by the live app, correctly excluded.
- Moving the canonical page from `stlite_app/index.html` to `../index.html`
  (repo root) re-verified end to end: app boots, zero bad HTTP responses,
  old `/stlite_app/` URL redirects correctly.

## Deploy to GitHub Pages

`.github/workflows/stlite-pages.yml` publishes this whole repo as a static
site so the relative fetches above keep working in production too. It runs
on push to `main` (and is still manually runnable via `workflow_dispatch`).

One-time setup: repo Settings → Pages → Source → **GitHub Actions**.

Before a custom domain is configured, the app lands at
`https://<user>.github.io/<repo>/`.

This is a separate deployment target from the droplet (`deploy.yaml`) and
Ploomber Cloud (`ploomber-cloud.yaml`) — running it doesn't touch either.

## Cutting over the domain

Steps for pointing `tftsimulator.app` at this instead of the droplet, per
[GitHub's own docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
(verified there directly, not from memory — DNS for a live domain isn't
somewhere to guess):

1. **In the DigitalOcean DNS panel** (Networking → Domains → tftsimulator.app),
   replace the existing `A` record (currently `165.232.53.150`, the droplet)
   with four `A` records, all at hostname `tftsimulator.app`, one IP each:
   `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`.
2. The existing `www` CNAME (currently aliasing `tftsimulator.app` itself)
   can stay as-is — once the apex resolves to GitHub Pages, it resolves
   through. GitHub's own recommendation is to instead point it directly at
   `carsonhu.github.io`, which is marginally more robust; either works.
3. **In the GitHub repo** → Settings → Pages → Custom domain → enter
   `tftsimulator.app` → Save. GitHub validates DNS at this point; it's fine
   to save before DNS has propagated, it'll just show a pending/unverified
   state until it catches up.
4. Once GitHub shows the domain verified (can take a few minutes up to the
   DNS TTL, which is 3600s/1hr on the current `A` record), check **Enforce
   HTTPS** in the same settings panel. Certificate provisioning can take up
   to 24 hours per GitHub's docs, so this checkbox may not be available
   immediately after verification — that's expected, not a failure.
5. The droplet keeps running (and costing money) until you separately decide
   to resize or destroy it — this cutover only changes where DNS points,
   nothing about the droplet itself.

Not done as part of getting this build production-ready, on purpose: this is
external, live-traffic-affecting infrastructure, so it's a deliberate step
for you to trigger, not something to automate.
