/* Read-only 4-page real-Chrome render and internal-CTA smoke test. */
import { chromium } from "playwright-core";
import fs from "node:fs/promises";
import path from "node:path";

const origin = "https://www.japanmedai.com";
const ids = ["001", "008", "034", "050"];
const modes = [
  {name:"desktop", width:1280, height:800, mobile:false},
  {name:"mobile", width:390, height:844, mobile:true},
];
const output = "weight-browser-qa";
await fs.mkdir(output, {recursive:true});
const browser = await chromium.launch({
  headless: true,
  executablePath: process.env.CHROME_BIN || "/usr/bin/google-chrome",
  args: ["--no-sandbox", "--disable-dev-shm-usage"],
});
let failed = false;
const rows = [];
for (const id of ids) {
  for (const mode of modes) {
    const context = await browser.newContext({
      viewport:{width:mode.width,height:mode.height},
      deviceScaleFactor:1,
      isMobile:mode.mobile,
    });
    const page = await context.newPage();
    const url = `${origin}/weight/articles/article-${id}.html`;
    const row = {article:id, viewport:mode.name, width:mode.width, checks:[], screenshot:null};
    try {
      const response = await page.goto(url,{waitUntil:"domcontentloaded",timeout:30000});
      row.http=response?.status();
      if (row.http !== 200) throw new Error(`HTTP ${row.http}`);
      await page.evaluate(() => document.fonts.ready);
      await page.waitForTimeout(150);
      const layout=await page.evaluate(()=>{
        const root=document.documentElement;
        const anchors=[...document.querySelectorAll("a[href*='utm_campaign=weight_library']")];
        return {
          pageTitle:document.title,
          pageH1:document.querySelector("h1")?.textContent?.trim() || "",
          scrollWidth:root.scrollWidth,
          viewportWidth:root.clientWidth,
          anchors:anchors.length,
          canonical:document.querySelector('link[rel="canonical"]')?.href || ""
        };
      });
      row.layout=layout;
      if (!layout.pageH1 || !layout.pageTitle) throw new Error("Missing title/H1");
      if (layout.canonical!==url) throw new Error("Canonical mismatch");
      if (layout.scrollWidth>layout.viewportWidth+2) throw new Error(`Horizontal overflow ${layout.scrollWidth}>${layout.viewportWidth}`);
      if (layout.anchors!==1) throw new Error(`CTA count ${layout.anchors}`);
      const screenshot=path.join(output,`article-${id}-${mode.name}.png`);
      await page.screenshot({path:screenshot,fullPage:true,animations:"disabled"});
      row.screenshot=screenshot;
      const cta=page.locator("a[href*='utm_campaign=weight_library']").first();
      await Promise.all([
        page.waitForURL(/\/weight\/(\?|$)/,{timeout:20000}),
        cta.click({timeout:10000}),
      ]);
      row.ctaFinalUrl=page.url();
      const parsed=new URL(page.url());
      if(parsed.origin!==origin || parsed.pathname!=="/weight/") throw new Error("CTA wrong destination");
      row.checks.push("HTTP 200","title+H1","canonical","no horizontal overflow","CTA link count=1","CTA click reaches /weight/","screenshot saved");
    } catch(e) {
      failed=true;
      row.failure=String(e);
    } finally {
      rows.push(row);
      await context.close();
    }
  }
}
await browser.close();
await fs.writeFile(path.join(output,"report.json"),JSON.stringify({date:"2026-10-29",sourceCommit:"b66c42de75c3a950be3b4b9159d6bd2650f2188a",checks:rows,passed:rows.filter(x=>!x.failure).length,failed:rows.filter(x=>x.failure).length},null,2));
console.log(JSON.stringify({tested:rows.length,passed:rows.filter(x=>!x.failure).length,failed:rows.filter(x=>x.failure).map(x=>({article:x.article,viewport:x.viewport,error:x.failure})),screenshots:rows.filter(x=>x.screenshot).map(x=>x.screenshot)},null,2));
if(process.env.GITHUB_STEP_SUMMARY){
  let s="## Weight 50 | Chrome 4-page visual + CTA smoke test\n\n";
  s+="Production source: `b66c42de`. Automated checks do not replace human screenshot review.\n\n";
  s+="| Article | Viewport | HTTP | Overflow | CTA click | Screenshot |\n|---|---|---|---|---|---|\n";
  for(const r of rows) s+=`| ${r.article} | ${r.viewport} | ${r.http??"N/A"} | ${r.layout?.scrollWidth??"?"}/${r.layout?.viewportWidth??"?"} | ${r.failure ? "FAIL":"PASS"} | ${r.screenshot??"not saved"} |\n`;
  s+="\n" + (failed ? "**AUTOMATED CHECK FAILED**":"**AUTOMATED CHECK PASSED**") + "\n";
  await fs.appendFile(process.env.GITHUB_STEP_SUMMARY,s);
}
if(failed)process.exitCode=1;
