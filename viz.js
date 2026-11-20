// viz.js
//
// The fight viewer: replays one table row's fight (sim_entry.run_trace) on a small hex board. The champion and the
// dummies stand where layout.py put them; projectiles fly from their launch tick to their arrival tick, damage
// numbers rise from the unit hit, and a card beside the board shows the champion's stats as each tick ends.
//
// app.js owns the page; it calls FightViewer.init(rpc, iconUrl) once and FightViewer.load(configJson, info) whenever
// the row or the config changes. Nothing here simulates: every number is the trace's.

"use strict";

const FightViewer = (() => {
  const HEX = 215; // world units between hex centres (layout.HEX_UNITS)
  const HEX_R = HEX / Math.sqrt(3); // centre to corner of a pointy-top hex
  const ROW = (HEX * Math.sqrt(3)) / 2;
  const DMG_COLOURS = { physical: "#ff9f43", magical: "#5aa9ff", true: "#f2f2f2" };
  const TYPE_SHORT = { physical: "phys", magical: "magic", true: "true" };
  const PROJ_COLOURS = { attack: "#ffe2a8", ricochet: "#ffd166", wave: "#5ee0ff" };
  const SPELL_PROJ = "#c39bff";
  const NUMBER_LIFE = 0.9; // seconds a damage number stays up
  const SPEEDS = [0.1, 0.25, 0.5, 1, 2, 4];

  let rpc = null;
  let iconUrl = () => null;
  let onTime = () => {}; // told the playhead in seconds (null at the start), for the damage chart's line
  let lastTime;
  const cache = new Map(); // config json -> trace
  let loadSeq = 0;

  const v = {
    trace: null,
    info: null,
    now: 0, // playhead, in ticks (fractional while playing)
    playing: false,
    speed: 1,
    lastFrame: null,
    states: [], // per tick: the champion's and dummies' state as the tick ends
    dealt: [], // per tick: damage dealt up to and including it, [total, per unit...]
    perTick: null, // tick -> {physical, magical, true}
    portrait: null,
    selectedStat: null, // the stat whose modifiers the card lists (click a stat; again to close)
    shownTick: -1,
    view: null, // world -> screen transform
  };

  const el = {};

  // ------------------------------------------------------------------ setup
  function init(rpcFn, iconFn, timeFn) {
    rpc = rpcFn;
    iconUrl = iconFn;
    if (timeFn) onTime = timeFn;
    for (const id of ["vizCanvas", "vizStrip", "vizCard", "vizLog", "vizPlay", "vizBack", "vizFwd", "vizSpeed",
                      "vizTime", "vizWhat", "vizStatus", "vizStage", "viz", "vizLength"]) {
      el[id] = document.getElementById(id);
    }
    for (const s of SPEEDS) el.vizSpeed.appendChild(new Option(s + "×", String(s)));
    el.vizSpeed.value = "1";
    el.vizSpeed.onchange = () => (v.speed = Number(el.vizSpeed.value));
    el.vizPlay.onclick = togglePlay;
    el.vizBack.onclick = () => step(-1);
    el.vizFwd.onclick = () => step(1);
    el.viz.addEventListener("keydown", (event) => {
      if (event.target.tagName === "SELECT") return;
      if (event.key === " ") {
        event.preventDefault();
        togglePlay();
      } else if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
        event.preventDefault();
        step((event.key === "ArrowLeft" ? -1 : 1) * (event.shiftKey ? 30 : 1));
      }
    });
    seekOnDrag(el.vizStrip);
    el.vizCard.addEventListener("click", (event) => {
      const row = event.target.closest("[data-stat]");
      if (row) {
        v.selectedStat = v.selectedStat === row.dataset.stat ? null : row.dataset.stat;
        v.shownTick = -1;
        draw();
      }
    });
    el.vizLog.addEventListener("click", (event) => {
      const row = event.target.closest("[data-tick]");
      if (row) seek(Number(row.dataset.tick));
    });
    new ResizeObserver(() => draw()).observe(el.vizStage);
    new ResizeObserver(() => draw()).observe(el.viz); // its height is the pane's rest when the chart is aligned
  }

  function seekOnDrag(canvas) {
    let dragging = false;
    const at = (event) => {
      const rect = canvas.getBoundingClientRect();
      const x = Math.min(Math.max(event.clientX - rect.left, 0), rect.width);
      seek(Math.round((x / rect.width) * (v.trace ? v.trace.ticks - 1 : 0)));
    };
    canvas.addEventListener("pointerdown", (event) => {
      if (!v.trace) return;
      dragging = true;
      canvas.setPointerCapture(event.pointerId);
      at(event);
    });
    canvas.addEventListener("pointermove", (event) => dragging && at(event));
    canvas.addEventListener("pointerup", () => (dragging = false));
  }

  // ------------------------------------------------------------------ loading
  // info: {label, champLabel, champCls, level} for the heading while the trace runs.
  async function load(configJson, info) {
    if (configJson === v.key) return; // already showing (or fetching) this fight
    v.key = configJson;
    const seq = ++loadSeq;
    v.info = info;
    el.vizWhat.textContent = info.champLabel + " " + "★".repeat(info.level) + " · " + info.label;
    let trace = cache.get(configJson);
    if (!trace) {
      setStatus("Simulating the fight…");
      try {
        trace = await rpc("trace", configJson);
      } catch (err) {
        if (seq !== loadSeq) return;
        v.key = null; // let the same request try again
        console.error("Fight trace failed:\n" + err.message);
        const lines = err.message.split("\n").filter((l) => l.trim() && !/^\s+at /.test(l));
        setStatus("Fight failed: " + (lines[lines.length - 1] || "unknown error"));
        return;
      }
      if (cache.size > 30) cache.clear();
      cache.set(configJson, trace);
    }
    if (seq !== loadSeq) return;
    setStatus(null);
    show(trace);
  }

  function setStatus(text) {
    el.vizStatus.hidden = !text;
    el.vizStatus.textContent = text || "";
  }

  function show(trace) {
    v.trace = trace;
    prepare(trace);
    const src = iconUrl(trace.champion.cls);
    v.portrait = null;
    if (src) {
      const img = new Image();
      img.onload = () => {
        if (v.trace === trace) {
          v.portrait = img;
          draw();
        }
      };
      img.src = src;
    }
    // a new fight (another row, item, buff or setting) starts from the beginning; playing carries on from there
    v.now = 0;
    v.lastFrame = null;
    v.shownTick = -1;
    draw();
  }

  // Snapshots hold only what changed; expand them to one state per tick, and add up the damage.
  function prepare(trace) {
    const n = trace.ticks;
    v.states = new Array(n);
    let state = {};
    let k = 0;
    for (let t = 0; t < n; t++) {
      if (k < trace.snapshots.length && trace.snapshots[k][0] === t) {
        state = Object.assign({}, state, trace.snapshots[k][1]);
        k++;
      }
      v.states[t] = state;
    }
    const units = trace.units.length;
    v.perTick = new Map();
    const add = new Array(n).fill(null);
    for (const d of trace.damage) {
      if (!add[d.t]) add[d.t] = new Array(units + 1).fill(0);
      add[d.t][0] += d.v;
      if (d.to != null) add[d.t][d.to + 1] += d.v;
      const bucket = v.perTick.get(d.t) || { physical: 0, magical: 0, true: 0 };
      bucket[d.type] = (bucket[d.type] || 0) + d.v;
      v.perTick.set(d.t, bucket);
    }
    v.dealt = new Array(n);
    v.byType = new Array(n); // per tick: damage so far by type, for the card's split
    let run = new Array(units + 1).fill(0);
    let types = { physical: 0, magical: 0, true: 0 };
    for (let t = 0; t < n; t++) {
      if (add[t]) run = run.map((x, i) => x + add[t][i]);
      const b = v.perTick.get(t);
      if (b) types = { physical: types.physical + b.physical, magical: types.magical + b.magical, true: types.true + b.true };
      v.dealt[t] = run;
      v.byType[t] = types;
    }
    // a cast's lock, for the board's cast ring and the strip
    v.casts = trace.marks.filter((m) => m.kind === "cast");
  }

  // ------------------------------------------------------------------ playback
  function togglePlay() {
    if (!v.trace) return;
    if (!v.playing && v.now >= v.trace.ticks - 1) v.now = 0;
    v.playing = !v.playing;
    v.lastFrame = null;
    el.vizPlay.textContent = v.playing ? "❚❚" : "▶";
    el.vizPlay.setAttribute("aria-label", v.playing ? "Pause" : "Play");
    if (v.playing) requestAnimationFrame(frame);
  }

  function frame(ts) {
    if (!v.playing || !v.trace) return;
    if (v.lastFrame != null) {
      v.now += ((ts - v.lastFrame) / 1000) * v.trace.tps * v.speed;
      if (v.now >= v.trace.ticks - 1) {
        v.now = v.trace.ticks - 1;
        togglePlay();
      }
    }
    v.lastFrame = ts;
    draw();
    if (v.playing) requestAnimationFrame(frame);
  }

  function step(n) {
    if (!v.trace) return;
    if (v.playing) togglePlay();
    seek(Math.floor(v.now + 1e-6) + n);
  }

  function seek(t) {
    if (!v.trace) return;
    v.now = Math.min(Math.max(t, 0), v.trace.ticks - 1);
    v.lastFrame = null;
    draw();
  }

  // ------------------------------------------------------------------ drawing
  function draw() {
    if (!v.trace || !el.vizStage.clientWidth) return;
    drawBoard();
    drawStrip();
    const tick = Math.floor(v.now + 1e-6);
    const secs = (v.now / v.trace.tps).toFixed(2);
    el.vizTime.textContent = `${secs} s · tick ${tick} / ${v.trace.ticks - 1}`;
    // nothing to mark at 0 s: a fresh fight clears the chart's line
    const time = v.now > 0 ? v.now / v.trace.tps : null;
    if (time !== lastTime) {
      lastTime = time;
      onTime(time);
    }
    if (tick !== v.shownTick) {
      v.shownTick = tick;
      renderCard(tick);
      renderLog(tick);
    }
  }

  function world(h) {
    return [HEX * (h[0] + h[1] / 2), ROW * h[1]];
  }

  function unitPos(i) {
    return world(v.trace.units[i].hex);
  }

  function point(p) {
    return Array.isArray(p) ? p : unitPos(p);
  }

  function setupCanvas(canvas, cssHeight) {
    const dpr = window.devicePixelRatio || 1;
    const w = canvas.parentElement.clientWidth;
    if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(cssHeight * dpr)) {
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(cssHeight * dpr);
      canvas.style.width = w + "px";
      canvas.style.height = cssHeight + "px";
    }
    const ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return [ctx, w, cssHeight];
  }

  function drawBoard() {
    const tr = v.trace;
    const live = tr.units.map((u, i) => i).filter((i) => tr.units[i].champion || tr.units[i].inPlay);
    const qs = live.map((i) => tr.units[i].hex);
    const pts = qs.map(world);
    const xmin = Math.min(...pts.map((p) => p[0])) - HEX * 1.1;
    const xmax = Math.max(...pts.map((p) => p[0])) + HEX * 1.1;
    const ymin = Math.min(...pts.map((p) => p[1])) - ROW * 0.95;
    const ymax = Math.max(...pts.map((p) => p[1])) + ROW * 0.7;
    const width = el.vizStage.clientWidth;
    const scale = width / (xmax - xmin);
    // as tall as the board's shape asks, up to what the viewer has room for: side by side its height is fixed (the
    // pane under the aligned chart), so the board fits it and leaves the log a few lines; stacked, ~28% of the pane
    let tallest;
    if (window.matchMedia("(min-width: 1321px)").matches) {
      const left = el.vizStage.parentElement;
      const others = [...left.children].filter((c) => c !== el.vizStage && !c.classList.contains("viz-log"))
        .reduce((sum, c) => sum + c.offsetHeight, 0);
      const room = el.viz.getBoundingClientRect().bottom - el.vizStage.getBoundingClientRect().top - others - 44;
      tallest = Math.min(Math.max(room, 110), 300);
    } else {
      const pane = el.viz.parentElement;
      tallest = Math.min(Math.max(190, (pane ? pane.clientHeight : 0) * 0.28), 300);
    }
    const height = Math.min(Math.max((ymax - ymin) * scale, Math.min(150, tallest)), tallest);
    const [ctx, W, H] = setupCanvas(el.vizCanvas, height);
    const s = Math.min(W / (xmax - xmin), H / (ymax - ymin));
    const ox = (W - (xmax - xmin) * s) / 2 - xmin * s;
    const oy = (H - (ymax - ymin) * s) / 2 - ymin * s;
    const S = (p) => [ox + p[0] * s, oy + p[1] * s];
    v.view = { s, S };
    ctx.clearRect(0, 0, W, H);

    // the hexes
    const rmin = Math.floor(ymin / ROW) - 1, rmax = Math.ceil(ymax / ROW) + 1;
    for (let r = rmin; r <= rmax; r++) {
      const q0 = Math.floor(xmin / HEX - r / 2) - 1, q1 = Math.ceil(xmax / HEX - r / 2) + 1;
      for (let q = q0; q <= q1; q++) {
        const [cx, cy] = S(world([q, r]));
        ctx.beginPath();
        for (let k = 0; k < 6; k++) {
          const a = (Math.PI / 180) * (60 * k + 30);
          const x = cx + HEX_R * 0.96 * s * Math.cos(a), y = cy + HEX_R * 0.96 * s * Math.sin(a);
          k ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
        }
        ctx.closePath();
        ctx.fillStyle = "#161a23";
        ctx.fill();
        ctx.strokeStyle = "#262a36";
        ctx.lineWidth = 1;
        ctx.stroke();
      }
    }

    const now = v.now;
    const tick = Math.floor(now + 1e-6);
    const state = v.states[tick] || {};
    const unitR = HEX * 0.3 * s;
    const secs = (t) => t / tr.tps;

    // marks under the units: areas, beams, dashes
    for (const m of tr.marks) {
      const age = secs(now - m.t);
      if (age < 0) continue;
      if (m.kind === "area") {
        const life = Math.max(m.seconds || 0, 0.35);
        if (age > life) continue;
        const fade = 1 - age / life;
        const hit = [m.at, ...(m.hit || [])].filter((x) => x != null);
        for (const i of hit) {
          const [x, y] = S(unitPos(i));
          ctx.beginPath();
          ctx.arc(x, y, unitR * 1.55, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(195, 155, 255, ${0.22 * fade})`;
          ctx.fill();
        }
        const [x, y] = S(unitPos(m.at));
        ctx.beginPath();
        ctx.arc(x, y, unitR * (1.2 + 1.6 * Math.min(age / 0.35, 1)), 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(195, 155, 255, ${0.8 * fade})`;
        ctx.lineWidth = 2;
        ctx.stroke();
      } else if (m.kind === "beam") {
        if (age > 0.22) continue;
        const fade = 1 - age / 0.22;
        const [x0, y0] = S(unitPos(0));
        for (const i of [m.at, ...(m.hit || [])]) {
          const [x1, y1] = S(unitPos(i));
          ctx.beginPath();
          ctx.moveTo(x0, y0);
          ctx.lineTo(x1, y1);
          ctx.strokeStyle = `rgba(195, 155, 255, ${0.85 * fade})`;
          ctx.lineWidth = i === m.at ? 5 : 3;
          ctx.stroke();
        }
      } else if (m.kind === "dash") {
        const life = secs(m.ticks || 6) + 0.15;
        if (age > life) continue;
        const [x0, y0] = S(unitPos(0));
        const target = m.to != null ? S(unitPos(m.to)) : [x0 + (m.hexes || 1) * HEX * s, y0];
        ctx.save();
        ctx.setLineDash([6, 5]);
        ctx.beginPath();
        ctx.moveTo(x0, y0);
        ctx.lineTo(target[0], target[1]);
        ctx.strokeStyle = `rgba(255, 75, 75, ${0.9 * (1 - age / life)})`;
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.restore();
        label(ctx, (m.name ? m.name + " " : "") + "dash", (x0 + target[0]) / 2, (y0 + target[1]) / 2 - 8, "#ff8a8a", 11);
      }
    }

    // the units
    tr.units.forEach((u, i) => {
      if (!u.champion && !u.inPlay) return;
      const [x, y] = S(world(u.hex));
      if (u.champion) drawChampion(ctx, x, y, unitR, state, tick);
      else drawDummy(ctx, x, y, unitR, i, state, tick);
    });

    // projectiles
    for (const p of tr.projectiles) {
      if (now < p.t0 || now > p.t1 + 0.999) continue;
      const span = Math.max(p.t1 - p.t0, 1e-9);
      const f = Math.min((now - p.t0) / span, 1);
      const a = S(point(p.from)), b = S(point(p.to));
      const colour = PROJ_COLOURS[p.name] || SPELL_PROJ;
      if (p.name === "wave") {
        drawWave(ctx, a, b, f, colour, s);
        continue;
      }
      let x = a[0] + (b[0] - a[0]) * f, y = a[1] + (b[1] - a[1]) * f;
      const dist = Math.hypot(b[0] - a[0], b[1] - a[1]);
      if (dist < 2) y -= Math.sin(f * Math.PI) * unitR * 2.2; // a bounce in place: a hop
      const big = p.name !== "attack" && p.name !== "ricochet";
      const ux = dist > 2 ? (b[0] - a[0]) / dist : 0, uy = dist > 2 ? (b[1] - a[1]) / dist : 0;
      const trail = Math.min(HEX * 0.45 * s, f * dist);
      const grad = ctx.createLinearGradient(x - ux * trail, y - uy * trail, x, y);
      grad.addColorStop(0, "rgba(0,0,0,0)");
      grad.addColorStop(1, colour);
      ctx.beginPath();
      ctx.moveTo(x - ux * trail, y - uy * trail);
      ctx.lineTo(x, y);
      ctx.strokeStyle = grad;
      ctx.lineWidth = big ? 4 : 2.5;
      ctx.lineCap = "round";
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(x, y, big ? 5.5 : 3.5, 0, Math.PI * 2);
      ctx.fillStyle = colour;
      ctx.shadowColor = colour;
      ctx.shadowBlur = big ? 12 : 6;
      ctx.fill();
      ctx.shadowBlur = 0;
    }

    // damage numbers, newest on top; several on one unit in one tick stack upwards
    const stack = new Map();
    const shown = [];
    for (const d of tr.damage) {
      if (d.t > now) break;
      const age = secs(now - d.t);
      if (age > NUMBER_LIFE || d.to == null) continue;
      shown.push(d);
    }
    for (const d of shown) {
      const key = d.t + ":" + d.to;
      const n = stack.get(key) || 0;
      stack.set(key, n + 1);
      const age = secs(now - d.t);
      const [x, y] = S(unitPos(d.to));
      const rise = 10 + age * 46;
      const alpha = age > NUMBER_LIFE - 0.3 ? (NUMBER_LIFE - age) / 0.3 : 1;
      const size = d.kind === "spell" ? 16 : d.kind === "item" ? 12 : 14;
      const text = d.v >= 10 ? String(Math.round(d.v)) : d.v.toFixed(1);
      ctx.globalAlpha = Math.max(alpha, 0);
      label(ctx, text, x + ((n % 3) - 1) * 16, y - unitR - rise - Math.floor(n / 3) * 15 - (n % 3 ? 7 : 0),
            DMG_COLOURS[d.type] || "#fff", size, true);
      ctx.globalAlpha = 1;
    }
  }

  function drawWave(ctx, a, b, f, colour, s) {
    const dx = b[0] - a[0], dy = b[1] - a[1];
    const len = Math.hypot(dx, dy) || 1;
    const ux = dx / len, uy = dy / len;
    const x = a[0] + dx * f, y = a[1] + dy * f;
    const half = 300 * s; // the wave's 600-unit width
    ctx.beginPath();
    ctx.moveTo(x - uy * half, y + ux * half);
    ctx.lineTo(x + uy * half, y - ux * half);
    ctx.strokeStyle = colour;
    ctx.lineWidth = 5;
    ctx.shadowColor = colour;
    ctx.shadowBlur = 10;
    ctx.stroke();
    ctx.shadowBlur = 0;
  }

  function label(ctx, text, x, y, colour, size, bold) {
    ctx.font = `${bold ? "700 " : "600 "}${size}px -apple-system, "Segoe UI", Roboto, sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.lineWidth = 3;
    ctx.strokeStyle = "rgba(8, 10, 14, 0.9)";
    ctx.strokeText(text, x, y);
    ctx.fillStyle = colour;
    ctx.fillText(text, x, y);
  }

  function lastCast(tick) {
    let found = null;
    for (const c of v.casts) {
      if (c.t > tick) break;
      found = c;
    }
    return found;
  }

  function drawChampion(ctx, x, y, r, state, tick) {
    const tr = v.trace;
    // the cast: a ring that fills over the cast lock, and a pulse as it starts
    const cast = lastCast(tick);
    if (cast) {
      const age = (v.now - cast.t) / tr.tps;
      if (age < 0.45) {
        ctx.beginPath();
        ctx.arc(x, y, r * (1.1 + age * 3), 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(255, 75, 75, ${1 - age / 0.45})`;
        ctx.lineWidth = 3;
        ctx.stroke();
        label(ctx, "CAST", x, y - r - 14 - age * 20, "#ff6b6b", 12, true);
      }
    }
    // attack launch flash
    for (const m of tr.marks) {
      if (m.kind !== "launch" || m.t > v.now) continue;
      const age = (v.now - m.t) / tr.tps;
      if (age < 0.15) {
        ctx.beginPath();
        ctx.arc(x, y, r * 1.18, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(255, 226, 168, ${1 - age / 0.15})`;
        ctx.lineWidth = 2;
        ctx.stroke();
      }
    }
    ctx.save();
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.clip();
    if (v.portrait) ctx.drawImage(v.portrait, x - r, y - r, r * 2, r * 2);
    else {
      ctx.fillStyle = "#3a3f52";
      ctx.fillRect(x - r, y - r, r * 2, r * 2);
    }
    ctx.restore();
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.strokeStyle = state.casting ? "#ff4b4b" : "#e8c26a";
    ctx.lineWidth = 2.5;
    ctx.stroke();
    if (state.casting && cast && cast.lock > 0) {
      const f = Math.min((v.now - cast.t) / cast.lock, 1);
      ctx.beginPath();
      ctx.arc(x, y, r + 4, -Math.PI / 2, -Math.PI / 2 + f * Math.PI * 2);
      ctx.strokeStyle = "#ff4b4b";
      ctx.lineWidth = 3;
      ctx.stroke();
    }
    // mana bar
    const w = r * 2.4, h = 6, bx = x - w / 2, by = y + r + 7;
    ctx.fillStyle = "#0b0d12";
    ctx.fillRect(bx - 1, by - 1, w + 2, h + 2);
    const full = state.maxMana > 0 ? Math.min(state.mana / state.maxMana, 1) : 0;
    ctx.fillStyle = state.lockedUntil != null ? "#55607a" : "#4d8dff";
    ctx.fillRect(bx, by, w * full, h);
    if (state.lockedUntil != null) label(ctx, "mana locked", x, by + h + 9, "#9aa3b8", 10);
  }

  function drawDummy(ctx, x, y, r, i, state, tick) {
    const hitNow = v.trace.damage.some((d) => d.to === i && d.t <= v.now && v.now - d.t < 3);
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fillStyle = hitNow ? "#4a3a3a" : "#33384a";
    ctx.fill();
    ctx.strokeStyle = i === 1 ? "#ff4b4b" : "#5b6175";
    ctx.lineWidth = i === 1 ? 2.5 : 1.5;
    ctx.stroke();
    label(ctx, i === 1 ? "T" : String(i), x, y, "#e6e8ef", 13, true);
    const taken = (v.dealt[tick] || [])[i + 1] || 0;
    label(ctx, Math.round(taken).toLocaleString(), x, y + r + 10, "#a3a8b8", 11);
    const d = state["d" + i];
    if (d && d.effects && d.effects.length) label(ctx, d.effects.join(", "), x, y + r + 23, "#c39bff", 10);
  }

  function drawStrip() {
    const tr = v.trace;
    const [ctx, W, H] = setupCanvas(el.vizStrip, 42);
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = "#12151d";
    ctx.fillRect(0, 0, W, H);
    const n = tr.ticks;
    const X = (t) => (t / Math.max(n - 1, 1)) * W;
    // cast locks
    for (const c of v.casts) {
      ctx.fillStyle = "rgba(255, 75, 75, 0.18)";
      ctx.fillRect(X(c.t), 0, Math.max(X(c.t + Math.max(c.lock, 1)) - X(c.t), 1.5), H - 12);
      ctx.fillStyle = "#ff4b4b";
      ctx.fillRect(X(c.t), 0, 1.5, H - 12);
    }
    // damage per tick, stacked by type, square-root scale
    let max = 0;
    for (const b of v.perTick.values()) max = Math.max(max, b.physical + b.magical + b.true);
    const base = H - 13;
    for (const [t, b] of v.perTick) {
      let y = base;
      for (const type of ["physical", "magical", "true"]) {
        if (!b[type]) continue;
        const total = b.physical + b.magical + b.true;
        const h = (Math.sqrt(total / max) * (base - 3) * b[type]) / total;
        ctx.fillStyle = DMG_COLOURS[type];
        ctx.fillRect(X(t) - 0.75, y - h, 1.5, h);
        y -= h;
      }
    }
    // seconds
    ctx.fillStyle = "#6c7286";
    ctx.font = "10px -apple-system, 'Segoe UI', Roboto, sans-serif";
    ctx.textBaseline = "bottom";
    const secs = (n - 1) / tr.tps;
    const every = secs > 45 ? 10 : 5;
    for (let s = 0; s <= secs; s += every) {
      ctx.textAlign = s === 0 ? "left" : "center";
      ctx.fillText(s + "s", X(s * tr.tps), H);
    }
    // playhead
    ctx.fillStyle = "#fafafa";
    ctx.fillRect(X(v.now) - 1, 0, 2, H - 11);
  }

  // ------------------------------------------------------------------ the card and the log
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const pct = (x) => (x * 100).toFixed(x * 100 >= 100 ? 0 : 1) + "%";
  const num = (x, d = 2) => (Math.abs(x) >= 100 ? x.toFixed(0) : x.toFixed(d));

  function renderCard(tick) {
    const tr = v.trace;
    const s = v.states[tick] || {};
    const secs = tick / tr.tps;
    const dealt = (v.dealt[tick] || [0])[0];
    let status = "Attacking";
    if (s.casting) status = `Casting, attacks again at ${(s.busyUntil / tr.tps).toFixed(2)} s`;
    // a spell that lifts its own lock holds one of 10^6 s until then (Ashe, Olaf, Kayle, Briar)
    const lock = s.lockedUntil == null ? "" : s.lockedUntil - tick > 1e5 ? "Mana locked until the spell lifts it"
      : `Mana locked until ${(s.lockedUntil / tr.tps).toFixed(2)} s`;
    const rows = [
      ["ad", "AD", num(s.ad, 1), s.adMult !== 1 ? `×${num(s.adMult)}` : ""],
      ["ap", "AP", pct(s.ap), ""],
      ["as", "Atk speed", num(s.as, 3), ""],
      ["crit", "Crit", pct(s.crit), ""],
      ["critDmg", "Crit dmg", pct(s.critDmg), ""],
      ["amp", "Amp", pct(s.amp - 1), ""],
      ["regen", "Mana regen", num(s.regen, 1) + "/s", ""],
      ["mpa", "Mana/atk", num(s.mpa, 1), s.manaMult !== 1 ? `×${num(s.manaMult)}` : ""],
    ];
    if (s.armorPen) rows.push(["", "Armor pen", pct(s.armorPen), ""]);
    if (s.mrPen) rows.push(["", "MR pen", pct(s.mrPen), ""]);
    if (s.omnivamp) rows.push(["", "Omnivamp", pct(s.omnivamp), ""]);
    // one line per modifier: its key without the effect's instance number, or the item and trait stats (unkeyed)
    const modLines = (key) => ((s.mods || {})[key] || []).map(([op, value, k]) =>
      `${k ? String(k).replace(/ \d+$/, "") : "item / trait stats"}: ${op} ${num(value, 3)}`);
    const mods = v.selectedStat ? modLines(v.selectedStat) : [];
    const selectedName = (rows.find((r) => r[0] === v.selectedStat) || [, ""])[1];
    const items = tr.items.filter((n) => n !== tr.extra);
    const manaFrac = s.maxMana > 0 ? Math.min(s.mana / s.maxMana, 1) : 0;

    el.vizCard.innerHTML = `
      <div class="viz-card-head">
        <strong>${esc(tr.champion.label)}</strong> <span class="viz-stars">${"★".repeat(tr.champion.level)}</span>
        <div class="viz-sub">${esc(tr.extra)}${items.length ? " · " + items.map(esc).join(", ") : ""}</div>
      </div>
      <div class="viz-status ${s.casting ? "is-casting" : ""}">${esc(status)}${lock ? `<br><span>${esc(lock)}</span>` : ""}</div>
      <div class="viz-mana"><div class="viz-mana-fill ${s.lockedUntil != null ? "locked" : ""}" style="width:${(manaFrac * 100).toFixed(1)}%"></div>
        <span>${num(s.mana, 1)} / ${num(s.maxMana, 0)} mana</span></div>
      <div class="viz-grid">${rows.map(([key, name, value, extra]) => `
        <div ${key ? `data-stat="${key}"` : ""} class="viz-cell ${key && key === v.selectedStat ? "selected" : ""}"
          title="${esc([extra, ...(key ? modLines(key) : [])].filter(Boolean).join("\n") || "no modifiers")}"
          ><span>${name}</span><b>${value}</b></div>`).join("")}
      </div>
      ${v.selectedStat ? `<div class="viz-mods"><div class="viz-dim">${esc(selectedName)}${mods.length ? "" : ": no modifiers"}</div>
        ${mods.map((line) => `<div title="${esc(line)}">${esc(line)}</div>`).join("")}</div>` : ""}
      <div class="viz-grid viz-totals">
        <div class="viz-cell"><span>Attacks</span><b>${s.attacks ?? 0}</b></div>
        <div class="viz-cell"><span>Casts</span><b>${s.casts ?? 0}</b></div>
        <div class="viz-cell"><span>Damage</span><b>${Math.round(dealt).toLocaleString()}</b></div>
        <div class="viz-cell"><span>DPS so far</span><b>${secs > 0 ? (dealt / secs).toFixed(1) : "–"}</b></div>
      </div>
      ${splitBar(v.byType[tick], dealt)}
      ${s.effects && s.effects.length ? `<div class="viz-effects">Effects on the champion: ${s.effects.map(esc).join(", ")}</div>` : ""}
      <div class="viz-dummies">${tr.units.slice(1).filter((u) => u.inPlay).map((u) => {
        const i = tr.units.indexOf(u);
        const d = s["d" + i] || {};
        return `<div><strong>${esc(u.name)}</strong> armor ${num(d.armor ?? 0, 0)}, MR ${num(d.mr ?? 0, 0)}` +
          `${d.effects && d.effects.length ? ` <span class="viz-dim">(${d.effects.map(esc).join(", ")})</span>` : ""}</div>`;
      }).join("")}</div>`;
  }

  // The damage so far by type: one bar in the strip's colours, the shares under it.
  function splitBar(types, total) {
    if (!types || !(total > 0)) return "";
    const parts = ["physical", "magical", "true"].filter((k) => types[k] > 0);
    const share = (k) => (types[k] / total) * 100;
    return `<div class="viz-split" title="Damage dealt so far, by type">
      <div class="viz-split-bar">${parts.map((k) =>
        `<i style="width:${share(k).toFixed(2)}%;background:${DMG_COLOURS[k]}"></i>`).join("")}</div>
      <div class="viz-split-key">${parts.map((k) =>
        `<span><i style="background:${DMG_COLOURS[k]}"></i>${TYPE_SHORT[k]} ${share(k).toFixed(1)}%</span>`).join("")}</div>
    </div>`;
  }

  function describe(e) {
    const tr = v.trace;
    if (e.cast) {
      const mana = e.cast.manaLock > 1e5 ? "mana locked until the spell lifts it" : `mana lock ${e.cast.manaLock} ticks`;
      return `<span class="viz-cast">Cast</span> · next attack in ${e.cast.lock} ticks, ${mana}`;
    }
    const d = e.damage;
    const who = tr.units[d.to] ? tr.units[d.to].name : "?";
    const what = d.by ? esc(d.by) : d.kind;
    return `<span style="color:${DMG_COLOURS[d.type]}">${d.v.toFixed(1)}</span> ${TYPE_SHORT[d.type] || d.type} → ` +
      `${esc(who)} <span class="viz-dim">${esc(d.kind === "attack" && !d.by ? "attack" : what)}</span>`;
  }

  function renderLog(tick) {
    const tr = v.trace;
    const out = [];
    let i = tr.damage.length - 1;
    let j = v.casts.length - 1;
    while (i >= 0 && tr.damage[i].t > tick) i--;
    while (j >= 0 && v.casts[j].t > tick) j--;
    while (out.length < 40 && (i >= 0 || j >= 0)) {
      if (j >= 0 && (i < 0 || v.casts[j].t >= tr.damage[i].t)) out.push({ t: v.casts[j].t, cast: v.casts[j--] });
      else out.push({ t: tr.damage[i].t, damage: tr.damage[i--] });
    }
    el.vizLog.innerHTML = out.length
      ? out.map((e) => `<div data-tick="${e.t}" class="${e.t === tick ? "now" : ""}">` +
          `<span class="viz-dim">${(e.t / tr.tps).toFixed(2)}s</span> ${describe(e)}</div>`).join("")
      : `<div class="viz-dim">Nothing has happened yet.</div>`;
  }

  return { init, load };
})();
