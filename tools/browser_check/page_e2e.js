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
  console.log("after", Math.round((Date.now() - t0) / 1000), "s:", JSON.stringify(await read(), null, 1));
  console.log("console errors:", errors.length ? errors : "none");
  await browser.close();
})();
