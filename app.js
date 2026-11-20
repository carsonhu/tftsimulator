// app.js
//
// UI logic for the static frontend. All simulation happens in worker.js
// (Pyodide); this file only builds controls from the catalog, assembles the
// config object sim_entry.py documents, and renders what comes back.

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

// The DPS columns (sim_entry.DPS_WINDOWS): average DPS over fights ending in each window; the catalog lists them.
let DPS_WINDOWS = [];
let HEADLINE = null;

// Bonus stats, keyed as sim_entry expects them. Each is rendered beside the
// stat it feeds in the Base stats panel.
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
    layout: { targets: 2 }, // the number of targets (layout.py); boot reads the default
    takedowns: 0,
    // a table row's own number by class (Hold the Line's units, Comeback Story's Health, Cappa Juice's takedowns):
    // typed into the row's box (rowNameWithInput); a class not here runs at its default
    rowInputs: {},
    bonus: { ad: 0, ap: 0, as: 0, dmgamp: 0, crit: 0, critdmg: 0, manaregen: 0, mpa: 0 },
    stage: "4-1",
    items: ["NoItem", "NoItem", "NoItem"],
    buffs: [], // [cls, level, params]
    enemy: { hp: 1800, armor: 100, mr: 100 },
    frame_rate: 30,
    t: 30,
  },
  // Team traits the champion is NOT a member of: cls -> {level, params}.
  // Kept out of cfg.buffs so the buff bar stays the buff bar; merged in by
  // cfgForSlice. params is 0 for an "Is X" flag, which is what the flag
  // means, and the ticked bits for a Flags trait (Heartsteel). Being
  // real entries in cfg.buffs from there on means the Trait slice sweeps
  // their other breakpoints too, same as any hand-picked buff.
  teamBuffs: new Map(),
  ownTraits: new Set(), // the champion's own traits (selectChampion): never removed from the buff bar, only set to 0
  slice: "Craftable",
  displayDps: false,
  colorScale: true,
  // Class name -> icon URL, from the per-group index.json files. A row draws
  // art only if its class is in here, so rows without art cost no failed
  // requests.
  icons: new Map(),
  // Class name -> the build's card for that item, augment or trait (sim_entry.get_cards), shown on hover. Reloaded
  // when the build changes; empty if the request fails, which only means no cards.
  cards: new Map(),
  // Lower-cased rich-text tags with a glyph in icons/stats (tools/icons.py), for a card's stat line.
  statIcons: new Set(),
  // icons/traits/tiers.json: {tiers: {cls: {level: tier}}, colours: {...}}.
  traitTiers: null,
  // Which header the table is sorted by. key null = the order sim_entry
  // delivered, which is already the headline window's ratio, descending.
  sort: { key: null, dir: "desc" },
  // Payload for the slice on screen, and per-slice plot selections. Any
  // config change (not a slice change) clears selections.
  current: null,
  currentCfg: null, // the config that produced `current`, for the chart's summary heading
  playhead: null, // the fight viewer's time in seconds (null at 0 s), drawn on the chart as a line
  hoverTime: null, // the time under the pointer while it is over the plot; the line and card go there instead
  selections: new Map(), // slice -> Set(idx)
  cache: new Map(), // config-json -> payload
  gen: 0,
  // The fight viewer's row (viz.js): {slice, extra} by the row's label, so it survives a re-run; none or not in the
  // table = the NoItem row. vizSeconds: the fight's length.
  vizRow: null,
  vizSeconds: 30,
  // Redraws each item slot's tile (icons arrive after boot).
  slotDraws: [],
};

const $ = (id) => document.getElementById(id);

function cfgForSlice(sliceName) {
  const cfg = Object.assign(JSON.parse(JSON.stringify(state.cfg)), {
    slice: sliceName,
  });
  // which of them came from Team Traits: the Trait slice sweeps the others, the Team Traits slice these
  cfg.team = [];
  for (const [cls, pick] of state.teamBuffs) {
    // renderTeamTraits drops any trait that is in the buff bar, so this can
    // only collide in the instant between the two updates. The buff bar's
    // entry wins; a second entry for one class would also give the Trait
    // slice two rows per breakpoint.
    if (!pick || cfg.buffs.some(([c]) => c === cls)) continue;
    cfg.team.push(cls);
    // at 0 it adds nothing to the fight, but is still sent so its Team Traits row ("Swiftstriker") runs
    cfg.buffs.push([cls, Math.max(0, pick.level), pick.params]);
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
  DPS_WINDOWS = state.catalog.dpsWindows;
  HEADLINE = state.catalog.headline;
  state.buffMeta = new Map(state.catalog.buffs.map((b) => [b.cls, b]));
  state.itemKinds = new Map(state.catalog.sidebarItems.map((i) => [i.cls, i.kind]));
  // Named explicitly (not left to "newest") so the run cache keys on it.
  state.cfg.build = state.catalog.builds.length ? state.catalog.builds[0].version : null;
  await loadCards();

  buildStaticControls();
  FightViewer.init(rpc, (cls) => state.icons.get(cls), (seconds) => {
    state.playhead = seconds;
    placePlayhead();
  });
  // Plotly's "responsive" only follows window resizes; the chart's box also changes with the layout around it (the
  // heading wrapping, the pane appearing), so follow the box itself.
  new ResizeObserver(() => {
    if (window.Plotly && $("chart").data && !$("chartWrap").hidden) Plotly.Plots.resize($("chart"));
  }).observe($("chartWrap"));
  $("vizRowSel").onchange = () => {
    state.vizRow = { slice: state.slice, extra: $("vizRowSel").value };
    renderResults();
  };
  // Hovering the plot moves the line and its card to the time under the pointer (the same card the viewer's
  // playhead draws; Plotly's own hover is off); leaving it brings back the viewer's time.
  $("chartWrap").addEventListener("pointermove", (event) => {
    const gd = $("chart");
    const xa = gd._fullLayout && gd._fullLayout.xaxis;
    const ya = gd._fullLayout && gd._fullLayout.yaxis;
    let t = null;
    if (xa && ya && gd.data) {
      const box = $("chartWrap").getBoundingClientRect();
      const x = event.clientX - box.left - xa._offset;
      const y = event.clientY - box.top - ya._offset;
      if (x >= 0 && x <= xa._length && y >= 0 && y <= ya._length) t = Math.max(0, xa.p2l(x));
    }
    if (t !== state.hoverTime) {
      state.hoverTime = t;
      placePlayhead();
    }
  });
  $("chartWrap").addEventListener("pointerleave", () => {
    state.hoverTime = null;
    placePlayhead();
  });
  const lengths = state.catalog.defaults.traceSeconds || [30];
  for (const s of lengths) $("vizLength").appendChild(new Option(s + " s", String(s)));
  state.vizSeconds = lengths[0];
  $("vizLength").onchange = () => {
    state.vizSeconds = Number($("vizLength").value);
    updateViz();
  };
  await selectChampion(state.catalog.defaultChampion || state.catalog.champions[0].name, { keepLevel: false });

  $("boot-status").hidden = true;
  $("layout").hidden = false;
}

// ---------------------------------------------------------------------------
// Cards: an item's, augment's or trait's in-game text on hover
// ---------------------------------------------------------------------------

async function loadCards() {
  if (!state.statIcons.size) {
    try {
      const response = await fetch("icons/stats/index.json");
      if (response.ok) state.statIcons = new Set(await response.json());
    } catch (err) {
      // no glyphs: the stat line falls back to the tags' names
    }
  }
  try {
    const cards = await rpc("cards", JSON.stringify({ build: state.cfg.build }));
    state.cards = new Map(Object.entries(cards));
  } catch (err) {
    state.cards = new Map();
  }
}

function cardElement() {
  let el = $("hoverCard");
  if (!el) {
    el = document.createElement("div");
    el.id = "hoverCard";
    el.setAttribute("role", "tooltip");
    el.hidden = true;
    document.body.appendChild(el);
  }
  return el;
}

// Fills the card for a class; false when the build has none (NoItem, a debuff row), so nothing is shown.
// level: a trait row's breakpoint, whose tier line is marked. team: a Team Traits trait, shown as only its team-wide
// half (the card's "team", BuildTrait.team_card) when the build has one.
function fillCard(cls, level, hint, team = false) {
  const card = state.cards.get(cls);
  if (!card) return false;
  const teamCard = team ? card.team : null;
  const el = cardElement();
  el.innerHTML = "";
  const head = document.createElement("div");
  head.className = "card-head";
  const src = state.icons.get(cls);
  if (src && !card.tiers.length) {
    const icon = document.createElement("img");
    icon.src = src;
    icon.alt = "";
    head.appendChild(icon);
  } else if (src) {
    const badge = traitBadge(cls, level);
    if (badge) head.appendChild(badge);
  }
  const title = document.createElement("div");
  title.className = "card-title";
  const name = document.createElement("div");
  name.className = "card-name";
  name.textContent = card.name;
  title.appendChild(name);
  if (card.kind || teamCard) {
    const kind = document.createElement("div");
    kind.className = "card-kind";
    kind.textContent = teamCard ? "Team-wide bonus" : card.kind;
    title.appendChild(kind);
  }
  head.appendChild(title);
  el.appendChild(head);
  const add = (cls_, text) => {
    const div = document.createElement("div");
    div.className = cls_;
    div.textContent = text;
    el.appendChild(div);
    return div;
  };
  // The stat line as the game draws it: each value followed by its stat's glyph, in the glyph's colour.
  const statParts = (line, stats) => {
    for (const [value, tag] of stats) {
      const part = document.createElement("span");
      part.className = "card-stat";
      part.appendChild(document.createTextNode(value));
      const glyph = tag && tag.toLowerCase();
      if (glyph && state.statIcons.has(glyph)) {
        const img = document.createElement("img");
        img.src = `icons/stats/${glyph}.png`;
        img.alt = tag;
        img.title = tag;
        part.appendChild(img);
      } else if (tag) {
        part.appendChild(document.createTextNode(tag));
      }
      line.appendChild(part);
    }
  };
  if (teamCard) {
    // the team-wide half: its sentence, then a line per breakpoint (or per Heartsteel member), the board's marked
    add("card-text", teamCard.text);
    const reached = teamCard.rows.filter((r) => r.threshold != null && level != null && r.threshold <= level).pop();
    for (const row of teamCard.rows) {
      // a breakpoint line is dim until the board reaches it; a line that always applies (a Heartsteel member) isn't
      const line = add("card-tier card-team-row" + (row.threshold == null ? " always" : row === reached ? " active" : ""), "");
      if (row.label) line.appendChild(Object.assign(document.createElement("span"), { className: "card-team-label", textContent: row.label }));
      statParts(line, row.stats);
      if (row.text) line.appendChild(document.createTextNode(row.text));
    }
    if (hint) add("card-hint", hint);
    return true;
  }
  if (card.stats.length) statParts(add("card-stats", ""), card.stats);
  if (card.text) add("card-text", card.text);
  // the simulator's own note on how it works (sim_entry CARD_NOTE): "[Multiplicative] The attack speed multiplies ..."
  if (card.note) {
    const note = add("card-note", "");
    note.append(Object.assign(document.createElement("span"), { className: "card-note-tag", textContent: card.note.tag }),
      card.note.text);
  }
  const active = card.tiers.filter((t) => level != null && t.threshold <= level).pop();
  for (const t of card.tiers) richText(add("card-tier" + (t === active ? " active" : ""), ""), t.text);
  if (hint) add("card-hint", hint);
  return true;
}

// A card line with the game's stat tags drawn as their glyphs: "12%AP, 25%AP for Arcanists" -> 12% [AP icon], ...
// A word not in the icon set ("1 Big Shot", "150 Shield") stays text.
function richText(el, text) {
  const re = /(\d+(?:\.\d+)?%?)([A-Za-z]+)/g;
  let last = 0;
  for (const m of text.matchAll(re)) {
    const glyph = m[2].toLowerCase();
    if (!state.statIcons.has(glyph)) continue;
    el.appendChild(document.createTextNode(text.slice(last, m.index) + m[1]));
    const img = document.createElement("img");
    img.className = "card-glyph";
    img.src = `icons/stats/${glyph}.png`;
    img.alt = m[2];
    img.title = m[2];
    el.appendChild(img);
    last = m.index + m[0].length;
  }
  el.appendChild(document.createTextNode(text.slice(last)));
}

function placeCard(event) {
  const el = cardElement();
  const pad = 14;
  const { innerWidth: w, innerHeight: h } = window;
  const r = el.getBoundingClientRect();
  let x = event.clientX + pad;
  let y = event.clientY + pad;
  if (x + r.width > w - 8) x = Math.max(8, event.clientX - pad - r.width);
  if (y + r.height > h - 8) y = Math.max(8, event.clientY - pad - r.height);
  el.style.left = x + "px";
  el.style.top = y + "px";
}

// Shows cls's card while the pointer is over target. getLevel/hint are read at each entry, so a re-rendered row
// needs no rebinding. Returns whether the build has a card for cls. cls may be a function, read at each entry
// (an item slot or buff row whose choice changes): then it always binds, and shows a card only when there is one.
function attachCard(target, cls, getLevel = () => null, hint = null, team = false) {
  const which = typeof cls === "function" ? cls : () => cls;
  if (typeof cls !== "function" && !state.cards.has(cls)) return false;
  target.addEventListener("mouseenter", (event) => {
    if (!fillCard(which(), getLevel(), typeof hint === "function" ? hint() : hint, typeof team === "function" ? team() : team)) return;
    cardElement().hidden = false;
    placeCard(event);
  });
  target.addEventListener("mousemove", placeCard);
  target.addEventListener("mouseleave", () => {
    cardElement().hidden = true;
  });
  return true;
}

function hideCard() {
  const el = $("hoverCard");
  if (el) el.hidden = true;
}
// A click re-renders the table and closes menus, which removes the hovered element without a mouseleave; the
// next pointer move over the new row shows its card again.
document.addEventListener("mousedown", hideCard, true);
window.addEventListener("scroll", hideCard, true);

// icons.py writes one directory per group. Class names are unique across the
// modules they come from, so a flat class -> URL map is enough.
const ICON_GROUPS = ["items", "augments", "traits", "champions"];

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
  if (state.cfg.champ) {
    renderChampPick();
    for (const draw of state.slotDraws) draw();
    renderBuffRows();
  }
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

  // Mobile drawer (CSS turns all of this on below 900px; on desktop the
  // toggle and backdrop are display:none and the class is inert).
  const toggle = $("sidebarToggle");
  const setSidebar = (open) => {
    document.body.classList.toggle("sidebar-open", open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.innerHTML = open ? "&times;" : "&#9776;";
  };
  toggle.onclick = () =>
    setSidebar(!document.body.classList.contains("sidebar-open"));
  $("sidebarBackdrop").onclick = () => setSidebar(false);
  document.addEventListener("keydown", (event) => {
    // The picker stops the Escape that closes it, so this only fires once
    // nothing narrower wants the key.
    if (event.key === "Escape") setSidebar(false);
  });

  // Champion: the hidden <select> (the catalog's order: by cost, then name) is
  // what runs; the portrait button opens the grid over it.
  const champSel = $("champ");
  for (const c of cat.champions) champSel.add(new Option(c.label || c.name, c.name));
  hookValue(champSel, renderChampPick);
  champSel.onchange = () => selectChampion(champSel.value, { keepLevel: false });
  $("champPick").onclick = () =>
    Picker.open($("champPick"), {
      title: "Champion",
      groups: champGroups(),
      selected: champForms(champSel.value)[0]?.name ?? champSel.value,
      onPick: (value) => pickInto(champSel, value),
    });

  $("level").onchange = () => {
    state.cfg.level = Number($("level").value);
    renderStars();
    // Re-read the champ's own defaults, but keep what you configured: it is
    // the same champion, so nothing about a star level can make the buffs or
    // target count you picked the wrong ones. Re-seeding here used to throw
    // them away -- setting the level last, after configuring the bar, reset
    // every trait to its first level and every slider to its default.
    selectChampion(state.cfg.champ, { keepLevel: true, keepConfig: true });
  };

  // Client build the numbers come from (newest first). Every champion number
  // depends on it, so a change re-reads the champion like a level change.
  const buildSel = $("build");
  for (const b of cat.builds) buildSel.add(new Option(b.label, b.version));
  buildSel.title = buildSel.value;
  buildSel.onchange = () => {
    state.cfg.build = buildSel.value;
    buildSel.title = buildSel.value;
    loadCards();
    selectChampion(state.cfg.champ, { keepLevel: true, keepConfig: true });
  };

  const stageSel = $("stage");
  for (const s of cat.defaults.stages) stageSel.add(new Option(s, s));
  stageSel.value = cat.defaults.stageDefault;
  stageSel.onchange = () => {
    state.cfg.stage = stageSel.value;
    onConfigChanged();
  };


  // Takedowns this game: Cappa Juice's Hats.
  $("takedowns").onchange = () => {
    state.cfg.takedowns = clampInput($("takedowns"));
    delete state.cfg.rowInputs.CappaJuice; // its row follows the takedowns again until it is typed over
    onConfigChanged();
  };
  selectZeroOnFocus($("takedowns"));

  // Item slots: a tile per slot over a hidden <select>.
  const itemRows = $("itemRows");
  state.slotDraws = [];
  for (let n = 0; n < cat.defaults.numItems; n++) {
    const slot = document.createElement("div");
    slot.className = "item-slot";
    const sel = document.createElement("select");
    sel.hidden = true;
    sel.setAttribute("aria-label", "Item " + (n + 1));
    for (const item of cat.sidebarItems) sel.add(new Option(item.name, item.cls));
    sel.value = "NoItem";
    const tile = document.createElement("button");
    tile.type = "button";
    tile.className = "slot-tile";
    tile.setAttribute("aria-haspopup", "dialog");
    const clear = document.createElement("button");
    clear.type = "button";
    clear.className = "slot-clear";
    clear.innerHTML = "&times;";
    clear.title = "Empty this slot";
    clear.setAttribute("aria-label", "Empty item slot " + (n + 1));
    const draw = () => drawItemTile(tile, clear, sel.value);
    hookValue(sel, draw);
    sel.onchange = () => {
      state.cfg.items[n] = sel.value;
      addEmblemTrait(sel.value);
      onConfigChanged();
    };
    tile.onclick = () =>
      Picker.open(tile, {
        title: "Item " + (n + 1),
        groups: itemGroups(),
        selected: sel.value,
        none: { label: "Empty slot", value: "NoItem" },
        cards: true,
        onPick: (value) => pickInto(sel, value),
      });
    clear.onclick = () => pickInto(sel, "NoItem");
    attachCard(tile, () => sel.value, () => null, "Click to change");
    slot.append(sel, tile, clear);
    itemRows.appendChild(slot);
    state.slotDraws.push(draw);
    draw();
  }
  $("resetItems").onclick = () => {
    state.cfg.items = state.cfg.items.map(() => "NoItem");
    for (const sel of itemRows.querySelectorAll("select")) sel.value = "NoItem";
    onConfigChanged();
  };

  // The number of targets (layout.py): shown only for a champion whose damage depends on it (catalog "area").
  state.cfg.layout = { targets: cat.defaults.layout.targets };
  $("layoutTargets").max = cat.defaults.layout.max;
  $("layoutTargets").value = state.cfg.layout.targets;
  $("layoutTargetsValue").textContent = state.cfg.layout.targets;
  bindSlider("layoutTargets", "layoutTargetsValue", (v) => {
    state.cfg.layout.targets = v;
    renderTargetsSeg();
    onConfigChanged();
  });
  renderTargetsSeg();

  // A buff row is added by picking its buff, so the bar never holds an empty
  // row that runs the whole table again for nothing.
  $("addBuff").onclick = () => {
    if (state.cfg.buffs.length >= cat.defaults.numBuffs.max) return;
    Picker.open($("addBuff"), {
      title: "Add a buff",
      // what the bar already holds is set in its own row
      groups: buffGroups().map((g) => ({
        ...g,
        entries: g.entries.filter((e) => !state.cfg.buffs.some(([cls]) => cls === e.value)),
      })),
      selected: null,
      cards: true,
      onPick: (value) => {
        if (state.cfg.buffs.some(([cls]) => cls === value)) return;
        state.cfg.buffs = state.cfg.buffs.filter(([cls]) => cls !== "NoBuff");
        state.cfg.buffs.push(defaultBuffTuple(value));
        renderBuffRows();
        onConfigChanged();
      },
    });
  };

  $("addTeamTrait").onclick = () => {
    const choices = teamTraitChoices();
    if (!choices.length) return;
    Picker.open($("addTeamTrait"), {
      title: "Add a team trait",
      cards: "team",
      groups: [{
        label: "Team traits",
        entries: choices.map((t) => ({
          value: t.cls, label: t.name, icon: state.icons.get(t.cls), badge: () => traitBadge(t.cls, t.onLevel),
        })),
      }],
      selected: null,
      onPick: (value) => {
        const trait = choices.find((t) => t.cls === value);
        if (trait) addTeamTrait(trait);
      },
    });
  };

  for (const [id, key] of [
    ["enemyHp", "hp"],
    ["enemyArmor", "armor"],
    ["enemyMr", "mr"],
  ]) {
    const input = $(id);
    input.value = state.cfg.enemy[key];
    sizeInlineNumber(input);
    // Width tracks the digits as they are typed, so the bar reads as a
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
  // Show: DPS | Ratio vs Base (state.displayDps true = the ratio columns, the old checkbox's meaning).
  const modeButtons = [...document.querySelectorAll("#valueMode button")];
  const drawMode = () => {
    for (const btn of modeButtons) {
      const on = (btn.dataset.mode === "ratio") === state.displayDps;
      btn.classList.toggle("active", on);
      btn.setAttribute("aria-checked", String(on));
    }
  };
  for (const btn of modeButtons) {
    btn.onclick = () => {
      state.displayDps = btn.dataset.mode === "ratio";
      drawMode();
      renderResults();
    };
  }
  drawMode();

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

// ---------------------------------------------------------------------------
// Pickers: champions, items and buffs as icon grids
// ---------------------------------------------------------------------------

// Each choice is still a hidden <select>: everything else reads sel.value and
// listens for change, so the tiles are only a skin over the real control.
// hookValue makes an assignment to .value (Clear, the boot default, code
// written later) redraw the skin as well, so no caller has to remember to.
function hookValue(select, onSet) {
  const native = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, "value");
  Object.defineProperty(select, "value", {
    configurable: true,
    get() {
      return native.get.call(this);
    },
    set(value) {
      native.set.call(this, value);
      onSet();
    },
  });
}

// What a pick does: set the select and fire the change the page hangs off
// (assigning .value alone fires nothing).
function pickInto(select, value) {
  if (select.value === String(value)) return;
  select.value = String(value);
  select.dispatchEvent(new Event("change"));
}

// The game's shop colours, by cost.
const COST_COLOURS = { 1: "#9aa4b1", 2: "#1fbf6a", 3: "#2b8ef0", 4: "#c25be0", 5: "#f2b33d" };

function costColour(cost) {
  return COST_COLOURS[cost] || "#6c7286";
}

function champMeta(name = state.cfg.champ) {
  return state.catalog.champions.find((c) => c.name === name);
}

function champGroups() {
  const groups = new Map();
  for (const c of state.catalog.champions) {
    if (c.variantOf) continue; // a form: chosen with the switch beside the stars, not here
    if (!groups.has(c.cost)) {
      groups.set(c.cost, { label: c.cost + " cost", colour: costColour(c.cost), entries: [] });
    }
    groups.get(c.cost).entries.push({
      value: c.name,
      label: c.label || c.name,
      icon: state.icons.get(c.name),
      colour: costColour(c.cost),
    });
  }
  return [...groups.values()];
}

function itemGroups() {
  const order = ["Craftable", "Artifact", "Radiant", "Emblem"];
  const groups = order.map((kind) => ({ label: kind, entries: [] }));
  for (const item of state.catalog.sidebarItems) {
    const group = groups[order.indexOf(item.kind)];
    if (group) {
      group.entries.push({ value: item.cls, label: item.name, icon: state.icons.get(item.cls), frame: itemFrame(item.cls) });
    }
  }
  return groups;
}

function buffGroups() {
  const groups = { Trait: { label: "Traits", entries: [] }, Augment: { label: "Augments", entries: [] } };
  for (const b of state.catalog.buffs) {
    const group = groups[b.kind];
    if (!group) continue;
    const onLevel = b.levels.find((l) => l > 0) ?? b.levels[0];
    group.entries.push({
      value: b.cls,
      label: b.name,
      icon: state.icons.get(b.cls),
      badge: b.kind === "Trait" ? () => traitBadge(b.cls, onLevel) : null,
    });
  }
  return [groups.Trait, groups.Augment];
}

// The frame the game draws over an artifact's or a radiant's icon (icons/frames, tools/icons.py), or null.
function itemFrame(cls) {
  const kind = state.itemKinds && state.itemKinds.get(cls);
  return kind === "Artifact" || kind === "Radiant" ? kind : null;
}

// An item's icon, inside its frame when it has one.
function itemIcon(src, cls, className) {
  const img = document.createElement("img");
  img.src = src;
  img.alt = "";
  img.loading = "lazy";
  const frame = itemFrame(cls);
  if (!frame) {
    img.className = className;
    return img;
  }
  const wrap = document.createElement("span");
  wrap.className = className + " item-framed";
  wrap.dataset.frame = frame;
  wrap.appendChild(img);
  return wrap;
}

// The art for one tile: a trait's tier badge, else the icon, else initials, so
// nothing ever renders as a blank square.
function tileArt(className, { icon, badge, label, frame }) {
  const art = document.createElement("span");
  art.className = className;
  if (frame && icon) {
    art.classList.add("item-framed");
    art.dataset.frame = frame;
  }
  const b = badge && badge();
  if (b) {
    art.classList.add("is-badge");
    art.appendChild(b);
  } else if (icon) {
    const img = document.createElement("img");
    img.src = icon;
    img.alt = "";
    img.loading = "lazy";
    art.appendChild(img);
  } else {
    art.classList.add("no-icon");
    art.textContent = String(label || "?")
      .split(/\s+/)
      .map((w) => w[0])
      .join("")
      .slice(0, 2);
  }
  return art;
}

// A floating grid of tiles under its control, grouped (by cost, by item kind,
// traits / augments), with a search box that filters as you type. Arrow keys
// move, Enter picks, Escape or a click outside closes.
const Picker = (() => {
  let box = null;
  let anchorEl = null;

  function outside(event) {
    if (!box || box.contains(event.target)) return;
    // a click on the control that opened it closes it (open() sees it closed and stops)
    if (anchorEl && anchorEl.contains(event.target)) {
      anchorEl.dataset.justClosed = "1";
    }
    hide();
  }

  function onScroll(event) {
    if (box && !box.contains(event.target)) hide();
  }

  function hide() {
    if (!box) return;
    box.remove();
    box = null;
    document.removeEventListener("mousedown", outside, true);
    window.removeEventListener("resize", hide);
    window.removeEventListener("scroll", onScroll, true);
    if (anchorEl) anchorEl.setAttribute("aria-expanded", "false");
    anchorEl = null;
  }

  function open(anchor, opts) {
    if (anchor.dataset.justClosed) {
      delete anchor.dataset.justClosed;
      return;
    }
    hide();
    anchorEl = anchor;
    anchor.setAttribute("aria-expanded", "true");

    box = document.createElement("div");
    box.className = "picker";
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-label", opts.title);
    const head = document.createElement("div");
    head.className = "picker-head";
    const title = document.createElement("span");
    title.className = "picker-title";
    title.textContent = opts.title;
    const search = document.createElement("input");
    search.type = "search";
    search.className = "picker-search";
    search.placeholder = "Search";
    search.autocomplete = "off";
    search.setAttribute("aria-label", "Search " + opts.title);
    head.append(title, search);
    const pick = (value) => {
      const anchorNow = anchorEl;
      hide();
      opts.onPick(value);
      if (anchorNow && anchorNow.isConnected) anchorNow.focus({ preventScroll: true });
    };
    if (opts.none && opts.selected !== opts.none.value) {
      const none = document.createElement("button");
      none.type = "button";
      none.className = "link-btn";
      none.textContent = opts.none.label;
      none.onclick = () => pick(opts.none.value);
      head.appendChild(none);
    }
    const body = document.createElement("div");
    body.className = "picker-body";
    box.append(head, body);
    document.body.appendChild(box);

    let tiles = [];
    let active = 0;
    const paint = () => {
      tiles.forEach((t, i) => t.el.classList.toggle("active", i === active));
      if (tiles[active]) tiles[active].el.scrollIntoView({ block: "nearest" });
    };
    const render = () => {
      const needle = search.value.trim().toLowerCase();
      body.innerHTML = "";
      tiles = [];
      for (const group of opts.groups) {
        const entries = group.entries.filter(
          (e) => !needle || e.label.toLowerCase().includes(needle) || group.label.toLowerCase().includes(needle)
        );
        if (!entries.length) continue;
        const label = document.createElement("div");
        label.className = "picker-group";
        label.textContent = group.label;
        if (group.colour) label.style.color = group.colour;
        const grid = document.createElement("div");
        grid.className = "picker-grid";
        for (const entry of entries) {
          const tile = document.createElement("button");
          tile.type = "button";
          tile.className = "picker-tile";
          if (entry.value === opts.selected) tile.classList.add("selected");
          const art = tileArt("picker-art", entry);
          if (entry.colour) art.style.borderColor = entry.colour;
          const name = document.createElement("span");
          name.className = "picker-name";
          name.textContent = entry.label;
          tile.append(art, name);
          tile.onclick = () => pick(entry.value);
          const index = tiles.length;
          tile.onmouseenter = () => {
            active = index;
            tiles.forEach((t, i) => t.el.classList.toggle("active", i === active));
          };
          // cards: "team" shows a team trait's team-wide half (the Team Traits + Add picker)
          if (!(opts.cards && attachCard(tile, entry.value, () => null, null, opts.cards === "team"))) tile.title = entry.label;
          tiles.push({ el: tile, value: entry.value });
          grid.appendChild(tile);
        }
        body.append(label, grid);
      }
      if (!tiles.length) {
        const empty = document.createElement("div");
        empty.className = "picker-empty";
        empty.textContent = "No match";
        body.appendChild(empty);
      }
      active = needle ? 0 : Math.max(0, tiles.findIndex((t) => t.value === opts.selected));
      paint();
    };

    // Up and down go to the tile nearest above or below, so the arrows follow
    // the grid however many tiles each row holds.
    const move = (key) => {
      if (!tiles.length) return;
      if (key === "ArrowLeft") active = Math.max(0, active - 1);
      else if (key === "ArrowRight") active = Math.min(tiles.length - 1, active + 1);
      else {
        const here = tiles[active].el.getBoundingClientRect();
        const down = key === "ArrowDown";
        const rows = tiles
          .map((t, i) => ({ i, r: t.el.getBoundingClientRect() }))
          .filter((c) => (down ? c.r.top > here.top + 4 : c.r.top < here.top - 4));
        if (!rows.length) return;
        const top = down ? Math.min(...rows.map((c) => c.r.top)) : Math.max(...rows.map((c) => c.r.top));
        const x = here.left + here.width / 2;
        const next = rows
          .filter((c) => Math.abs(c.r.top - top) < 4)
          .reduce((a, c) =>
            Math.abs(c.r.left + c.r.width / 2 - x) < Math.abs(a.r.left + a.r.width / 2 - x) ? c : a
          );
        active = next.i;
      }
      paint();
    };

    search.oninput = render;
    search.onkeydown = (event) => {
      if (event.key.startsWith("Arrow")) {
        event.preventDefault();
        move(event.key);
      } else if (event.key === "Enter") {
        event.preventDefault();
        if (tiles[active]) pick(tiles[active].value);
      } else if (event.key === "Escape") {
        event.stopPropagation();
        const anchorNow = anchorEl;
        hide();
        if (anchorNow) anchorNow.focus({ preventScroll: true });
      } else if (event.key === "Tab") {
        hide();
      }
    };

    // Below the control, or above it when there is more room there; never
    // wider or taller than the window, and the body scrolls itself.
    const r = anchor.getBoundingClientRect();
    const width = Math.min(opts.width || 600, window.innerWidth - 16);
    box.style.width = width + "px";
    box.style.left = Math.min(Math.max(8, r.left), window.innerWidth - width - 8) + "px";
    const below = window.innerHeight - r.bottom - 14;
    const above = r.top - 14;
    const flip = below < 360 && above > below;
    box.style.maxHeight = Math.max(220, flip ? above : below) + "px";
    if (flip) box.style.bottom = window.innerHeight - r.top + 6 + "px";
    else box.style.top = r.bottom + 6 + "px";

    render();
    search.focus({ preventScroll: true });
    document.addEventListener("mousedown", outside, true);
    window.addEventListener("resize", hide);
    window.addEventListener("scroll", onScroll, true);
  }

  return { open, hide };
})();

// An item slot's tile: the item's art and name, or an empty slot.
function drawItemTile(tile, clear, cls) {
  const item = state.catalog.sidebarItems.find((i) => i.cls === cls);
  const empty = !item || cls === "NoItem";
  tile.innerHTML = "";
  tile.classList.toggle("empty", empty);
  clear.hidden = empty;
  const art = empty ? document.createElement("span") : tileArt("slot-art", { icon: state.icons.get(cls), label: item.name, frame: itemFrame(cls) });
  if (empty) {
    art.className = "slot-art slot-plus";
    art.textContent = "+";
  }
  const name = document.createElement("span");
  name.className = "slot-name";
  name.textContent = empty ? "Empty" : item.name;
  tile.setAttribute("aria-label", empty ? "Choose an item" : item.name + ", click to change");
  tile.append(art, name);
}

// A champion with forms (Seraphine) is one menu entry; its forms are the base class and every class naming it in
// variantOf. Returns [base, ...forms] (just [champ] for everyone else).
function champForms(name) {
  const meta = champMeta(name);
  if (!meta) return [];
  const base = meta.variantOf ? champMeta(meta.variantOf) : meta;
  return [base, ...state.catalog.champions.filter((c) => c.variantOf === base.name)];
}

// The bar's champion: portrait in its cost colour and name (the base name when a form switch is beside it).
function renderChampPick() {
  const meta = champMeta($("champ").value);
  if (!meta) return;
  const forms = champForms(meta.name);
  $("headerChamp").textContent = forms.length > 1 ? forms[0].label || forms[0].name : meta.label || meta.name;
  const icon = state.icons.get(meta.name);
  $("champIcon").hidden = !icon;
  if (icon) $("champIcon").src = icon;
  $("champPick").style.setProperty("--cost", costColour(meta.cost));
  renderChampModes(meta, forms);
}

// Which form the champion is in (Seraphine: Indie | Rising Star | Superstar), chosen after picking her. A switch
// keeps the items, buffs and level: only the unit changes.
function renderChampModes(meta, forms) {
  const box = $("champModes");
  box.innerHTML = "";
  box.hidden = forms.length < 2;
  for (const form of forms) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.setAttribute("role", "radio");
    btn.textContent = form.mode || form.label || form.name;
    const on = form.name === meta.name;
    btn.classList.toggle("active", on);
    btn.setAttribute("aria-checked", String(on));
    btn.onclick = () => {
      if (on) return;
      $("champ").value = form.name;
      selectChampion(form.name, { keepLevel: true, keepConfig: true });
    };
    box.appendChild(btn);
  }
}

// Star level: one button per level the champion has, over the hidden select.
function renderStars() {
  const meta = champMeta();
  const box = $("levelStars");
  box.innerHTML = "";
  if (!meta) return;
  for (const level of meta.levels) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "star-btn";
    btn.textContent = "★".repeat(level);
    btn.title = level + " star";
    btn.setAttribute("role", "radio");
    const on = level === state.cfg.level;
    btn.setAttribute("aria-checked", String(on));
    btn.classList.toggle("active", on);
    btn.onclick = () => pickInto($("level"), level);
    box.appendChild(btn);
  }
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

// The Targets buttons (1 .. max) over the hidden range input, which stays the value: a click sets it and fires its
// change, so everything else (bindSlider, the browser checks) sees one control.
function renderTargetsSeg() {
  const range = $("layoutTargets");
  const seg = $("targetsSeg");
  const max = Number(range.max);
  if (seg.children.length !== max) {
    seg.innerHTML = "";
    for (let n = 1; n <= max; n++) {
      const b = document.createElement("button");
      b.type = "button";
      b.setAttribute("role", "radio");
      b.textContent = n;
      b.onclick = () => {
        if (range.value === String(n)) return;
        range.value = n;
        range.dispatchEvent(new Event("change"));
      };
      seg.appendChild(b);
    }
  }
  [...seg.children].forEach((b, i) => b.setAttribute("aria-checked", String(i + 1 === Number(range.value))));
}

async function selectChampion(name, { keepLevel, keepConfig = false }) {
  const meta = champMeta(name);
  state.cfg.champ = name;
  if ($("champ").value !== name) $("champ").value = name;  // the bar shows what runs (boot picks a default)
  renderChampPick();
  $("targetsRow").hidden = !meta.area;
  // its own cap, shape and default (Jhin: a line of 3 behind the target; Kayn: a line of 2, 1 by default): a newly
  // picked champion starts at its default, and a value over the cap comes down to it
  const range = $("layoutTargets");
  range.max = meta.targetsMax || state.catalog.defaults.layout.max;
  if (!keepConfig) state.cfg.layout.targets = meta.targetsDefault || state.catalog.defaults.layout.targets;
  if (state.cfg.layout.targets > Number(range.max)) state.cfg.layout.targets = Number(range.max);
  range.value = state.cfg.layout.targets;
  $("layoutTargetsValue").textContent = range.value;
  $("targetsRow").title =
    meta.targetsShape === "line"
      ? "The target and the enemies standing in a line behind it, which the champion's piercing shots pass through."
      : "The target and the enemies next to it, which the champion's area damage hits.";
  renderTargetsSeg();

  const levelSel = $("level");
  levelSel.innerHTML = "";
  for (const l of meta.levels) levelSel.add(new Option(l, l));
  if (keepLevel && meta.levels.includes(state.cfg.level)) {
    levelSel.value = state.cfg.level;
  } else {
    state.cfg.level = meta.levels[0];
    levelSel.value = state.cfg.level;
  }
  renderStars();

  // Minimal config: the default traits must describe the champion itself,
  // not whatever items/buffs are still configured.
  const probe = cfgForSlice(state.slice);
  probe.items = ["NoItem", "NoItem", "NoItem"];
  probe.buffs = [];
  const info = await rpc("champInfo", JSON.stringify(probe));

  // Buff bar: the champion's own traits at their first listed level. No empty
  // rows: + Add opens the picker. Skipped when only the star level moved --
  // see the level handler.
  // the champion's own traits: x in the buff bar sets one to 0 rather than removing it
  state.ownTraits = new Set(info.defaultTraits.classNames);
  if (!keepConfig) {
    const defaults = info.defaultTraits.classNames.filter((c) => state.buffMeta.has(c));
    state.cfg.buffs = defaults.map(defaultBuffTuple);
    renderBuffRows();
    ensureDefaultTeamTraits();
  }

  onConfigChanged();
}

function defaultBuffTuple(cls) {
  const meta = state.buffMeta.get(cls);
  const params = meta.extra ? meta.extra.Default : 0;
  return [cls, alwaysOn(cls) ? onLevel(meta) : meta.levels[0], params];
}

// The champion's own unique trait (Composer for Malzahar) is always active: its one level, never 0 (owner,
// 2026-11-19). Anywhere else (Team Traits, another champion's bar) it can still be off.
function alwaysOn(cls) {
  const meta = state.buffMeta.get(cls);
  return Boolean(meta && meta.unique && state.ownTraits.has(cls));
}

function onLevel(meta) {
  return meta.levels.find((l) => l > 0) ?? meta.levels[0];
}

// An emblem makes its holder a member of the trait, so picking one puts the
// trait in the buff bar at its lowest active level. A row that already holds
// the trait keeps its level unless that level is 0 (off). Removing the emblem
// leaves the row alone: the trait may be in the bar for its own sake.
function addEmblemTrait(itemCls) {
  const item = state.catalog.sidebarItems.find((i) => i.cls === itemCls);
  const trait = item && item.trait;
  const meta = trait && state.buffMeta.get(trait);
  if (!meta) return;
  const onLevel = meta.levels.find((l) => l > 0);
  if (onLevel === undefined) return;
  // A 0/1 "Is X" flag: the emblem is the membership.
  const isFlag =
    meta.extra && !meta.extra.Options && meta.extra.Min === 0 && meta.extra.Max === 1;

  const buffs = state.cfg.buffs;
  const existing = buffs.find(([cls]) => cls === trait);
  if (existing) {
    if (existing[1] === 0) existing[1] = onLevel;
    if (isFlag) existing[2] = 1;
  } else {
    const tuple = [trait, onLevel, meta.extra ? meta.extra.Default : 0];
    const free = buffs.findIndex(([cls]) => cls === "NoBuff");
    if (free >= 0) {
      buffs[free] = tuple;
    } else if (buffs.length < state.catalog.defaults.numBuffs.max) {
      buffs.push(tuple);
    } else {
      return;
    }
  }
  renderBuffRows();
}

// One row per buff: its tile (opens the picker to swap it), its level, a
// remove button, and under them its parameter or tick boxes when it has one.
// The buff's own <select> stays in the row, hidden, before the level select.
function renderBuffRows() {
  const container = $("buffRows");
  container.innerHTML = "";
  $("addBuff").hidden = state.cfg.buffs.length >= state.catalog.defaults.numBuffs.max;
  if (!state.cfg.buffs.length) {
    const empty = document.createElement("p");
    empty.className = "empty-note";
    empty.textContent = "No traits or augments. + Add picks one.";
    container.appendChild(empty);
  }
  state.cfg.buffs.forEach((tuple, i) => {
    const row = document.createElement("div");
    row.className = "buff-row";

    const buffSel = document.createElement("select");
    buffSel.hidden = true;
    for (const b of state.catalog.buffs) buffSel.add(new Option(b.name, b.cls));
    buffSel.value = tuple[0];

    const tile = document.createElement("button");
    tile.type = "button";
    tile.className = "buff-tile";
    tile.setAttribute("aria-haspopup", "dialog");

    const levelSel = document.createElement("select");
    levelSel.className = "buff-level";
    levelSel.title = "Level (units of the trait on the board)";
    levelSel.setAttribute("aria-label", "Level");

    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "row-remove";
    remove.innerHTML = "&times;";
    remove.title = "Remove";
    remove.setAttribute("aria-label", "Remove buff");

    const paramInput = document.createElement("input");
    paramInput.type = "number";
    // A parameter whose values are names, not a count (Illbeats' mix).
    // The stored value is still the index, so nothing downstream changes --
    // only what the row shows for it.
    const paramSelect = document.createElement("select");
    // A parameter that is a set of yes/no facts (Heartsteel: which members are
    // fielded, and whether this unit is a Bias). Stored as one number, bit i
    // for Flags[i], so the tuple keeps its shape.
    const flagBox = document.createElement("div");
    flagBox.className = "param-flags";
    let flagBits = 0;

    const paramCol = document.createElement("label");
    paramCol.className = "buff-param";
    const paramCaption = document.createElement("span");
    paramCaption.className = "col-label";
    paramCol.append(paramCaption, paramInput, paramSelect);

    const drawTile = () => {
      const meta = state.buffMeta.get(buffSel.value);
      tile.innerHTML = "";
      const isTrait = meta && meta.kind === "Trait";
      tile.appendChild(
        tileArt("buff-art", {
          icon: state.icons.get(buffSel.value),
          badge: isTrait ? () => traitBadge(buffSel.value, Number(levelSel.value) || meta.levels.find((l) => l > 0)) : null,
          label: meta ? meta.name : buffSel.value,
        })
      );
      const name = document.createElement("span");
      name.className = "buff-name";
      name.textContent = meta ? meta.name : buffSel.value;
      tile.appendChild(name);
    };

    const paramValue = (meta) => {
      if (!meta.extra) return 0;
      if (meta.extra.Flags) return flagBits;
      return Number(meta.extra.Options ? paramSelect.value : paramInput.value);
    };

    const drawFlags = (meta) => {
      flagBox.innerHTML = "";
      const caption = document.createElement("span");
      caption.className = "col-label";
      caption.textContent = meta.extra.Title;
      flagBox.appendChild(caption);
      meta.extra.Flags.forEach((name, bit) => {
        const label = document.createElement("label");
        const check = document.createElement("input");
        check.type = "checkbox";
        check.checked = Boolean((flagBits >> bit) & 1);
        check.onchange = () => {
          flagBits ^= 1 << bit;
          syncRow(false);
          onConfigChanged();
        };
        label.appendChild(check);
        label.appendChild(document.createTextNode(name));
        flagBox.appendChild(label);
      });
    };

    const syncParamColumn = (meta) => {
      const flags = Boolean(meta.extra && meta.extra.Flags);
      flagBox.hidden = !flags;
      if (flags) drawFlags(meta);
      paramCol.hidden = !(meta.extra && !flags);
      paramCaption.textContent = meta.extra ? meta.extra.Title : "";
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

    const fillLevels = (meta) => {
      levelSel.innerHTML = "";
      // the champion's own unique trait: only its active level (alwaysOn)
      const levels = alwaysOn(buffSel.value) ? [onLevel(meta)] : meta.levels;
      for (const l of levels) levelSel.add(new Option(String(l), String(l)));
      // a buff with one level (most augments, an own unique trait) has nothing to choose
      levelSel.style.visibility = levels.length > 1 ? "visible" : "hidden";
    };

    const syncRow = (resetToDefaults) => {
      const meta = state.buffMeta.get(buffSel.value);
      // Rebuilding the options resets the browser's selection, so hold on to
      // it -- otherwise changing the *level* snaps back to the first entry
      // before the config reads it.
      const previousLevel = levelSel.value;
      fillLevels(meta);
      if (resetToDefaults) {
        levelSel.value = alwaysOn(buffSel.value) ? onLevel(meta) : meta.levels[0];
        paramInput.value = meta.extra ? meta.extra.Default : 0;
        paramSelect.value = String(meta.extra ? meta.extra.Default : 0);
        flagBits = meta.extra ? meta.extra.Default : 0;
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
      state.cfg.buffs[i] = [buffSel.value, Number(levelSel.value), paramValue(meta)];
      drawTile();
    };

    buffSel.onchange = () => {
      syncRow(true);
      drawRemove();
      onConfigChanged();
    };
    levelSel.onchange = () => {
      syncRow(false);
      drawRemove();
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
    selectZeroOnFocus(paramInput);
    tile.onclick = () =>
      Picker.open(tile, {
        title: "Buff",
        // the other rows' buffs are left out: one class twice would be set twice
        groups: buffGroups().map((g) => ({
          ...g,
          entries: g.entries.filter(
            (e) => e.value === buffSel.value || !state.cfg.buffs.some(([cls]) => cls === e.value)
          ),
        })),
        selected: buffSel.value,
        cards: true,
        onPick: (value) => pickInto(buffSel, value),
      });
    // The champion's own traits stay in the bar: x turns one to 0 (and hides once it is), as removing it would only
    // hide a trait the champion has (owner, 2026-11-19). Anything else is removed.
    const ownTrait = () => state.ownTraits.has(buffSel.value) && [...levelSel.options].some((o) => o.value === "0");
    const drawRemove = () => {
      const own = ownTrait();
      // an own unique trait has neither a 0 to go to nor a way out of the bar
      remove.style.visibility = (own && levelSel.value === "0") || alwaysOn(buffSel.value) ? "hidden" : "";
      remove.title = own ? "Set to 0" : "Remove";
      remove.setAttribute("aria-label", own ? "Set this trait to 0" : "Remove buff");
    };
    remove.onclick = () => {
      if (ownTrait()) {
        levelSel.value = "0";
        syncRow(false);
        drawRemove();
      } else {
        state.cfg.buffs.splice(i, 1);
        renderBuffRows();
      }
      onConfigChanged();
    };
    attachCard(tile, () => buffSel.value, () => Number(levelSel.value), "Click to change");

    // Initial fill from the stored tuple.
    const meta = state.buffMeta.get(tuple[0]);
    fillLevels(meta);
    levelSel.value = String(tuple[1]);
    paramInput.value = tuple[2];
    flagBits = tuple[2];
    if (meta.extra) {
      paramInput.min = meta.extra.Min;
      paramInput.max = meta.extra.Max;
      paramInput.title = meta.extra.Title;
      paramSelect.title = meta.extra.Title;
    }
    syncParamColumn(meta);
    paramSelect.value = String(tuple[2]);
    drawTile();
    drawRemove();

    row.append(buffSel, tile, levelSel, remove, paramCol, flagBox);
    container.appendChild(row);
  });
}

// ---------------------------------------------------------------------------
// Team traits ("my team runs this, but this champion isn't one of them")
// ---------------------------------------------------------------------------

function renderTeamTraits() {
  // Team traits (owner, 2026-11-19: like the buff bar): only the ones added are rows; + Add picks another. A trait
  // in the buff bar is configured there with its own level and flag, so it is neither a row nor offered here.
  const container = $("teamTraits");
  const all = state.catalog.teamBuffs || [];
  for (const cls of [...state.teamBuffs.keys()]) {
    if (state.cfg.buffs.some(([c]) => c === cls)) state.teamBuffs.delete(cls);
  }
  const available = teamTraitChoices();
  $("addTeamTrait").hidden = !available.length;
  $("teamTraitsPanel").hidden = !all.length || (!available.length && !state.teamBuffs.size);
  container.innerHTML = "";
  if (!state.teamBuffs.size) {
    const note = document.createElement("p");
    note.className = "empty-note";
    note.textContent = "Traits your board runs that this champion isn't in. + Add picks one.";
    container.appendChild(note);
    return;
  }
  for (const [cls, picked] of state.teamBuffs) {
    const trait = all.find((t) => t.cls === cls);
    if (trait) container.appendChild(teamTraitRow(trait, picked));
  }
}

// Team Traits always starts with Heartsteel, nothing ticked (owner, 2026-11-19): the tick boxes are the panel's
// idea at its plainest. Put back on every champion change unless it is the champion's own trait.
const DEFAULT_TEAM_TRAITS = ["Heartsteel"];

function ensureDefaultTeamTraits() {
  for (const cls of DEFAULT_TEAM_TRAITS) {
    const trait = (state.catalog.teamBuffs || []).find((t) => t.cls === cls);
    if (trait && !state.teamBuffs.has(cls) && !state.cfg.buffs.some(([c]) => c === cls)) {
      state.teamBuffs.set(cls, { level: trait.onLevel, params: 0 });
    }
  }
}

// The team traits + Add can still offer: every one not added and not in the buff bar.
function teamTraitChoices() {
  return (state.catalog.teamBuffs || []).filter(
    (t) => !state.teamBuffs.has(t.cls) && !state.cfg.buffs.some(([c]) => c === t.cls)
  );
}

// A team trait added with + Add: on at its first breakpoint, its question at the default.
function addTeamTrait(trait) {
  // tick boxes start empty (Heartsteel: no member fielded yet); a choice or a count at its default
  const params = trait.options || trait.number ? trait.paramDefault : 0;
  state.teamBuffs.set(trait.cls, { level: trait.onLevel, params });
  onConfigChanged();
}

// One team trait's row: badge and name, its level where the team-wide half steps per breakpoint (Arcanist), x;
// under it whatever it asks: a named choice (Illbeats' mix), a count (Composer's instruments) or tick boxes
// (Heartsteel's fielded members).
function teamTraitRow(trait, picked) {
  const row = document.createElement("div");
  row.className = "buff-row team-row";
  const store = (level, params) => {
    state.teamBuffs.set(trait.cls, { level, params });
    onConfigChanged();
  };
  let { level, params } = picked;

  const tile = document.createElement("span");
  tile.className = "buff-tile team-tile";
  tile.appendChild(tileArt("buff-art", {
    icon: state.icons.get(trait.cls),
    badge: () => traitBadge(trait.cls, level || trait.onLevel),
    label: trait.name,
  }));
  const name = document.createElement("span");
  name.className = "buff-name";
  name.textContent = trait.name;
  tile.appendChild(name);
  attachCard(tile, () => trait.cls, () => level || trait.onLevel, null, true);

  // A non-member gets the same bonus at every breakpoint unless `scales`: then there is no level to ask.
  const levelSel = document.createElement("select");
  levelSel.className = "buff-level";
  levelSel.title = "Level (units of the trait on the board)";
  for (const l of trait.levels) levelSel.add(new Option(String(l), String(l)));
  levelSel.value = String(level);
  levelSel.style.visibility = trait.scales ? "visible" : "hidden";
  levelSel.onchange = () => store(Number(levelSel.value), params);

  const remove = document.createElement("button");
  remove.type = "button";
  remove.className = "row-remove";
  remove.innerHTML = "&times;";
  remove.title = "Remove";
  remove.setAttribute("aria-label", "Remove " + trait.name);
  remove.onclick = () => {
    state.teamBuffs.delete(trait.cls);
    onConfigChanged();
  };
  row.append(tile, levelSel, remove);

  if (trait.options || trait.number) {
    const line = document.createElement("label");
    line.className = "buff-param";
    const caption = document.createElement("span");
    caption.className = "col-label";
    caption.textContent = trait.paramTitle;
    line.appendChild(caption);
    if (trait.options) {
      const sel = document.createElement("select");
      trait.options.forEach((option, index) => sel.add(new Option(option, String(index))));
      sel.value = String(params);
      sel.onchange = () => store(level, Number(sel.value));
      line.appendChild(sel);
    } else {
      const box = document.createElement("input");
      box.type = "number";
      box.min = trait.number.min;
      if (trait.number.max != null) box.max = trait.number.max;
      box.value = params;
      selectZeroOnFocus(box);
      box.onchange = () => store(level, clampInput(box));
      line.appendChild(box);
    }
    row.appendChild(line);
  }
  if (trait.flags) {
    const box = document.createElement("div");
    box.className = "param-flags";
    box.title = trait.paramTitle;
    trait.flags.forEach((flag, bit) => {
      const item = document.createElement("label");
      const tick = document.createElement("input");
      tick.type = "checkbox";
      tick.checked = Boolean((params >> bit) & 1);
      tick.onchange = () => store(level, params ^ (1 << bit));
      item.append(tick, document.createTextNode(flag));
      box.appendChild(item);
    });
    row.appendChild(box);
  }
  return row;
}

// ---------------------------------------------------------------------------
// Slice options & the run loop
// ---------------------------------------------------------------------------

// Does the setup's damage depend on the top bar's Takedowns? A champion that scales with them (catalog `takedowns`:
// Viego's swords) or a Cappa Juice in a slot (owner, 2026-11-19): the box is highlighted and the Takedowns slice shown.
function usesTakedowns() {
  const meta = champMeta(state.cfg.champ);
  return Boolean((meta && meta.takedowns) || state.cfg.items.includes("CappaJuice"));
}

function renderTakedownsField() {
  const on = usesTakedowns();
  $("takedownsField").classList.toggle("hot", on);
  $("takedownsField").title = on
    ? "Takedowns this game: this setup's damage depends on them (Viego: +1 sword per 8; Cappa Juice: a Hat each). " +
      "The Takedowns tab compares other counts."
    : "Takedowns this game (Cappa Juice's Hats)";
}

function sliceOptions() {
  // With a full item bar only the non-item slices remain; with nothing in Team Traits, no Team Traits slice; the
  // Takedowns slice only when the setup reads them.
  const itemCount = state.cfg.items.filter((i) => i !== "NoItem").length;
  const options = itemCount >= 3 ? ["Trait", "Team Traits", "Augment/Buff", "Takedowns"] : state.catalog.slices.slice();
  return options.filter((o) => (o !== "Team Traits" || state.teamBuffs.size) && (o !== "Takedowns" || usesTakedowns()));
}

function onConfigChanged() {
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
  renderTakedownsField();
  renderAskBonus();
  updateStatsPanel(gen);

  const ranCfg = cfgForSlice(state.slice);
  const payload = await runSlice(state.slice, gen, true);
  if (gen !== state.gen || !payload) return;
  state.current = payload;
  state.currentCfg = ranCfg;
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
  if (state.cache.has(key)) {
    // A cache hit still replaces whatever the last run left on screen -- an
    // old failure must not sit above results that came back fine.
    if (showStatus) setRunStatus(null);
    return state.cache.get(key);
  }
  if (showStatus) setRunStatus("Simulating " + sliceName + "…");
  try {
    const payload = await rpc("run", key);
    if (state.cache.size > 60) state.cache.clear();
    state.cache.set(key, payload);
    if (showStatus && gen === state.gen) setRunStatus(null);
    return payload;
  } catch (err) {
    // Cleared only on success: this used to clear in a finally, which wiped
    // the message the instant it was set, so a run that threw just left the
    // page frozen on its previous results with nothing saying why. The
    // worker hands over a PythonError's JS stack: the Python traceback, then
    // the JS frames ("    at ..."). The last line before those frames is the
    // exception itself, which is what fits on the page.
    console.error("Simulation failed (" + sliceName + "):\n" + err.message);
    const lines = err.message.split("\n").filter((l) => l.trim() && !/^\s+at /.test(l));
    if (showStatus && gen === state.gen) {
      setRunStatus("Simulation failed: " + (lines[lines.length - 1] || "unknown error"));
    }
    return null;
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
  // The enemy numbers in the bar are live inputs; only the champion half and
  // the caption are redrawn.
  renderChampPick();
  $("footerCaption").textContent =
    "Simulation computed in your browser" +
    (bootMs != null ? " · engine booted in " + (bootMs / 1000).toFixed(1) + "s" : "");
}

// The stats grid: two cells to a row, each a stat's name, its value as the
// fight starts (the formula on hover) and, where it takes one, the bonus box.
const STAT_CELLS = [
  { id: "ad", label: "AD", bonus: "ad" },
  { id: "as", label: "AS", bonus: "as" },
  { id: "ap", label: "AP", bonus: "ap" },
  { id: "crit", label: "Crit", bonus: "crit" },
  { id: "dmgamp", label: "Amp", bonus: "dmgamp" },
  { id: "critdmg", label: "Crit dmg", bonus: "critdmg" },
  { id: "manaregen", label: "Mana regen", bonus: "manaregen" },
  { id: "mpa", label: "Mana/atk", bonus: "mpa" },
  { id: "mana", label: "Mana" },
  { id: "cast", label: "Cast" },
  { id: "role", label: "Role" },
  { id: "spellcrit", label: "Spell crit" },
];

function buildStatsPanel() {
  const panel = $("statsPanel");
  if (panel.dataset.built) return;
  panel.dataset.built = "1";
  panel.innerHTML = "";
  for (const cell of STAT_CELLS) {
    const el = document.createElement("div");
    el.className = "stat-cell";
    if (cell.bonus) el.dataset.bonus = cell.bonus;
    const label = document.createElement("span");
    label.className = "stat-label";
    label.textContent = cell.label;
    const value = document.createElement("span");
    value.className = "stat-val";
    value.dataset.stat = cell.id;
    el.append(label, value);
    if (cell.bonus) {
      const field = BONUS_FIELDS[cell.bonus];
      const input = document.createElement("input");
      input.type = "number";
      input.min = field.min;
      input.max = field.max;
      input.value = state.cfg.bonus[cell.bonus] ?? 0;
      input.title = field.label;
      input.setAttribute("aria-label", field.label);
      input.onchange = () => {
        state.cfg.bonus[cell.bonus] = clampInput(input);
        onConfigChanged();
      };
      selectZeroOnFocus(input);
      el.appendChild(input);
    } else {
      el.classList.add("no-bonus");
    }
    panel.appendChild(el);
  }
}

// A champion's Stats boxes the user should fill in (catalog askBonus: Neeko's AP from kills) are highlighted, the
// reason on hover (owner, 2026-11-19).
function renderAskBonus() {
  const meta = champMeta(state.cfg.champ);
  const ask = (meta && meta.askBonus) || {};
  for (const el of document.querySelectorAll("#statsPanel .stat-cell[data-bonus]")) {
    const why = ask[el.dataset.bonus];
    el.classList.toggle("ask", Boolean(why));
    const input = el.querySelector("input");
    input.title = why ? `Add ${why}` : BONUS_FIELDS[el.dataset.bonus].label;
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
  const P = (v) => `${Math.round(v * 1000) / 10}%`; // 0.25 -> 25%, 1.633 -> 163.3%
  const Pts = (v) => `${Math.round(v * 10) / 10}%`; // already in points: 20 -> 20%

  // [value, how it is made] per cell; the formula is the hover text.
  const ad = r2(s.atk.stat * s.bonusAd.stat);
  const excessCrit = Math.max(0, s.crit.stat - 1);
  const critRatio = s.excessCritRatio ?? 0.5;
  const critDmg = s.critDmg.stat + excessCrit * critRatio;
  const values = {
    ad: [ad, s.bonusAd.addMultiplier === 1
      ? `AD ${ad} = ${s.atk.base} × ${r4(s.bonusAd.stat)} AD`
      : `AD ${ad} = ${s.atk.base} × (1 + ${s.bonusAd.addMultiplier} × ${r4(s.bonusAd.add / 100)} AD)`],
    // AP, crit, crit damage and amp read as percentages, the way the game shows them (owner, 2026-11-19); amp is
    // the bonus over 1 (a multiplier of 1.1 is 10%)
    // the total is a fraction (1.2), base and bonus already points of 100 (sim_entry._panel "multiplier": 100, 20)
    ap: [P(s.ap.stat), s.ap.addMultiplier === 1
      ? `AP ${P(s.ap.stat)} = ${Pts(s.ap.base)} + ${Pts(s.ap.add)}`
      : `AP ${P(s.ap.stat)} = ${Pts(s.ap.base)} + ${s.ap.addMultiplier} × ${Pts(s.ap.add)}`],
    dmgamp: [P(s.dmgAmp.stat - 1), `Damage amp ${P(s.dmgAmp.stat - 1)} = ${P(s.dmgAmp.base - 1)} + ${P(s.dmgAmp.add)}`],
    manaregen: [r2(s.manaRegen.stat), `Mana regen ${r2(s.manaRegen.stat)} = ${s.manaRegen.base} + ${r2(s.manaRegen.add)}`],
    as: [r3(s.aspd.stat), `AS ${r3(s.aspd.stat)} = ${s.aspd.base} × (1 + ${Pts(s.aspd.add)})`], // add: percent (_panel "aspd")
    // Crit chance stops at 1; the excess is crit damage instead, at the build's ratio (champion.critDamage), so the
    // panel shows what a hit uses rather than the raw sum.
    crit: [P(Math.min(1, s.crit.stat)), s.crit.stat > 1
      ? `Crit chance 100% (capped): ${P(s.crit.stat)} = ${P(s.crit.base)} + ${P(s.crit.add)}; the ${P(excessCrit)} over 100% is crit damage`
      : `Crit chance ${P(s.crit.stat)} = ${P(s.crit.base)} + ${P(s.crit.add)}`],
    critdmg: [P(critDmg), excessCrit > 0
      ? `Crit damage ${P(critDmg)} = ${P(s.critDmg.base)} + ${P(s.critDmg.add)} + ${P(excessCrit)} excess crit × ${critRatio}`
      : `Crit damage ${P(critDmg)} = ${P(s.critDmg.base)} + ${P(s.critDmg.add)}`],
    mpa: [r2(s.manaPerAttack.stat), `Mana per attack ${r2(s.manaPerAttack.stat)} = ${s.manaPerAttack.base} + ${r2(s.manaPerAttack.add)}`],
    mana: [`${r2(s.curMana)} / ${r2(s.fullMana)}`, "Starting mana / mana to cast"],
    cast: [`${r3(s.castTime)} s`, "Cast time"],
    role: [s.role, "Role"],
    spellcrit: [s.canSpellCrit ? "yes" : "no", "Whether the spell can crit"],
  };

  buildStatsPanel();
  renderAskBonus();
  // Only the values are rewritten on refresh: the inputs are long-lived, and
  // replacing them would drop whatever is being typed (and the caret).
  for (const el of document.querySelectorAll("#statsPanel .stat-val")) {
    const [value, formula] = values[el.dataset.stat];
    el.textContent = value;
    el.parentElement.title = formula;
  }

  const notes = $("champNotes");
  notes.hidden = !s.notes;
  notes.textContent = s.notes || "";
}

// ---------------------------------------------------------------------------
// Rendering: results table
// ---------------------------------------------------------------------------

function currentSelection() {
  if (!state.selections.has(state.slice)) state.selections.set(state.slice, new Map());
  return state.selections.get(state.slice);
}

// What the chart draws (idx -> colour slot): the rows clicked, or NoItem alone while none is, so the chart always
// has the baseline to look at; the first row plotted replaces it (owner, 2026-11-19). NoItem clicked like any row
// stays with the others.
function plottedSlots() {
  const selection = currentSelection();
  if (selection.size || !state.current) return selection;
  const base = state.current.rows.find((r) => r.extraCls === "NoItem");
  return base ? new Map([[base.idx, BASE_SLOT]]) : selection;
}

// NoItem's line has its own colour, outside the palette (owner, 2026-11-19): the first row plotted over the default
// NoItem line must not take on the colour NoItem just had, so the swap reads as a different line.
const BASE_SLOT = -1;
const BASE_COLOR = "#c3c7d4";

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
  const row = state.current && state.current.rows.find((r) => r.idx === idx);
  if (row && row.extraCls === "NoItem") {
    selection.set(idx, BASE_SLOT);
    return;
  }
  const taken = new Set(selection.values());
  let slot = 0;
  while (taken.has(slot)) slot++;
  selection.set(idx, slot);
}

function seriesColor(slot) {
  return slot === BASE_SLOT ? BASE_COLOR : COLORS[slot % COLORS.length];
}

function renderResults() {
  const payload = state.current;
  if (!payload) return;
  const selection = plottedSlots(); // what the chart draws, NoItem included while it stands in alone

  // "Display DPS" swaps the DPS columns for the ratio columns. Each column is the average over fights ending in
  // its window (sim_entry.DPS_WINDOWS).
  const headline = DPS_WINDOWS.find((w) => w.key === HEADLINE) || DPS_WINDOWS[DPS_WINDOWS.length - 1];
  // The ratio is named for what it is (this row's DPS over NoItem's, in that window), not "Extra DPS": it is not in
  // DPS units, and 1.93 means 93% more. Each header's hover says what the column holds.
  const ratioCol = (w) => ({
    label: "DPS ÷ Base (" + w.label + ")",
    title: `This row's DPS divided by the base setup's (the NoItem row: nothing added), averaged over fights ending ${w.label} (1.50 = 50% more damage)`,
    get: (row) => row.ratio[w.key],
  });
  const dpsCols = state.displayDps
    ? DPS_WINDOWS.map(ratioCol)
    : DPS_WINDOWS.map((w) => ({
        label: "DPS " + w.label,
        title: `Average damage per second over fights ending ${w.label}`,
        get: (row) => row.dps[w.key],
      })).concat([ratioCol(headline)]);

  // Every column is described the same way, so the header handler is
  // written once.
  const labelCols = [
    {
      label: "Extra",
      text: true,
      get: (row) => row.extra,
      render: (cell, row) => {
        // Decorative (alt ""): the name sits right beside it, so a screen
        // reader announcing the file too would only repeat.
        const art = rowArt(row);
        if (art) cell.appendChild(art);
        if (row.input) rowNameWithInput(cell, row);
        else cell.appendChild(document.createTextNode(row.extra));
        const add = rowAddButton(row);
        if (add) cell.appendChild(add);
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
  // sort returns to the order sim_entry delivered (the headline window's ratio, descending).
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
  const viewed = vizRow();
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
    const hint = slot !== undefined ? "Click to remove from the chart" : "Click to plot";
    // the card carries the hint where there is one (a native title would pop up over it)
    if (!attachCard(tr, row.extraCls, () => row.extraLevel, hint, state.slice === "Team Traits")) tr.title = hint;
    if (row === viewed) tr.classList.add("viewing");
    const toggle = () => {
      togglePlotted(row.idx);
      if (currentSelection().has(row.idx)) {
        // the fight viewer follows the row just plotted
        state.vizRow = { slice: state.slice, extra: row.extra };
      } else if (row === vizRow()) {
        // un-plotting the row on view: show the last plotted row left (NoItem when none is)
        const left = selectedRows();
        state.vizRow = left.length ? { slice: state.slice, extra: left[left.length - 1].row.extra } : null;
      }
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
  updateViz();
}

// Adding a table row's extra to the setup (owner, 2026-11-19): an item goes in the first empty slot; a trait or
// augment already in the buff bar is set to the row's level and parameter (a trait row is one breakpoint); a team
// trait is set in the Team Traits panel; anything else joins the buff bar. Returns what a click would do, so the
// button can say it (and be off when it can't: slots or bar full, already set).
function rowAddPlan(row) {
  const cls = row.extraCls;
  if (!cls || cls === "NoItem") return null;
  if (cls === "TakedownCount") {  // a Takedowns row: set the top bar's Takedowns to its count
    const n = row.extraParams;
    if (state.cfg.takedowns === n) return { disabled: true, title: `Takedowns is already ${n}` };
    return {
      title: `Set Takedowns to ${n}`,
      run: () => {
        $("takedowns").value = n;
        $("takedowns").onchange();
      },
    };
  }
  if (state.itemKinds.has(cls)) {
    const slot = state.cfg.items.findIndex((i) => i === "NoItem");
    return slot < 0
      ? { disabled: true, title: "The item slots are full" }
      : { title: `Add ${row.extra} to item slot ${slot + 1}`, run: () => pickInto(document.querySelectorAll(".item-slot select")[slot], cls) };
  }
  const meta = state.buffMeta.get(cls);
  if (!meta) return null;
  const level = row.extraLevel ?? meta.levels.find((l) => l > 0) ?? meta.levels[0];
  const params = row.extraParams ?? (meta.extra ? meta.extra.Default : 0);
  const name = meta.name;
  const inBar = state.cfg.buffs.findIndex(([c]) => c === cls);
  if (inBar >= 0) {
    const [, curLevel, curParams] = state.cfg.buffs[inBar];
    if (curLevel === level && curParams === params) return { disabled: true, title: `${name} is already set to this` };
    return {
      title: `Set ${row.extra} in the buff bar`,
      run: () => {
        state.cfg.buffs[inBar] = [cls, level, params];
        renderBuffRows();
        onConfigChanged();
      },
    };
  }
  const team = (state.catalog.teamBuffs || []).some((t) => t.cls === cls);
  if (team) {
    const cur = state.teamBuffs.get(cls);
    if (cur && cur.level === level && cur.params === params) return { disabled: true, title: `${name} is already set to this` };
    return {
      title: `Set ${row.extra} in Team Traits`,
      run: () => {
        state.teamBuffs.set(cls, { level, params });
        renderTeamTraits();
        onConfigChanged();
      },
    };
  }
  if (state.cfg.buffs.length >= state.catalog.defaults.numBuffs.max) return { disabled: true, title: "The buff bar is full" };
  return {
    title: `Add ${row.extra} to the buff bar`,
    run: () => {
      state.cfg.buffs.push([cls, level, params]);
      renderBuffRows();
      onConfigChanged();
    },
  };
}

// A row whose result hangs on a number of its own reads "Hold the Line ([7] units)", the number a box: typing in it
// reruns the slice with that number for that row (cfg.rowInputs; sim_entry._row_input) (owner, 2026-11-19).
function rowNameWithInput(cell, row) {
  const { value, min, max, template, title } = row.input;
  const [before, after] = template.split("{}");
  const suffix = " (" + before + value + after + ")";
  const name = row.extra.endsWith(suffix) ? row.extra.slice(0, -suffix.length) : row.extra;
  const box = document.createElement("input");
  box.type = "number";
  box.className = "row-input";
  box.min = min;
  box.max = max;
  box.value = value;
  box.title = title;
  box.setAttribute("aria-label", `${name}: ${title}`);
  sizeInlineNumber(box);
  const commit = () => {
    const v = clampInput(box);
    sizeInlineNumber(box);
    if (v === value) return;
    state.cfg.rowInputs[row.extraCls] = v;
    refresh(); // the rows keep their places (idx), so what is plotted stays plotted
  };
  // never above the max as typed: 150 Health shows 100 (owner, 2026-11-19: "65 units")
  box.oninput = () => {
    if (box.value !== "" && Number(box.value) > max) box.value = max;
    sizeInlineNumber(box);
  };
  // the row toggles its plot on click and on Enter / Space: typing in the box must do neither
  for (const type of ["click", "pointerdown", "keydown"]) box.addEventListener(type, (event) => event.stopPropagation());
  box.addEventListener("keydown", (event) => {
    if (event.key === "Enter") box.blur();
    // a one-digit box (Hold the Line's 0-7): each digit is the new value, at once
    else if (max < 10 && /^[0-9]$/.test(event.key)) {
      event.preventDefault();
      box.value = event.key;
      commit();
    }
  });
  box.onchange = commit;
  // the whole number is selected on focus, so typing replaces it rather than appending to it
  let picked = false;
  box.addEventListener("focus", () => {
    box.select();
    picked = true;
  });
  box.addEventListener("mouseup", (event) => {
    if (picked) event.preventDefault(); // Chromium collapses the selection on the click's mouseup
    picked = false;
  });
  cell.append(name + " (" + before, box, after + ")");
}

// The "+" at the end of a row's name: adds the row's extra to the setup (rowAddPlan); its click doesn't plot the row.
function rowAddButton(row) {
  const plan = rowAddPlan(row);
  if (!plan) return null;
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "row-add";
  btn.textContent = "+";
  btn.title = plan.title;
  btn.setAttribute("aria-label", plan.title);
  btn.disabled = !!plan.disabled;
  btn.onclick = (event) => {
    event.stopPropagation();
    if (plan.run) plan.run();
  };
  btn.onkeydown = (event) => event.stopPropagation(); // Enter / Space on it must not toggle the row
  return btn;
}

// The row the fight viewer shows: the one clicked last, if this table has it, else NoItem.
function vizRow() {
  const payload = state.current;
  if (!payload) return null;
  const want = state.vizRow;
  const picked = want && want.slice === state.slice ? payload.rows.find((r) => r.extra === want.extra) : null;
  return picked || payload.rows.find((r) => r.extraCls === "NoItem") || payload.rows[0] || null;
}

// The viewer's row picker: the plotted rows (in legend order), plus the row on view if it isn't plotted (NoItem
// before anything is). Its edge wears the row's line colour; the row's own art sits beside it.
function renderVizPicker(row) {
  const sel = $("vizRowSel");
  const entries = selectedRows();
  const options = entries.map(({ row: r, slot }) => ({ row: r, slot }));
  if (row && !options.some((o) => o.row === row)) options.unshift({ row, slot: null });
  sel.innerHTML = "";
  for (const o of options) sel.add(new Option(o.row.extra, o.row.extra));
  sel.value = row ? row.extra : "";
  sel.disabled = options.length < 2;
  const chosen = options.find((o) => o.row === row);
  sel.style.borderLeftColor = chosen && chosen.slot != null ? seriesColor(chosen.slot) : "";
  const art = $("vizRowArt");
  art.innerHTML = "";
  if (row) {
    const node = rowArt(row);
    if (node) art.appendChild(node);
  }
}

// A row's art, as the table's first column draws it: a trait's badge at the row's level, else the icon (framed for
// artifacts and radiants), else nothing.
function rowArt(row, className = "row-icon") {
  if (state.traitTiers?.tiers?.[row.extraCls]) return traitBadge(row.extraCls, row.extraLevel);
  const src = state.icons.get(row.extraCls);
  return src ? itemIcon(src, row.extraCls, className) : null;
}

function updateViz() {
  const row = vizRow();
  renderVizPicker(row);
  if (!row) return;
  const cfg = Object.assign(cfgForSlice(state.slice), { row: row.idx, seconds: state.vizSeconds });
  const champ = state.catalog.champions.find((c) => c.name === state.cfg.champ);
  FightViewer.load(JSON.stringify(cfg), {
    label: row.extra,
    champLabel: champ ? champ.label || champ.name : state.cfg.champ,
    level: state.cfg.level,
  });
}

function sortableHeader(col) {
  const th = document.createElement("th");
  th.className = "sortable";
  th.textContent = col.label;
  if (col.title) th.title = col.title;

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
// Rendering: the damage chart
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
  const selection = plottedSlots();
  const byIdx = new Map(payload.rows.map((row) => [row.idx, row]));
  // Ordered by slot, i.e. by when each row was added, so the legend doesn't
  // reshuffle when the table is sorted.
  return [...selection.entries()]
    .sort((a, b) => a[1] - b[1])
    .map(([idx, slot]) => ({ row: byIdx.get(idx), slot }))
    .filter((entry) => entry.row);
}

// How each bonus box reads in the chart heading (sim_entry applies ad, as, dmgamp, crit, critdmg as percents).
const BONUS_SUMMARY = {
  ad: (v) => `+${v}% AD`,
  ap: (v) => `+${v} AP`,
  as: (v) => `+${v}% AS`,
  dmgamp: (v) => `+${v}% Amp`,
  crit: (v) => `+${v}% Crit`,
  critdmg: (v) => `+${v}% Crit dmg`,
  manaregen: (v) => `+${v} Mana regen`,
  mpa: (v) => `+${v} Mana/atk`,
};

// Each bonus box's glyph in icons/stats (the client's rich-text icon tags, lower-cased) and whether it reads as a %.
const BONUS_GLYPHS = {
  ad: { glyph: "ad", pct: true, name: "AD" },
  ap: { glyph: "ap", pct: false, name: "AP" },
  as: { glyph: "as", pct: true, name: "AS" },
  dmgamp: { glyph: "damageamp", pct: true, name: "Amp" },
  crit: { glyph: "critchance", pct: true, name: "Crit" },
  critdmg: { glyph: "critdmg", pct: true, name: "Crit dmg" },
  manaregen: { glyph: "manaregen", pct: false, name: "Mana regen" },
  mpa: { glyph: "mana", pct: false, name: "Mana/atk" },
};

// The chart's and the viewer's headings: the setup every row shares, in pictures. The champion's portrait with its
// stars on it, its items, each active trait's badge with its level, augments, and the stat bonuses typed in. Drawn
// from the config that produced the table, so it never runs ahead of the lines under it.
function renderPlotSummary() {
  renderSetupSummary($("plotSummary"));
  renderSetupSummary($("vizSetup"));
}

function renderSetupSummary(box) {
  box.innerHTML = "";
  const cfg = state.currentCfg;
  if (!cfg) return;
  const add = (node, title) => {
    if (title) node.title = title;
    box.appendChild(node);
    return node;
  };
  const img = (src, cls) => {
    const i = document.createElement("img");
    i.src = src;
    i.alt = "";
    i.className = cls;
    return i;
  };

  const meta = champMeta(cfg.champ);
  const champ = document.createElement("span");
  champ.className = "ps-champ";
  champ.style.setProperty("--cost", costColour(meta?.cost));
  const portrait = state.icons.get(cfg.champ);
  if (portrait) champ.appendChild(img(portrait, "ps-portrait"));
  else champ.appendChild(Object.assign(document.createElement("span"), { className: "ps-portrait no-icon", textContent: cfg.champ.slice(0, 2) }));
  const stars = document.createElement("span");
  stars.className = "ps-stars";
  stars.textContent = "★".repeat(cfg.level);
  champ.appendChild(stars);
  add(champ, `${meta ? meta.label || meta.name : cfg.champ} ${"★".repeat(cfg.level)}`);

  const items = cfg.items.filter((cls) => cls && cls !== "NoItem");
  if (items.length) {
    const group = add(Object.assign(document.createElement("span"), { className: "ps-group" }));
    for (const cls of items) {
      const name = state.catalog.sidebarItems.find((i) => i.cls === cls)?.name || cls;
      const src = state.icons.get(cls);
      const node = src ? itemIcon(src, cls, "ps-item") : Object.assign(document.createElement("span"), { className: "ps-chip", textContent: name });
      node.title = name;
      group.appendChild(node);
    }
  }

  const buffs = cfg.buffs.filter(([, level]) => level > 0);
  if (buffs.length) {
    const group = add(Object.assign(document.createElement("span"), { className: "ps-group" }));
    for (const [cls, level] of buffs) {
      const b = state.buffMeta.get(cls);
      const name = b ? b.name : cls;
      const node = document.createElement("span");
      node.className = "ps-buff";
      node.title = b && b.kind === "Trait" ? `${name} ${level}` : name;
      const badge = b && b.kind === "Trait" ? traitBadge(cls, level) : null;
      const src = state.icons.get(cls);
      if (badge) node.appendChild(badge);
      else if (src) node.appendChild(img(src, "ps-item"));
      else node.appendChild(Object.assign(document.createElement("span"), { className: "ps-chip", textContent: name }));
      // a trait's level beside its badge; an augment (one level) needs none
      if (b && b.kind === "Trait") {
        node.appendChild(Object.assign(document.createElement("span"), { className: "ps-level", textContent: level }));
      }
      group.appendChild(node);
    }
  }

  const bonuses = Object.entries(cfg.bonus || {}).filter(([, v]) => Number(v));
  if (bonuses.length) {
    const group = add(Object.assign(document.createElement("span"), { className: "ps-group" }));
    for (const [key, v] of bonuses) {
      // "+30" and the stat's own glyph (icons/stats, the game's rich-text icons), as an item card writes "15%[AD]"
      const how = BONUS_GLYPHS[key];
      const chip = document.createElement("span");
      chip.className = "ps-chip ps-bonus";
      const text = BONUS_SUMMARY[key] ? BONUS_SUMMARY[key](v) : `+${v} ${key}`;
      chip.title = text;
      if (how && state.statIcons.has(how.glyph)) {
        chip.appendChild(document.createTextNode(`+${v}${how.pct ? "%" : ""}`));
        const glyph = document.createElement("img");
        glyph.src = `icons/stats/${how.glyph}.png`;
        glyph.alt = how.name;
        chip.appendChild(glyph);
      } else {
        chip.textContent = text;
      }
      group.appendChild(chip);
    }
  }
}

function renderPlot() {
  renderPlotSummary();
  const entries = selectedRows();
  const hasRows = entries.length > 0;
  $("plotHint").hidden = hasRows;
  $("chartWrap").hidden = !hasRows;
  if (!window.Plotly) return;
  if (!hasRows) {
    Plotly.purge($("chart"));
    renderChartLegend();
    placePlayhead();
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
      line: { width: 2.5, color, shape: "linear" },
      name: label,
      hoverinfo: "skip",
    });
  });

  // No title: the section heading already names the chart.
  const layout = {
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    font: { size: 12, color: FONT_COLOR },
    xaxis: {
      title: { text: "Time (s)", font: { color: FONT_COLOR } },
      rangemode: "tozero", // the fight starts at 0 s, though the first damage lands later
      showgrid: true,
      gridcolor: GRID_COLOR,
      zeroline: false,
      tickfont: { color: FONT_COLOR },
    },
    yaxis: {
      title: { text: "Damage", font: { color: FONT_COLOR }, standoff: 10 },
      automargin: true,
      showgrid: true,
      gridcolor: GRID_COLOR,
      zeroline: false,
      tickformat: ",",
      tickfont: { color: FONT_COLOR },
    },
    showlegend: false, // drawn by renderChartLegend, with each row's art
    // no Plotly hover: the pointer moves the playhead's line and card instead (placePlayhead)
    hovermode: false,
    margin: { l: 58, r: 14, t: 12, b: 40 },
  };
  const gd = $("chart");
  Plotly.react(gd, traces, layout, { displaylogo: false, responsive: true }).then(() => {
    // the axes move on every redraw (new rows, a resize): keep the line on its time
    if (!gd.dataset.playheadHooked) {
      gd.dataset.playheadHooked = "1";
      gd.on("plotly_afterplot", () => {
        renderChartLegend();
        placePlayhead();
      });
    }
    renderChartLegend();
    placePlayhead();
  });
}

// The chart's legend: each plotted row's colour, art (an item's icon, framed for artifacts and radiants; a trait's
// badge) and name, at the plot's top-left. Clicking an entry shows its fight in the viewer.
function renderChartLegend() {
  const box = $("chartLegend");
  const gd = $("chart");
  const xa = gd._fullLayout && gd._fullLayout.xaxis;
  const ya = gd._fullLayout && gd._fullLayout.yaxis;
  const entries = !gd.data || $("chartWrap").hidden ? [] : selectedRows();
  box.innerHTML = "";
  box.hidden = !entries.length || !xa;
  if (box.hidden) return;
  const viewed = vizRow();
  for (const { row, slot } of entries) {
    const item = document.createElement("button");
    item.type = "button";
    item.className = "legend-row";
    if (row === viewed) item.classList.add("viewing");
    item.title = "Show this fight in the viewer";
    const swatch = document.createElement("i");
    swatch.style.background = seriesColor(slot);
    item.appendChild(swatch);
    const art = rowArt(row, "legend-art");
    if (art) item.appendChild(art);
    item.appendChild(Object.assign(document.createElement("span"), { textContent: row.extra }));
    item.onclick = () => {
      state.vizRow = { slice: state.slice, extra: row.extra };
      renderResults();
    };
    box.appendChild(item);
  }
  box.style.left = xa._offset + 10 + "px";
  box.style.top = ya._offset + 8 + "px";
}

// The playhead on the chart: a vertical line and a card with every plotted row's damage so far (each line's last
// point at or before that time), at the time under the pointer while it is over the plot, else the fight viewer's.
// Plain elements over the plot rather than Plotly shapes, so following playback costs no re-layout.
function placePlayhead() {
  const line = $("playLine");
  const label = $("playLabel");
  const gd = $("chart");
  const xa = gd._fullLayout && gd._fullLayout.xaxis;
  const ya = gd._fullLayout && gd._fullLayout.yaxis;
  const t = state.hoverTime ?? state.playhead;
  const entries = t == null || !gd.data || $("chartWrap").hidden ? [] : selectedRows();
  if (!entries.length || !xa || !ya) {
    line.hidden = true;
    label.hidden = true;
    return;
  }
  const x = xa._offset + xa.l2p(t);
  line.hidden = false;
  line.style.left = x + "px";
  line.style.top = ya._offset + "px";
  line.style.height = ya._length + "px";

  label.innerHTML = "";
  let highest = 0;
  const head = document.createElement("div");
  head.className = "play-time";
  head.textContent = t.toFixed(2) + " s";
  label.appendChild(head);
  for (const { row, slot } of entries) {
    const tl = state.current.timelines[String(row.idx)];
    // the last point at or before t (binary search; the times are sorted)
    let lo = 0;
    let hi = tl.t.length - 1;
    let k = -1;
    while (lo <= hi) {
      const mid = (lo + hi) >> 1;
      if (tl.t[mid] <= t + 1e-9) {
        k = mid;
        lo = mid + 1;
      } else hi = mid - 1;
    }
    const value = k < 0 ? 0 : tl.cum[k];
    highest = Math.max(highest, value);
    const item = document.createElement("div");
    item.className = "play-row";
    const swatch = document.createElement("i");
    swatch.style.background = seriesColor(slot);
    const name = document.createElement("span");
    name.textContent = row.extra;
    const num = document.createElement("b");
    num.textContent = Math.round(value).toLocaleString();
    item.append(swatch, name, num);
    label.appendChild(item);
  }
  label.hidden = false;
  // Beside the line (flipped to its left near the right edge), in the half of the plot the lines aren't in at
  // that time, and under the legend rather than over it.
  const right = xa._offset + xa._length;
  const width = label.offsetWidth;
  const height = label.offsetHeight;
  const left = x + 8 + width > right ? x - 8 - width : x + 8;
  const linesLow = ya.l2p(highest) > ya._length / 2; // pixels grow downwards
  let top = linesLow ? ya._offset + 6 : ya._offset + ya._length - height - 6;
  const legend = $("chartLegend").hidden ? null : $("chartLegend");
  if (legend && linesLow) {
    const box = legend.getBoundingClientRect();
    const origin = $("chartWrap").getBoundingClientRect();
    const lx = box.left - origin.left;
    const overlaps = left < lx + box.width && left + width > lx;
    if (overlaps) top = Math.max(top, box.bottom - origin.top + 6);
  }
  label.style.top = top + "px";
  label.style.left = left + "px";
}
