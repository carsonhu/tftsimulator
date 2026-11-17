# TFT Set 19 damage simulator

Work in progress. Pick a champion, items, traits and augments, simulate a fight against training dummies, and
compare the damage one more item or buff adds. Every number comes from a TFT client build the user selects, and
every rule about game behaviour is recorded with its evidence in `docs/ASSUMPTIONS.md`.

- `index.html` + `app.js`: the static site; the simulator runs in the browser under Pyodide (`worker.js`).
- `champions/<Name>.md`: one worksheet per champion in scope (`roster.json`).
- `builds/`: the client builds the simulator can use.

Local run: `python serve.py`, then open http://127.0.0.1:8618/. See `CLAUDE.md` for how the project works.
