// app.js
//
// UI logic for the static frontend. All simulation happens in worker.js
// (Pyodide); this file only builds controls from the catalog, assembles the
// config object sim_entry.py documents, and renders what comes back. Where
// behavior mirrors the Streamlit page (slice options, table columns, chart
// construction), it mirrors pages/ChampionSelector.py and
// class_utilities.plot_df on purpose -- v2 is a re-skin, not a redesign.

"use strict";

// ---------------------------------------------------------------------------
// Worker RPC
// ---------------------------------------------------------------------------

const worker = new Worker("worker.js");
const pending = new Map();
let nextRpcId = 1;
let bootMs = null;

function rpc(cmd, arg) {
  return new Promise((resolve, reject) => {
    const id = nextRpcId++;
    pending.set(id, { resolve, reject });
    worker.postMessage({ id, cmd, arg });
  });
}

worker.onmessage = (event) => {
  const msg = event.data;
  if (msg.type === "ready") {
    bootMs = msg.bootMs;
    init().catch((err) => showBootError(String((err && err.stack) || err)));
    return;
  }
  if (msg.type === "boot-error") {
    showBootError(msg.error);
    return;
  }
  const entry = pending.get(msg.id);
  if (!entry) return;
  pending.delete(msg.id);
  if (msg.ok) entry.resolve(JSON.parse(msg.data));
  else entry.reject(new Error(msg.error));
};

worker.onerror = (event) => {
  showBootError(event.message || "worker error");
};

function showBootError(text) {
  const boot = document.getElementById("boot-status");
  boot.hidden = false;
  boot.innerHTML =
    "<div>Failed to start the simulator.</div>" +
    '<div class="detail">Check the browser console for the full trace.</div>' +
    '<pre class="error"></pre>';
  boot.querySelector("pre").textContent = text;
}

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

const DPS_TIMES = [5, 10, 15, 20, 25];

// Bonus stats, keyed as sim_entry expects them. Ranges are the ones the
// Streamlit sidebar used. Each is rendered beside the stat it feeds in the
// Base stats panel.
const BONUS_FIELDS = {
  ad: { label: "Bonus AD", min: 0, max: 2000 },
  ap: { label: "Bonus AP", min: 0, max: 2000 },
  as: { label: "Bonus AS", min: 0, max: 200 },
  dmgamp: { label: "DmgAmp", min: 0, max: 1000 },
  crit: { label: "Bonus Crit", min: 0, max: 200 },
  critdmg: { label: "CritDmg", min: 0, max: 200 },
  manaregen: { label: "ManaRegen", min: 0, max: 10 },
  mpa: { label: "ManaPerAuto", min: 0, max: 15 },
};

const state = {
  catalog: null,
  buffMeta: null, // cls -> {name, levels, extra}
  cfg: {
    champ: null,
    level: 1,
    num_targets: null,
    num_extra_targets: null,
    takedowns: 0,
    num_traits: 6,
    bonus: { ad: 0, ap: 0, as: 0, dmgamp: 0, crit: 0, critdmg: 0, manaregen: 0, mpa: 0 },
    stage: "4-1",
    tactician_level: 4,
    blackthorn: null,
    items: ["NoItem", "NoItem", "NoItem"],
    buffs: [], // [cls, level, params]
    enemy: { hp: 1800, armor: 100, mr: 100 },
    frame_rate: 30,
    t: 30,
  },
  // Team traits the champion is NOT a member of: cls -> level. Kept out of
  // cfg.buffs so the buff bar stays the buff bar; merged in by cfgForSlice
  // with params 0, which is what the "Is X" flag means. Being real entries
  // in cfg.buffs from there on means the Trait slice sweeps their other
  // breakpoints too, same as any hand-picked buff.
  teamBuffs: new Map(),
  slice: "Craftable",
  displayDps: false,
  colorScale: true,
  // Class name -> icon URL, from the per-group index.json files. A row draws
  // art only if its class is in here, so the wisp rows -- which have none --
  // cost no failed requests.
  icons: new Map(),
  // icons/traits/tiers.json: {tiers: {cls: {level: tier}}, colours: {...}}.
  traitTiers: null,
  // Which header the table is sorted by. key null = the order sim_entry
  // delivered, which is already ratio-at-25s descending.
  sort: { key: null, dir: "desc" },
  // Payload for the slice on screen, and per-slice plot selections. Any
  // config change (not a slice change) clears selections, like a Streamlit
  // rerun resetting the checkbox column.
  current: null,
  selections: new Map(), // slice -> Set(idx)
  cache: new Map(), // config-json -> payload
  gen: 0,
};

const $ = (id) => document.getElementById(id);

function cfgForSlice(sliceName) {
  const cfg = Object.assign(JSON.parse(JSON.stringify(state.cfg)), {
    slice: sliceName,
  });
  for (const [cls, level] of state.teamBuffs) {
    if (level <= 0) continue;
    // renderTeamTraits drops any trait that is in the buff bar, so this can
    // only collide in the instant between the two updates. The buff bar's
    // entry wins; a second entry for one class would also give the Trait
    // slice two rows per breakpoint.
    if (cfg.buffs.some(([c]) => c === cls)) continue;
    cfg.buffs.push([cls, level, 0]);
  }
  return cfg;
}

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------

async function init() {
  // Loaded alongside the catalog rather than before it: a missing or stale
  // index just means no icons, never a page that fails to start.
  loadIcons();
  state.catalog = await rpc("catalog");
  state.buffMeta = new Map(state.catalog.buffs.map((b) => [b.cls, b]));

  buildStaticControls();
  await selectChampion(state.catalog.champions[0].name, { keepLevel: false });

  $("boot-status").hidden = true;
  $("layout").hidden = false;
}

// icons.py writes one directory per group. Class names are unique across the
// modules they come from, so a flat class -> URL map is enough.
const ICON_GROUPS = ["items", "augments", "traits"];

async function loadIcons() {
  await Promise.all(
    ICON_GROUPS.map(async (group) => {
      try {
        const response = await fetch(`icons/${group}/index.json`);
        if (!response.ok) return;
        for (const cls of await response.json())
          state.icons.set(cls, `icons/${group}/${cls}.png`);
      } catch (err) {
        // No icons for this group; the names still say everything the table
        // needs them to.
      }
    })
  );
  try {
    // Traits alone need a second file: their glyphs are white silhouettes, and
    // the tier a breakpoint sits at is what gives one its colour. icons.py has
    // already resolved level -> tier, so nothing here knows what a breakpoint
    // is -- it looks up the level it is drawing.
    const response = await fetch("icons/traits/tiers.json");
    if (response.ok) state.traitTiers = await response.json();
  } catch (err) {
    // Without it the glyphs still draw, just in the neutral colour.
  }
  // This resolves after the first render (it is deliberately not awaited at
  // boot), so anything that draws an icon has to be told to draw again.
  if (state.catalog) renderTeamTraits();
  if (state.current) renderResults();
}

// A trait's glyph in a hexagon coloured by the tier that breakpoint sits at,
// which is how the game itself distinguishes them. Falls back to the plain
// glyph when the level has no tier (or tiers.json never loaded), so this is
// never the reason a trait goes unlabelled.
function traitBadge(cls, level) {
  const src = state.icons.get(cls);
  if (!src) return null;
  const badge = document.createElement("span");
  badge.className = "trait-badge";
  const tier = state.traitTiers?.tiers?.[cls]?.[String(level)];
  const colour = tier && state.traitTiers.colours[tier];
  if (colour) {
    badge.style.background = colour;
    badge.dataset.tier = tier;
  }
  const glyph = document.createElement("span");
  glyph.className = "trait-glyph";
  // Masked rather than an <img>: the glyph is white-on-nothing, and a mask
  // lets one file sit on any tier colour without shipping a copy per tier.
  glyph.style.webkitMaskImage = `url("${src}")`;
  glyph.style.maskImage = `url("${src}")`;
  badge.appendChild(glyph);
  return badge;
}

function buildStaticControls() {
  const cat = state.catalog;

  const champSel = $("champ");
  for (const c of cat.champions) champSel.add(new Option(c.name, c.name));
  champSel.onchange = () => selectChampion(champSel.value, { keepLevel: false });

  $("level").onchange = () => {
    state.cfg.level = Number($("level").value);
    // Level changes re-read the champ's own defaults, like re-running
    // champ_selector does.
    selectChampion(state.cfg.champ, { keepLevel: true });
  };

  const stageSel = $("stage");
  for (const s of cat.defaults.stages) stageSel.add(new Option(s, s));
  stageSel.value = cat.defaults.stageDefault;
  stageSel.onchange = () => {
    state.cfg.stage = stageSel.value;
    onConfigChanged();
  };

  bindSlider("tactician", "tacticianValue", (v) => {
    state.cfg.tactician_level = v;
    onConfigChanged();
  });

  $("takedowns").onchange = () => {
    state.cfg.takedowns = clampInput($("takedowns"));
    onConfigChanged();
  };
  $("numTraits").onchange = () => {
    state.cfg.num_traits = clampInput($("numTraits"));
    onConfigChanged();
  };

  // Item selectors.
  const itemRows = $("itemRows");
  for (let n = 0; n < cat.defaults.numItems; n++) {
    const label = document.createElement("label");
    label.textContent = "Item " + (n + 1);
    const sel = document.createElement("select");
    for (const item of cat.sidebarItems) sel.add(new Option(item.name, item.cls));
    sel.value = "NoItem";
    sel.onchange = () => {
      state.cfg.items[n] = sel.value;
      onConfigChanged();
    };
    label.appendChild(sel);
    itemRows.appendChild(label);
  }
  $("resetItems").onclick = () => {
    state.cfg.items = state.cfg.items.map(() => "NoItem");
    for (const sel of itemRows.querySelectorAll("select")) sel.value = "NoItem";
    onConfigChanged();
  };

  bindSlider("numBuffs", "numBuffsValue", (v) => {
    resizeBuffRows(v);
    onConfigChanged();
  });

  // Blackthorn panel.
  if (cat.blackthorn) {
    const roleSel = $("btRole");
    for (const r of cat.blackthorn.roles) roleSel.add(new Option(r, r));
    const costSel = $("btCost");
    for (const c of cat.blackthorn.costs) costSel.add(new Option(c.label, c.value));
    roleSel.onchange = () => {
      syncBlackthornCfg();
      onConfigChanged();
    };
    costSel.onchange = () => {
      // Which star levels exist depends on the cost, same as the page.
      refreshBlackthornStars();
      syncBlackthornCfg();
      onConfigChanged();
    };
    $("btStar").onchange = () => {
      syncBlackthornCfg();
      onConfigChanged();
    };
  }

  for (const [id, key] of [
    ["enemyHp", "hp"],
    ["enemyArmor", "armor"],
    ["enemyMr", "mr"],
  ]) {
    const input = $(id);
    input.value = state.cfg.enemy[key];
    sizeInlineNumber(input);
    // Width tracks the digits as they are typed so the title reads as a
    // sentence rather than as three boxes with slack in them.
    input.oninput = () => sizeInlineNumber(input);
    input.onchange = () => {
      state.cfg.enemy[key] = clampInput(input);
      sizeInlineNumber(input);
      onConfigChanged();
    };
    selectZeroOnFocus(input);
  }

  // No frame-rate control: cfg.frame_rate stays at the 30 the sim expects.
  $("displayDps").onchange = () => {
    state.displayDps = $("displayDps").checked;
    renderResults();
  };

  const colorScale = $("colorScale");
  colorScale.checked = state.colorScale;
  colorScale.onchange = () => {
    state.colorScale = colorScale.checked;
    $("scaleLegend").hidden = !state.colorScale;
    renderResults();
  };
}

function selectZeroOnFocus(input) {
  // A 0 is a placeholder rather than a value: select it so the next
  // keystroke replaces it, instead of the caret landing beside it and
  // turning a typed 5 into 50. Anything non-zero is a real number the user
  // is more likely adjusting than retyping (an enemy's 100 armor, a bonus
  // already set to 50), so its caret is left where it was clicked.
  let selected = false;
  input.addEventListener("focus", () => {
    selected = Number(input.value) === 0;
    if (selected) input.select();
  });
  // Chromium collapses the selection on the mouseup following the click
  // that moved focus, which would undo the select() above.
  input.addEventListener("mouseup", (event) => {
    if (selected) {
      event.preventDefault();
      selected = false;
    }
  });
}

function sizeInlineNumber(input) {
  input.style.width = Math.max(2, String(input.value).length) + 1 + "ch";
}

function clampInput(input) {
  let v = Number(input.value) || 0;
  if (input.min !== "") v = Math.max(v, Number(input.min));
  if (input.max !== "") v = Math.min(v, Number(input.max));
  input.value = v;
  return v;
}

function bindSlider(id, valueId, onChange) {
  const slider = $(id);
  const label = $(valueId);
  slider.oninput = () => (label.textContent = slider.value);
  slider.onchange = () => {
    label.textContent = slider.value;
    onChange(Number(slider.value));
  };
}

function buildPills(container, values, selected, onPick) {
  container.innerHTML = "";
  for (const v of values) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = v;
    btn.className = String(v) === String(selected) ? "pill active" : "pill";
    btn.onclick = () => {
      for (const b of container.children) b.classList.remove("active");
      btn.classList.add("active");
      onPick(v);
    };
    container.appendChild(btn);
  }
}

// ---------------------------------------------------------------------------
// Champion selection & buff bar
// ---------------------------------------------------------------------------

async function selectChampion(name, { keepLevel }) {
  const cat = state.catalog;
  const meta = cat.champions.find((c) => c.name === name);
  state.cfg.champ = name;

  const levelSel = $("level");
  levelSel.innerHTML = "";
  for (const l of meta.levels) levelSel.add(new Option(l, l));
  if (keepLevel && meta.levels.includes(state.cfg.level)) {
    levelSel.value = state.cfg.level;
  } else {
    state.cfg.level = meta.levels[0];
    levelSel.value = state.cfg.level;
  }

  state.cfg.num_targets = null;
  state.cfg.num_extra_targets = null;

  // Minimal config: the defaults (traits, target counts) must describe the
  // champion itself, not whatever items/buffs are still configured.
  const probe = cfgForSlice(state.slice);
  probe.items = ["NoItem", "NoItem", "NoItem"];
  probe.buffs = [];
  const info = await rpc("champInfo", JSON.stringify(probe));

  setupTargetSlider("numTargets", info.numTargets, (v) => {
    state.cfg.num_targets = v;
    onConfigChanged();
  });
  setupTargetSlider("numExtraTargets", info.numExtraTargets, (v) => {
    state.cfg.num_extra_targets = v;
    onConfigChanged();
  });

  // Buff bar: default traits at their first listed level, min two rows.
  const defaults = info.defaultTraits.classNames.filter((c) => state.buffMeta.has(c));
  const rows = Math.max(state.catalog.defaults.numBuffs.default, defaults.length);
  state.cfg.buffs = [];
  for (let i = 0; i < rows; i++) {
    const cls = i < defaults.length ? defaults[i] : "NoBuff";
    state.cfg.buffs.push(defaultBuffTuple(cls));
  }
  $("numBuffs").value = rows;
  $("numBuffsValue").textContent = rows;
  renderBuffRows();

  onConfigChanged();
}

function defaultBuffTuple(cls) {
  const meta = state.buffMeta.get(cls);
  const params = meta.extra ? meta.extra.Default : 0;
  return [cls, meta.levels[0], params];
}

function setupTargetSlider(id, defaultValue, onChange) {
  const row = $(id + "Row");
  const slider = $(id);
  const label = $(id + "Value");
  if (!defaultValue || defaultValue <= 0) {
    row.hidden = true;
    return;
  }
  row.hidden = false;
  slider.min = 1;
  slider.max = Math.max(3, defaultValue + 1);
  slider.value = defaultValue;
  label.textContent = defaultValue;
  slider.oninput = () => (label.textContent = slider.value);
  slider.onchange = () => {
    label.textContent = slider.value;
    onChange(Number(slider.value));
  };
}

function resizeBuffRows(count) {
  const buffs = state.cfg.buffs;
  while (buffs.length < count) buffs.push(defaultBuffTuple("NoBuff"));
  buffs.length = count;
  renderBuffRows();
}

function renderBuffRows() {
  const container = $("buffRows");
  container.innerHTML = "";
  state.cfg.buffs.forEach((tuple, i) => {
    const row = document.createElement("div");
    row.className = "buff-row";

    const buffSel = document.createElement("select");
    for (const b of state.catalog.buffs) buffSel.add(new Option(b.name, b.cls));
    buffSel.value = tuple[0];
    buffSel.title = "Buff " + (i + 1);

    const levelSel = document.createElement("select");
    const paramInput = document.createElement("input");
    paramInput.type = "number";
    // A parameter whose values are names, not a count (Greenfather's Hex).
    // The stored value is still the index, so nothing downstream changes --
    // only what the row shows for it.
    const paramSelect = document.createElement("select");

    // Column headers per row, like buff_bar's widget labels: the third one
    // is the buff's own parameter title (Stacks, Casts, ...) and follows the
    // selected buff.
    const column = (text, ...controls) => {
      const label = document.createElement("label");
      const caption = document.createElement("span");
      caption.className = "col-label";
      caption.textContent = text;
      label.appendChild(caption);
      for (const control of controls) label.appendChild(control);
      return label;
    };
    const nameCol = column("Name", buffSel);
    const levelCol = column("Level", levelSel);
    const paramCol = column("Param", paramInput, paramSelect);
    const paramCaption = paramCol.querySelector(".col-label");

    const paramValue = (meta) => {
      if (!meta.extra) return 0;
      return Number(meta.extra.Options ? paramSelect.value : paramInput.value);
    };

    const syncParamColumn = (meta) => {
      // Hidden rather than removed: rows keep their columns aligned when
      // some buffs in the bar take a parameter and others don't.
      paramCol.style.visibility = meta.extra ? "visible" : "hidden";
      paramCaption.textContent = meta.extra ? meta.extra.Title : "Param";
      const named = Boolean(meta.extra && meta.extra.Options);
      paramInput.hidden = named;
      paramSelect.hidden = !named;
      if (!named) return;
      const previous = paramSelect.value;
      paramSelect.innerHTML = "";
      meta.extra.Options.forEach((name, index) => {
        paramSelect.add(new Option(name, String(index)));
      });
      if ([...paramSelect.options].some((o) => o.value === previous)) {
        paramSelect.value = previous;
      }
    };

    const syncRow = (resetToDefaults) => {
      const meta = state.buffMeta.get(buffSel.value);
      // Rebuilding the options resets the browser's selection, so hold on to
      // it -- otherwise changing the *level* snaps back to the first entry
      // before the config reads it.
      const previousLevel = levelSel.value;
      levelSel.innerHTML = "";
      for (const l of meta.levels) levelSel.add(new Option(l, l));
      if (resetToDefaults) {
        levelSel.value = meta.levels[0];
        paramInput.value = meta.extra ? meta.extra.Default : 0;
        paramSelect.value = String(meta.extra ? meta.extra.Default : 0);
      } else if ([...levelSel.options].some((o) => o.value === previousLevel)) {
        levelSel.value = previousLevel;
      }
      if (meta.extra) {
        paramInput.min = meta.extra.Min;
        paramInput.max = meta.extra.Max;
        paramInput.title = meta.extra.Title;
        paramSelect.title = meta.extra.Title;
      }
      // Before reading the value: for a named parameter this is what fills
      // the options, and reading an empty select gives "".
      syncParamColumn(meta);
      if (resetToDefaults && meta.extra && meta.extra.Options) {
        paramSelect.value = String(meta.extra.Default);
      }
      state.cfg.buffs[i] = [
        buffSel.value,
        Number(levelSel.value),
        paramValue(meta),
      ];
      // After the write, not before: the layout is decided by reading every
      // row out of state.cfg.buffs, so running it first sees this row's
      // previous buff and lands one change behind.
      updateBuffParamLayout();
    };

    buffSel.onchange = () => {
      syncRow(true);
      onConfigChanged();
    };
    levelSel.onchange = () => {
      syncRow(false);
      onConfigChanged();
    };
    paramInput.onchange = () => {
      clampInput(paramInput);
      syncRow(false);
      onConfigChanged();
    };
    paramSelect.onchange = () => {
      syncRow(false);
      onConfigChanged();
    };

    // Initial fill from the stored tuple.
    const meta = state.buffMeta.get(tuple[0]);
    for (const l of meta.levels) levelSel.add(new Option(l, l));
    levelSel.value = tuple[1];
    paramInput.value = tuple[2];
    if (meta.extra) {
      paramInput.min = meta.extra.Min;
      paramInput.max = meta.extra.Max;
      paramInput.title = meta.extra.Title;
      paramSelect.title = meta.extra.Title;
    }
    syncParamColumn(meta);
    paramSelect.value = String(tuple[2]);

    row.appendChild(nameCol);
    row.appendChild(levelCol);
    row.appendChild(paramCol);
    container.appendChild(row);
  });
  updateBuffParamLayout();
  updateBlackthornPanel();
}

function updateBuffParamLayout() {
  // When nothing in the bar takes a parameter there is no third column to
  // align against, so Name and Level take the whole width instead of
  // leaving a permanent empty gutter.
  const anyParam = state.cfg.buffs.some(
    ([cls]) => state.buffMeta.get(cls) && state.buffMeta.get(cls).extra
  );
  $("buffRows").classList.toggle("no-param", !anyParam);
}

// ---------------------------------------------------------------------------
// Team traits ("my team runs this, but this champion isn't one of them")
// ---------------------------------------------------------------------------

function renderTeamTraits() {
  const container = $("teamTraits");
  const traits = state.catalog.teamBuffs || [];
  if (!traits.length) {
    $("teamTraitsPanel").hidden = true;
    return;
  }
  container.innerHTML = "";
  let shown = 0;

  for (const trait of traits) {
    // A trait picked in Global Buffs is configured there, with its own level
    // and Is-X flag, so it is not offered here at all -- two controls for
    // one trait invites setting it twice.
    if (state.cfg.buffs.some(([cls]) => cls === trait.cls)) {
      state.teamBuffs.delete(trait.cls);
      continue;
    }
    shown++;

    const current = state.teamBuffs.get(trait.cls) ?? 0;
    const label = document.createElement("label");
    label.className = trait.scales ? "team-trait" : "team-trait flat";
    label.title =
      "Team-wide " + trait.name + " only (" + trait.paramTitle + " = 0)";

    const caption = document.createElement("span");
    caption.className = "col-label";
    caption.textContent = trait.name;

    // Coloured by the level actually selected, so the badge tracks the picker
    // beside it; an unselected trait shows its first breakpoint's tier rather
    // than going colourless, which would read as "no icon" instead of "off".
    const badge = traitBadge(trait.cls, current || trait.onLevel);

    if (trait.scales) {
      // The aura itself steps per breakpoint (Lunar), so the level is a real
      // question and gets a picker.
      const sel = document.createElement("select");
      for (const level of trait.levels) {
        sel.add(new Option(level === 0 ? "—" : String(level), String(level)));
      }
      sel.value = String(current);
      sel.onchange = () => {
        const level = Number(sel.value);
        if (level > 0) state.teamBuffs.set(trait.cls, level);
        else state.teamBuffs.delete(trait.cls);
        onConfigChanged();
      };
      label.appendChild(sel);
      if (badge) label.appendChild(badge);
      label.appendChild(caption);
    } else {
      // A non-member gets the same bonus at every breakpoint, so asking for
      // one would be asking a question with no answer: on/off is the whole
      // decision. onLevel is simply the first active breakpoint.
      const check = document.createElement("input");
      check.type = "checkbox";
      check.checked = current > 0;
      check.onchange = () => {
        if (check.checked) state.teamBuffs.set(trait.cls, trait.onLevel);
        else state.teamBuffs.delete(trait.cls);
        onConfigChanged();
      };
      label.appendChild(check);
      if (badge) label.appendChild(badge);
      label.appendChild(caption);
    }

    container.appendChild(label);
  }

  // Every team trait is already in the buff bar: an empty panel would just
  // be a labelled box with nothing in it.
  $("teamTraitsPanel").hidden = shown === 0;
}

// ---------------------------------------------------------------------------
// Blackthorn panel
// ---------------------------------------------------------------------------

function blackthornSelected() {
  return state.cfg.buffs.some(([cls]) => cls === "Blackthorn");
}

function updateBlackthornPanel() {
  const panel = $("blackthornPanel");
  if (!state.catalog.blackthorn || !blackthornSelected()) {
    panel.hidden = true;
    state.cfg.blackthorn = null;
    return;
  }
  if (panel.hidden) {
    panel.hidden = false;
    $("btRole").value = state.catalog.blackthorn.roles[0];
    $("btCost").value = state.catalog.blackthorn.costs[0].value;
    refreshBlackthornStars();
  }
  syncBlackthornCfg();
}

function refreshBlackthornStars() {
  const stars = state.catalog.blackthorn.starsByCost[String($("btCost").value)];
  const starSel = $("btStar");
  const previous = starSel.value;
  starSel.innerHTML = "";
  for (const s of stars) starSel.add(new Option(s.label, s.value));
  if ([...starSel.options].some((o) => o.value === previous)) starSel.value = previous;
}

function syncBlackthornCfg() {
  if (!blackthornSelected()) return;
  state.cfg.blackthorn = {
    role: $("btRole").value,
    star: Number($("btStar").value),
    cost: Number($("btCost").value),
  };
}

// ---------------------------------------------------------------------------
// Slice options & the run loop
// ---------------------------------------------------------------------------

function sliceOptions() {
  // Mirrors the page: with a full item bar only the non-item slices remain,
  // and Blackthorn appears once the trait is in the buff bar.
  let options;
  const itemCount = state.cfg.items.filter((i) => i !== "NoItem").length;
  if (itemCount >= 3) {
    options = ["Trait", "Augment/Buff", "Wisp"];
  } else {
    options = state.catalog.slices.slice();
  }
  if (blackthornSelected()) options.push("Blackthorn");
  return options;
}

function onConfigChanged() {
  updateBlackthornPanel();
  // Re-rendered here rather than from renderBuffRows so that picking a trait
  // in the buff bar immediately disables its team-trait row.
  renderTeamTraits();
  state.selections.clear();
  refresh();
}

async function refresh() {
  const gen = ++state.gen;
  const options = sliceOptions();
  if (!options.includes(state.slice)) state.slice = options[0];
  buildPills($("sliceRadio"), options, state.slice, (v) => {
    state.slice = v;
    refresh();
  });

  renderHeader();
  updateStatsPanel(gen);

  const payload = await runSlice(state.slice, gen, true);
  if (gen !== state.gen || !payload) return;
  state.current = payload;
  renderResults();

  // Warm the other slices so radio clicks are cache hits; abandoned as soon
  // as the config changes again.
  for (const name of options) {
    if (gen !== state.gen) return;
    if (name !== state.slice) await runSlice(name, gen, false);
  }
}

async function runSlice(sliceName, gen, showStatus) {
  const key = JSON.stringify(cfgForSlice(sliceName));
  if (state.cache.has(key)) return state.cache.get(key);
  if (showStatus) setRunStatus("Simulating " + sliceName + "…");
  try {
    const payload = await rpc("run", key);
    if (state.cache.size > 60) state.cache.clear();
    state.cache.set(key, payload);
    return payload;
  } catch (err) {
    if (showStatus && gen === state.gen) setRunStatus("Simulation failed: " + err.message);
    return null;
  } finally {
    if (showStatus && gen === state.gen) setRunStatus(null);
  }
}

function setRunStatus(text) {
  const el = $("runStatus");
  el.hidden = !text;
  el.textContent = text || "";
}

// ---------------------------------------------------------------------------
// Rendering: header, stats panel
// ---------------------------------------------------------------------------

function renderHeader() {
  // Only the champion half is rewritten -- the enemy numbers in this heading
  // are live inputs, and replacing the heading's contents would blow them
  // away (and the caret with them, mid-typing).
  $("headerChamp").textContent = state.cfg.champ + " " + state.cfg.level;
  $("footerCaption").textContent =
    "Simulation computed in your browser" +
    (bootMs != null ? " · engine booted in " + (bootMs / 1000).toFixed(1) + "s" : "");
}

function buildStatsPanel(leftBonus, rightBonus) {
  const panel = $("statsPanel");
  if (panel.dataset.built) return;
  panel.dataset.built = "1";
  panel.innerHTML = "";

  for (const keys of [leftBonus, rightBonus]) {
    const col = document.createElement("div");
    col.className = "stats-col";
    for (const key of keys) {
      const row = document.createElement("div");
      row.className = "stat-row";

      const text = document.createElement("span");
      text.className = "stat-text";
      row.appendChild(text);

      if (key) {
        const field = BONUS_FIELDS[key];
        const wrap = document.createElement("span");
        wrap.className = "stat-bonus";
        wrap.textContent = "+";
        const input = document.createElement("input");
        input.type = "number";
        input.min = field.min;
        input.max = field.max;
        input.value = state.cfg.bonus[key] ?? 0;
        input.title = field.label;
        input.setAttribute("aria-label", field.label);
        input.onchange = () => {
          state.cfg.bonus[key] = clampInput(input);
          onConfigChanged();
        };
        selectZeroOnFocus(input);
        wrap.appendChild(input);
        row.appendChild(wrap);
      }
      col.appendChild(row);
    }
    panel.appendChild(col);
  }
}

async function updateStatsPanel(gen) {
  let info;
  try {
    info = await rpc("champInfo", JSON.stringify(cfgForSlice(state.slice)));
  } catch (err) {
    return; // panel is informational; the run's own error reporting suffices
  }
  if (gen !== state.gen) return;
  const s = info.stats;
  const r2 = (v) => Math.round(v * 100) / 100;
  const r3 = (v) => Math.round(v * 1000) / 1000;
  const r4 = (v) => Math.round(v * 10000) / 10000;
  const b = (v) => '<span class="c-blue">' + v + "</span>";
  const g = (v) => '<span class="c-green">' + v + "</span>";
  const r = (v) => '<span class="c-red">' + v + "</span>";

  const ad =
    s.bonusAd.addMultiplier === 1
      ? "AD: " + b(r2(s.atk.stat * s.bonusAd.stat)) + " = " + s.atk.base + " * " + g(r4(s.bonusAd.stat) + " AD")
      : "AD: " + b(r2(s.atk.stat * s.bonusAd.stat)) + " = " + s.atk.base + " * (1 + " + r(s.bonusAd.addMultiplier) + " * " + g(r4(s.bonusAd.add / 100) + " AD") + ")";
  const ap =
    s.ap.addMultiplier === 1
      ? "AP: " + b(r2(s.ap.stat)) + " = " + s.ap.base + " + " + g(r2(s.ap.add) + " AP")
      : "AP: " + b(r2(s.ap.stat)) + " = " + s.ap.base + " + " + r(s.ap.addMultiplier) + " * " + g(r2(s.ap.add) + " AP");

  // Two columns, each read top to bottom, in the order write_champion used:
  // offence and mana on the left, attack speed and crit on the right. Laying
  // these out as one flat grid instead reflows them across the columns and
  // scrambles that order.
  const leftText = [
    ad,
    ap,
    "DmgAmp: " + b(r2(s.dmgAmp.stat)) + " = " + s.dmgAmp.base + " + " + g(r4(s.dmgAmp.add) + " DmgAmp"),
    // Mana Regen sits above Mana here, unlike write_champion, so the line
    // carrying an input isn't stranded below the one that doesn't.
    "Mana Regen: " + b(r2(s.manaRegen.stat)) + " = " + s.manaRegen.base + " + " + g(r2(s.manaRegen.add) + " Mana"),
    "Mana: " + b(r2(s.curMana)) + " / " + b(r2(s.fullMana)),
    "Cast Time: " + b(s.castTime + " seconds"),
  ];
  const rightText = [
    "AS: " + b(r3(s.aspd.stat)) + " = " + s.aspd.base + " * (1 + " + g(r4(s.aspd.add) + " AS") + ")",
    "Crit Chance: " + b(r3(s.crit.stat)) + " = " + s.crit.base + " + " + g(r4(s.crit.add) + " Crit"),
    "Crit Dmg: " + b(r2(s.critDmg.stat)) + " = " + s.critDmg.base + " + " + g(r4(s.critDmg.add) + " CritDmg"),
    "ManaPerAttack: " + b(r2(s.manaPerAttack.stat)) + " = " + s.manaPerAttack.base + " + " + g(r2(s.manaPerAttack.add) + " Mana"),
    "Role: " + b(s.role),
    "Can SpellCrit: " + b(s.canSpellCrit ? "True" : "False"),
  ];

  // Which stat line carries which additive input. null = nothing to add.
  const leftBonus = ["ad", "ap", "dmgamp", "manaregen", null, null];
  const rightBonus = ["as", "crit", "critdmg", "mpa", null, null];

  buildStatsPanel(leftBonus, rightBonus);
  // Only the text is rewritten on refresh: the inputs are long-lived, and
  // replacing them would drop whatever is being typed (and the caret).
  const texts = leftText.concat(rightText);
  document.querySelectorAll("#statsPanel .stat-text").forEach((el, i) => {
    el.innerHTML = texts[i];
  });

  const notes = $("champNotes");
  notes.hidden = !s.notes;
  notes.textContent = s.notes ? "Notes: " + s.notes : "";
}

// ---------------------------------------------------------------------------
// Rendering: results table
// ---------------------------------------------------------------------------

function currentSelection() {
  if (!state.selections.has(state.slice)) state.selections.set(state.slice, new Map());
  return state.selections.get(state.slice);
}

// A plotted row owns its colour slot until it is unplotted. Assigning by
// position instead would repaint every line whenever the table is re-sorted
// or a row above is removed, so the colour would identify a rank rather than
// an item -- and the swatch in the table would drift from the line it names.
function togglePlotted(idx) {
  const selection = currentSelection();
  if (selection.has(idx)) {
    selection.delete(idx);
    return;
  }
  const taken = new Set(selection.values());
  let slot = 0;
  while (taken.has(slot)) slot++;
  selection.set(idx, slot);
}

function seriesColor(slot) {
  return COLORS[slot % COLORS.length];
}

function renderResults() {
  const payload = state.current;
  if (!payload) return;
  const isBlackthorn = payload.slice === "Blackthorn";
  const selection = currentSelection();

  // Same column logic as the page's display_dps checkbox.
  const dpsCols = state.displayDps
    ? DPS_TIMES.map((t) => ({ label: "Extra DPS (" + t + "s)", get: (row) => row.ratio[String(t)] }))
    : DPS_TIMES.map((t) => ({ label: "DPS at " + t, get: (row) => row.dps[String(t)] })).concat([
        { label: "Extra DPS (25s)", get: (row) => row.ratio["25"] },
      ]);

  // The label columns differ per slice, but sorting shouldn't care: every
  // column is described the same way, so the header handler is written once.
  const labelCols = isBlackthorn
    ? ["Role", "Star Level", "Cost"].map((name) => ({
        label: name,
        text: true,
        get: (row) => (row.blackthorn || {})[name] ?? "",
      }))
    : [
        {
          label: "Extra",
          text: true,
          get: (row) => row.extra,
          render: (cell, row) => {
            const src = state.icons.get(row.extraCls);
            const isTrait = state.traitTiers?.tiers?.[row.extraCls];
            if (isTrait) {
              const badge = traitBadge(row.extraCls, row.extraLevel);
              if (badge) cell.appendChild(badge);
            } else if (src) {
              const icon = document.createElement("img");
              icon.className = "row-icon";
              icon.src = src;
              // Decorative: the name sits right beside it, so a screen reader
              // announcing the file too would only repeat.
              icon.alt = "";
              icon.loading = "lazy";
              cell.appendChild(icon);
            }
            cell.appendChild(document.createTextNode(row.extra));
          },
        },
      ];
  const columns = labelCols.concat(dpsCols.map((col) => ({ ...col, shade: true })));

  // Column-wise magnitude scale. Each DPS interval is normalised against its
  // own column, which is the whole point: it answers "what is unusually good
  // *at 10 seconds*", a question a table-wide scale cannot ask because the
  // late columns are numerically larger and would own the top of the ramp.
  const scales = new Map();
  dpsCols.forEach((col) => {
    const values = payload.rows
      .map((row) => Number(col.get(row)))
      .filter((v) => Number.isFinite(v));
    const sorted = [...values].sort((a, z) => z - a);
    scales.set(col.label, {
      min: Math.min(...values),
      max: Math.max(...values),
      rank: (v) => sorted.indexOf(v) + 1,
      count: values.length,
    });
  });

  // Sorting is a view concern: the payload is left alone so that clearing the
  // sort returns to the order sim_entry delivered (ratio at 25s, descending).
  let rows = payload.rows;
  const sortCol = columns.find((col) => col.label === state.sort.key);
  if (sortCol) {
    const dir = state.sort.dir === "asc" ? 1 : -1;
    rows = [...rows].sort((a, b) => {
      const va = sortCol.get(a);
      const vb = sortCol.get(b);
      if (sortCol.text) return dir * String(va).localeCompare(String(vb));
      return dir * (Number(va) - Number(vb));
    });
  }

  const table = $("resultsTable");
  table.innerHTML = "";
  const thead = table.createTHead();
  const headRow = thead.insertRow();
  for (const col of columns) headRow.appendChild(sortableHeader(col));

  const tbody = table.createTBody();
  for (const row of rows) {
    const tr = tbody.insertRow();
    const slot = selection.get(row.idx);
    if (slot !== undefined) {
      tr.classList.add("plotted");
      // Drives the accent bar on the first cell, so the table's mark and the
      // chart's line are literally the same value.
      tr.style.setProperty("--series", seriesColor(slot));
    }
    tr.tabIndex = 0;
    tr.setAttribute("aria-pressed", slot !== undefined ? "true" : "false");
    tr.title = slot !== undefined ? "Click to remove from the chart" : "Click to plot";
    const toggle = () => {
      togglePlotted(row.idx);
      renderResults();
    };
    tr.onclick = toggle;
    tr.onkeydown = (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        toggle();
      }
    };
    for (const col of columns) {
      const cell = tr.insertCell();
      const value = col.get(row);
      if (col.render) col.render(cell, row);
      else cell.textContent = col.text ? value : formatNumber(value);
      if (col.shade && state.colorScale) {
        shadeCell(cell, Number(value), scales.get(col.label), col.label);
      }
    }
  }

  renderPlot();
}

function sortableHeader(col) {
  const th = document.createElement("th");
  th.className = "sortable";
  th.textContent = col.label;

  const active = state.sort.key === col.label;
  if (active) {
    th.classList.add("sorted");
    // Screen readers get the state from aria-sort; the arrow is for everyone
    // else. Kept in its own span so it can't be picked up as cell text.
    th.setAttribute("aria-sort", state.sort.dir === "asc" ? "ascending" : "descending");
    const arrow = document.createElement("span");
    arrow.className = "sort-arrow";
    arrow.textContent = state.sort.dir === "asc" ? " ▲" : " ▼";
    th.appendChild(arrow);
  }

  th.onclick = () => {
    if (state.sort.key === col.label) {
      state.sort = { key: col.label, dir: state.sort.dir === "desc" ? "asc" : "desc" };
    } else {
      // Numbers open with the best row first; names open A to Z.
      state.sort = { key: col.label, dir: col.text ? "asc" : "desc" };
    }
    renderResults();
  };
  return th;
}

// Sequential fill: one hue, the page surface at the column's minimum rising
// to blue step 500 at its maximum. Step 500 is where the ramp stops because
// it is the brightest step that still carries #fafafa text at 4.5:1 (5.17:1;
// step 450 is 4.23:1, which fails), and it clears 3:1 against the surface, so
// every cell stays readable without ever flipping the ink colour. Painting
// with alpha over the surface *is* the ramp -- rgba(37,106,191,1) is exactly
// #256abf -- which keeps the steps monotone by construction.
const SCALE_RGB = "37, 106, 191";

function shadeCell(cell, value, scale, label) {
  if (!Number.isFinite(value)) return;
  const span = scale.max - scale.min;
  // A column with no spread carries no information to encode; leave it bare
  // rather than painting every cell the same shade.
  const t = span > 0 ? (value - scale.min) / span : 0;
  cell.style.backgroundColor = "rgba(" + SCALE_RGB + ", " + t.toFixed(3) + ")";
  // The number is already printed, so hover adds the standing it can't show.
  cell.title = label + ": rank " + scale.rank(value) + " of " + scale.count;
}

function formatNumber(v) {
  if (typeof v !== "number") return String(v);
  return Number.isInteger(v) ? String(v) : v.toFixed(2);
}

// ---------------------------------------------------------------------------
// Rendering: chart, index log, pie (mirror of class_utilities.plot_df)
// ---------------------------------------------------------------------------

const COLORS = [
  "#4cc9f0", "#f72585", "#ffd166", "#80ed99", "#f8961e",
  "#56cfe1", "#b8f2e6", "#ffcad4", "#c77dff", "#72efdd",
];
const FONT_COLOR = "#EAEAEA";
const GRID_COLOR = "rgba(255,255,255,0.12)";

function selectedRows() {
  const payload = state.current;
  if (!payload) return [];
  const selection = currentSelection();
  const byIdx = new Map(payload.rows.map((row) => [row.idx, row]));
  // Ordered by slot, i.e. by when each row was added, so the legend doesn't
  // reshuffle when the table is sorted.
  return [...selection.entries()]
    .sort((a, b) => a[1] - b[1])
    .map(([idx, slot]) => ({ row: byIdx.get(idx), slot }))
    .filter((entry) => entry.row);
}

function renderPlot() {
  const entries = selectedRows();
  const rows = entries.map((entry) => entry.row);
  const hasRows = entries.length > 0;
  $("plotHint").hidden = hasRows;
  $("plotColumns").hidden = !hasRows;
  if (!hasRows) {
    Plotly.purge($("chart"));
    Plotly.purge($("pie"));
    return;
  }

  const payload = state.current;
  const traces = [];
  entries.forEach(({ row, slot }) => {
    const tl = payload.timelines[String(row.idx)];
    const label = row.extra;
    // The slot, not the loop index: the line keeps the colour its table row
    // is wearing however the table is sorted.
    const color = seriesColor(slot);
    traces.push({
      x: tl.t,
      y: tl.cum,
      mode: "lines",
      line: { width: 3, color, shape: "linear" },
      name: label,
      hoverinfo: "skip",
      showlegend: true,
    });
    // Invisible midpoint markers reporting the left endpoint: identical to
    // the hover-helper trick in plot_df.
    if (tl.t.length >= 2) {
      const mids = [];
      const prevVals = [];
      const prevTimes = [];
      for (let k = 0; k + 1 < tl.t.length; k++) {
        mids.push((tl.t[k] + tl.t[k + 1]) / 2);
        prevVals.push(tl.cum[k]);
        prevTimes.push(tl.t[k]);
      }
      traces.push(hoverHelper(mids, prevVals, prevTimes, label));
    } else {
      traces.push(hoverHelper(tl.t, tl.cum, tl.t, label));
    }
  });

  const first = rows[0];
  const layout = {
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    title: {
      text: first.name + " " + first.level + " Damage Chart",
      x: 0.5,
      font: { size: 26, color: FONT_COLOR },
    },
    font: { size: 14, color: FONT_COLOR },
    xaxis: {
      title: { text: "Time (s)", font: { color: FONT_COLOR } },
      showgrid: true,
      gridcolor: GRID_COLOR,
      zeroline: false,
      tickfont: { color: FONT_COLOR },
      showspikes: true,
      spikemode: "across",
      spikesnap: "cursor",
      spikethickness: 1,
      spikecolor: "#bbbbbb",
      spikedash: "dot",
    },
    yaxis: {
      title: { text: "Damage", font: { color: FONT_COLOR } },
      showgrid: true,
      gridcolor: GRID_COLOR,
      zeroline: false,
      tickformat: ",",
      tickfont: { color: FONT_COLOR },
    },
    legend: {
      x: 0.02,
      y: 0.98,
      xanchor: "left",
      yanchor: "top",
      bgcolor: "rgba(20,20,20,0.85)",
      bordercolor: "rgba(0,0,0,0.2)",
      borderwidth: 1,
      font: { size: 16, color: "#FFFFFF" },
    },
    hovermode: "x unified",
    hoverlabel: {
      namelength: -1,
      align: "left",
      bgcolor: "rgba(20,20,20,0.6)",
      bordercolor: "rgba(255,255,255,0.12)",
    },
    hoverdistance: 20,
    spikedistance: -1,
    margin: { l: 60, r: 20, t: 70, b: 60 },
  };
  Plotly.react($("chart"), traces, layout, { displaylogo: false, responsive: true });

  renderLogControls(rows);
}

function hoverHelper(x, y, customdata, name) {
  return {
    x,
    y,
    customdata,
    mode: "markers",
    marker: { size: 0.1, opacity: 0 },
    name,
    showlegend: false,
    hovertemplate:
      "<b>%{fullData.name}</b><br>t=%{customdata:.1f}s<br>Total Dmg=%{y:,.0f}<extra></extra>",
  };
}

function renderLogControls(rows) {
  const logSel = $("logSelect");
  const previous = logSel.value;
  logSel.innerHTML = "";
  for (const row of rows) logSel.add(new Option(row.extra, row.idx));
  if ([...logSel.options].some((o) => o.value === previous)) logSel.value = previous;
  logSel.onchange = () => renderLog(Number(logSel.value));
  renderLog(Number(logSel.value));
}

function renderLog(idx) {
  const tl = state.current.timelines[String(idx)];
  if (!tl) return;

  const table = $("logTable");
  table.innerHTML = "";
  const headRow = table.createTHead().insertRow();
  for (const label of ["Time", "Dmg", "Type", "AS", "Mana"]) {
    headRow.insertCell().textContent = label;
  }
  const tbody = table.createTBody();
  for (let i = 0; i < tl.t.length; i++) {
    const tr = tbody.insertRow();
    tr.insertCell().textContent = round2(tl.t[i]);
    tr.insertCell().textContent = round2(tl.dmg[i]);
    tr.insertCell().textContent = tl.type[i];
    tr.insertCell().textContent = round2(tl.as[i]);
    tr.insertCell().textContent =
      tl.manaFull[i] > 0
        ? tl.manaCur[i].toFixed(1) + " / " + round2(tl.manaFull[i])
        : tl.manaCur[i].toFixed(1);
  }

  // Damage split pie for the selected trial.
  const totals = { physical: 0, magical: 0, true: 0 };
  for (let i = 0; i < tl.dmg.length; i++) {
    let kind = tl.type[i];
    if (kind === "magic") kind = "magical";
    if (kind in totals) totals[kind] += tl.dmg[i];
  }
  const allLabels = ["Physical", "Magic", "True"];
  const allValues = [totals.physical, totals.magical, totals.true];
  const allColors = ["#de4b39", "#2db2e3", "#f0e6d2"];
  const labels = [], values = [], colors = [];
  allValues.forEach((v, i) => {
    if (v > 0) {
      labels.push(allLabels[i]);
      values.push(v);
      colors.push(allColors[i]);
    }
  });
  if (!values.length) {
    Plotly.purge($("pie"));
    return;
  }
  Plotly.react(
    $("pie"),
    [
      {
        type: "pie",
        labels,
        values,
        hole: 0.4,
        textinfo: "label+percent",
        marker: { colors },
        sort: false,
      },
    ],
    {
      title: { text: "Damage Distribution", x: 0.5 },
      margin: { l: 20, r: 20, t: 40, b: 20 },
      height: 300,
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      font: { color: FONT_COLOR },
      showlegend: false,
    },
    { displaylogo: false, responsive: true }
  );
}

function round2(v) {
  return String(Math.round(v * 100) / 100);
}
