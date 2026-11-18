// The fight viewer (viz.js): loads the page, waits for the viewer to draw the default row's fight, clicks another
// row, scrubs and plays, and saves screenshots. Reports the viewer's state and any console errors.
//     python serve.py 8619   (another shell), then: node viz_e2e.js [url] [champion] [screenshot dir]
const puppeteer = require("puppeteer-core");
const path = require("path");

(async () => {
  const url = process.argv[2] || "http://127.0.0.1:8619/";
  const champ = process.argv[3] || null;
  const out = process.argv[4] || ".";
  const browser = await puppeteer.launch({
    executablePath: process.env.EDGE || "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    headless: true,
    args: ["--no-first-run"],
    defaultViewport: { width: 1900, height: 1250 },
  });
  const page = await browser.newPage();
  const errors = [];
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  page.on("pageerror", (e) => errors.push("pageerror: " + e.message));
  await page.goto(url, { waitUntil: "load" });
  await page.waitForFunction(() => document.querySelectorAll("#resultsTable tr").length > 1, { timeout: 120000 });
  if (champ) {
    await page.evaluate((c) => {
      const sel = document.querySelector("#champ");
      sel.value = c;
      sel.dispatchEvent(new Event("change"));
    }, champ);
    await page.waitForFunction((c) => document.querySelector("#headerChamp").textContent.startsWith(c), { timeout: 60000 }, champ);
    await page.waitForFunction(() => document.querySelectorAll("#resultsTable tr").length > 1, { timeout: 120000 });
  }
  const viewer = () => page.evaluate(() => ({
    what: document.querySelector("#vizWhat").textContent,
    status: document.querySelector("#vizStatus").hidden ? "" : document.querySelector("#vizStatus").textContent,
    time: document.querySelector("#vizTime").textContent,
    card: document.querySelector("#vizCard").innerText.split("\n").slice(0, 12).join(" | "),
    log: [...document.querySelectorAll("#vizLog div")].slice(0, 3).map((d) => d.innerText),
    viewing: (document.querySelector("#resultsTable tr.viewing") || {}).innerText,
  }));
  await page.waitForFunction(() => document.querySelector("#vizTime").textContent.includes("tick"), { timeout: 60000 });
  console.log("default:", JSON.stringify(await viewer(), null, 1));

  // the second row: the viewer follows it
  await page.evaluate(() => document.querySelectorAll("#resultsTable tbody tr")[0].click());
  await page.waitForFunction(() => !document.querySelector("#vizWhat").textContent.endsWith("NoItem"), { timeout: 60000 });
  await page.waitForFunction(() => document.querySelector("#vizStatus").hidden, { timeout: 60000 });
  // scrub to 9.5 s on the strip, then step a tick
  await page.evaluate(() => {
    const strip = document.querySelector("#vizStrip");
    const r = strip.getBoundingClientRect();
    const x = r.left + r.width * (9.5 / 30);
    strip.dispatchEvent(new PointerEvent("pointerdown", { clientX: x, clientY: r.top + 10, pointerId: 1, bubbles: true }));
    strip.dispatchEvent(new PointerEvent("pointerup", { clientX: x, clientY: r.top + 10, pointerId: 1, bubbles: true }));
  });
  console.log("row 1 at 9.5 s:", JSON.stringify(await viewer(), null, 1));
  const viz = await page.$("#viz");
  await viz.screenshot({ path: path.join(out, "viz_scrub.png") });
  // play a moment
  await page.click("#vizPlay");
  await new Promise((r) => setTimeout(r, 1300));
  await page.click("#vizPlay");
  console.log("after playing:", (await viewer()).time);
  await viz.screenshot({ path: path.join(out, "viz_play.png") });
  await page.screenshot({ path: path.join(out, "viz_page.png") });
  console.log("errors:", errors.length ? errors : "none");
  await browser.close();
})();
