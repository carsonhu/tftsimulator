// Loads the set19 page in headless Edge, waits for the results table, reports the build picker, the champion,
// the first result rows and any console errors.
//     python serve.py 8619   (another shell), then: node page_e2e.js [http://127.0.0.1:8619/]
// Uses the installed Microsoft Edge (EDGE env var to override); puppeteer-core downloads no browser.
const puppeteer = require("puppeteer-core");

(async () => {
  const browser = await puppeteer.launch({
    executablePath: process.env.EDGE || "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    headless: true,
    args: ["--no-first-run"],
  });
  const page = await browser.newPage();
  const errors = [];
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  page.on("pageerror", (e) => errors.push("pageerror: " + e.message));
  await page.goto(process.argv[2] || "http://127.0.0.1:8619/", { waitUntil: "load" });
  const t0 = Date.now();
  try {
    await page.waitForFunction(() => document.querySelectorAll("#resultsTable tr").length > 1, { timeout: 120000 });
  } catch (e) {
    console.log("TIMEOUT waiting for results");
  }
  const read = () => page.evaluate(() => {
    const opts = (id) => [...document.querySelectorAll("#" + id + " option")].map((o) => o.textContent + "=" + o.value);
    return {
      build: opts("build"), buildValue: document.querySelector("#build").value,
      champ: document.querySelector("#champ").value, level: document.querySelector("#level").value,
      status: document.querySelector("#runStatus").hidden ? "" : document.querySelector("#runStatus").textContent,
      rows: [...document.querySelectorAll("#resultsTable tr")].slice(0, 3).map((r) => r.textContent.replace(/\s+/g, " ").trim()),
    };
  });
  const first = await read();
  console.log("after", Math.round((Date.now() - t0) / 1000), "s:", JSON.stringify(first, null, 1));

  // The champion's own traits are preselected in the buff bar (off); turning one up must change the results.
  // a row: the buff's hidden select, then its level select; the parameter (when it has one) on the line under them
  const buffRows = () => page.evaluate(() => [...document.querySelectorAll("#buffRows .buff-row")].map((r) => {
    const [buff, level] = r.querySelectorAll("select");
    const paramBox = r.querySelector(".buff-param");
    return { buff: buff.value, level: level.value, levels: [...level.options].map((o) => o.value),
             param: paramBox.hidden ? null : paramBox.querySelector("input[type=number]").value,
             paramTitle: paramBox.querySelector(".col-label").textContent };
  }));
  const bar = await buffRows();
  console.log("buff bar:", JSON.stringify(bar));
  // the default champion's own implemented trait (Draven: Trickshot)
  const idx = bar.findIndex((b) => b.buff !== "NoBuff");
  const trait = idx < 0 ? null : bar[idx].buff;
  if (idx < 0) {
    console.log("FAIL no trait of the champion preselected");
  } else {
    const last = bar[idx].levels[bar[idx].levels.length - 1];
    await page.evaluate((i, v) => {
      const sel = document.querySelectorAll("#buffRows .buff-row")[i].querySelectorAll("select")[1];
      sel.value = v;
      sel.dispatchEvent(new Event("change"));
    }, idx, last);
    try {
      await page.waitForFunction((before) => {
        const r = document.querySelectorAll("#resultsTable tr")[1];
        return r && r.textContent.replace(/\s+/g, " ").trim() !== before;
      }, { timeout: 60000 }, first.rows[1]);
      console.log(trait + " " + last + ":", JSON.stringify((await read()).rows));
    } catch (e) {
      console.log("FAIL results did not change after setting " + trait + " " + last);
    }
  }
  // Senna: her traits Hitmaker (with its "Is Big Shot" flag, default 1) preselected
  await page.evaluate(() => {
    const sel = document.querySelector("#champ");
    sel.value = "Senna";
    sel.dispatchEvent(new Event("change"));
  });
  try {
    await page.waitForFunction(() => [...document.querySelectorAll("#buffRows .buff-row select")].some((s) => s.value === "Hitmaker"),
                               { timeout: 30000 });
    const hm = (await buffRows()).find((b) => b.buff === "Hitmaker");
    console.log("Senna Hitmaker row:", JSON.stringify(hm));
    if (hm.paramTitle !== "Is Big Shot" || hm.param !== "1") console.log("FAIL Hitmaker's Is Big Shot flag");
  } catch (e) {
    console.log("FAIL Hitmaker not preselected for Senna");
  }
  // Ezreal: Heartsteel's tick boxes (Kayn, Alune, Aphelios, Ezreal, Bias; default Ezreal + Bias) on their own line
  await page.evaluate(() => {
    const sel = document.querySelector("#champ");
    sel.value = "Ezreal";
    sel.dispatchEvent(new Event("change"));
  });
  try {
    await page.waitForFunction(() => [...document.querySelectorAll("#buffRows .buff-row select")].some((s) => s.value === "Heartsteel"),
                               { timeout: 30000 });
    const flags = () => page.evaluate(() => {
      const row = [...document.querySelectorAll("#buffRows .buff-row")].find((r) => r.querySelector("select").value === "Heartsteel");
      const box = row.querySelector(".param-flags");
      return { hidden: box.hidden,
               ticks: [...box.querySelectorAll("label")].map((l) => l.textContent + "=" + l.querySelector("input").checked) };
    });
    const hs = await flags();
    console.log("Ezreal Heartsteel flags:", JSON.stringify(hs));
    if (hs.hidden || hs.ticks.join() !== "Kayn=false,Alune=false,Aphelios=false,Ezreal=true,Bias=false") {
      console.log("FAIL Heartsteel tick boxes");
    }
    const before = (await read()).rows[1];
    await page.evaluate(() => {
      const row = [...document.querySelectorAll("#buffRows .buff-row")].find((r) => r.querySelector("select").value === "Heartsteel");
      const level = row.querySelectorAll("select")[1];
      level.value = "3";
      level.dispatchEvent(new Event("change"));
      row.querySelector(".param-flags input").click();  // Kayn
    });
    await page.waitForFunction((b) => {
      const r = document.querySelectorAll("#resultsTable tr")[1];
      return r && r.textContent.replace(/\s+/g, " ").trim() !== b;
    }, { timeout: 60000 }, before);
    const after = await flags();
    console.log("Heartsteel 3 + Kayn:", JSON.stringify(after.ticks), JSON.stringify((await read()).rows));
    if (!after.ticks[0].endsWith("true")) console.log("FAIL Kayn tick did not stick");
  } catch (e) {
    console.log("FAIL Heartsteel row for Ezreal: " + e.message);
  }
  // The number of targets (layout.py): shown for Ezreal (his splash), default 2; 5 targets means more splash.
  // Hidden for a champion whose damage doesn't depend on it.
  try {
    const layout = () => page.evaluate(() => ({
      hidden: document.querySelector("#targetsRow").hidden,
      value: document.querySelector("#layoutTargets").value + "/" + document.querySelector("#layoutTargetsValue").textContent,
    }));
    const shown = await layout();
    console.log("targets slider:", JSON.stringify(shown));
    if (shown.hidden || shown.value !== "2/2") console.log("FAIL targets slider for Ezreal (shown, default 2)");
    const before = (await read()).rows[1];
    await page.evaluate(() => {
      const s = document.querySelector("#layoutTargets");
      s.value = "5";
      s.dispatchEvent(new Event("change"));
    });
    await page.waitForFunction((b) => {
      const r = document.querySelectorAll("#resultsTable tr")[1];
      return r && r.textContent.replace(/\s+/g, " ").trim() !== b;
    }, { timeout: 60000 }, before);
    console.log("5 targets:", JSON.stringify(await layout()), JSON.stringify((await read()).rows));
    await page.evaluate(() => {
      const sel = document.querySelector("#champ");
      sel.value = "Draven";
      sel.dispatchEvent(new Event("change"));
    });
    await page.waitForFunction(() => document.querySelector("#targetsRow").hidden, { timeout: 30000 });
    const draven = await layout();
    console.log("Draven targets slider:", JSON.stringify(draven));
    if (!draven.hidden) console.log("FAIL targets slider shown for Draven");
    // Vladimir (owner, 2026-11-20): buttons 3-9, default 7
    await page.evaluate(() => {
      const sel = document.querySelector("#champ");
      sel.value = "Vladimir";
      sel.dispatchEvent(new Event("change"));
    });
    await page.waitForFunction(() => !document.querySelector("#targetsRow").hidden, { timeout: 30000 });
    const vlad = await page.evaluate(() => ({
      value: document.querySelector("#layoutTargets").value,
      buttons: [...document.querySelectorAll("#targetsSeg button")].map((b) => b.textContent + (b.getAttribute("aria-checked") === "true" ? "*" : "")),
    }));
    console.log("Vladimir targets:", JSON.stringify(vlad));
    if (vlad.value !== "7" || vlad.buttons.join(",") !== "3,4,5,6,7*,8,9") console.log("FAIL Vladimir targets (3-9, default 7)");
    // Seraphine (owner, 2026-11-22): Indie has no Targets; the Superstar switch shows them at 8 (the whole board)
    await page.evaluate(() => {
      const sel = document.querySelector("#champ");
      sel.value = "Seraphine";
      sel.dispatchEvent(new Event("change"));
    });
    await page.waitForFunction(() => document.querySelector("#targetsRow").hidden, { timeout: 30000 });
    await page.evaluate(() => [...document.querySelectorAll("#champModes button")].find((b) => b.textContent === "Superstar").click());
    await page.waitForFunction(() => !document.querySelector("#targetsRow").hidden, { timeout: 30000 });
    const sera = await page.evaluate(() => ({
      champ: document.querySelector("#champ").value, value: document.querySelector("#layoutTargets").value,
      buttons: [...document.querySelectorAll("#targetsSeg button")].map((b) => b.textContent + (b.getAttribute("aria-checked") === "true" ? "*" : "")),
    }));
    console.log("Seraphine Superstar targets:", JSON.stringify(sera));
    if (sera.champ !== "SeraphineSuperstar" || sera.value !== "8" || sera.buttons.join(",") !== "1,2,3,4,5,6,7,8*,9")
      console.log("FAIL Seraphine Superstar targets (1-9, default 8)");
  } catch (e) {
    console.log("FAIL targets slider: " + e.message);
  }
  console.log("console errors:", errors.length ? errors : "none");
  await browser.close();
})();
