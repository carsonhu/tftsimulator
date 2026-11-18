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
  const buffRows = () => page.evaluate(() => [...document.querySelectorAll(".buff-row")].map((r) => {
    const [buff, level] = r.querySelectorAll("select");
    const param = r.querySelector("input[type=number]");
    return { buff: buff.value, level: level.value, levels: [...level.options].map((o) => o.value),
             param: r.querySelectorAll("label")[2].style.visibility === "hidden" ? null : param.value,
             paramTitle: r.querySelectorAll(".col-label")[2].textContent };
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
      const sel = document.querySelectorAll(".buff-row")[i].querySelectorAll("select")[1];
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
    await page.waitForFunction(() => [...document.querySelectorAll(".buff-row select")].some((s) => s.value === "Hitmaker"),
                               { timeout: 30000 });
    const hm = (await buffRows()).find((b) => b.buff === "Hitmaker");
    console.log("Senna Hitmaker row:", JSON.stringify(hm));
    if (hm.paramTitle !== "Is Big Shot" || hm.param !== "1") console.log("FAIL Hitmaker's Is Big Shot flag");
  } catch (e) {
    console.log("FAIL Hitmaker not preselected for Senna");
  }
  console.log("console errors:", errors.length ? errors : "none");
  await browser.close();
})();
