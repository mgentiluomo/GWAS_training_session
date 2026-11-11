// Authoring QA: requires Playwright and a compatible Chromium executable.
// TUTORIAL_BROWSER can select the executable; no dependency is needed to read the tutorial.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const { pathToFileURL } = require('node:url');
const path = require('node:path');

(async () => {
  const browser = await chromium.launch({
    ...(process.env.TUTORIAL_BROWSER ? { executablePath: process.env.TUTORIAL_BROWSER } : {}),
    headless: true,
    args: ['--no-sandbox', '--single-process', '--no-zygote', '--disable-gpu']
  });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    await page.emulateMedia({ reducedMotion: 'reduce' });
    page.setDefaultTimeout(5000);
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    const url = pathToFileURL(path.resolve(__dirname, '../tutorial/index.html')).href;
    await page.goto(url + '#home');
    assert.doesNotMatch(await page.locator('.topbar').innerText(), /Omics|552EE/i);
    assert.doesNotMatch(await page.locator('.rail').innerText(), /Omics|552EE/i);
    assert.equal((await page.locator('#home').innerText()).split('Omics: Biotechnology and AI for Health').length - 1, 1);
    assert.match(await page.locator('#home').innerText(), /independent teaching materials/i);
    await page.goto(url + '#setup');
    await page.locator('#reset-progress').click();
    await page.locator('[data-os=mac]').click();
    assert(await page.locator('[data-os-panel=mac]').isVisible());
    assert(!(await page.locator('[data-os-panel=windows]').isVisible()));
    await page.locator('[data-progress=ready-project]').check();
    await page.reload();
    assert(await page.locator('[data-progress=ready-project]').isChecked());
    await page.locator('.copy-button').first().click();
    await page.locator('#toast').waitFor({ state: 'visible' });
    await page.goto(url + '#qc-missing');
    assert.equal(await page.locator('#retained-count').innerText(), '594');
    await page.locator('#missingness-threshold').fill('25');
    assert.equal(await page.locator('#retained-count').innerText(), '600');
    await page.locator('input[value=a]').check();
    await page.locator('[data-quiz] button').click();
    assert.match(await page.locator('.feedback').innerText(), /^Yes\./);
    await page.goto(url + '#practice');
    await page.locator('#practice summary').first().click();
    assert.notEqual(await page.locator('#practice details').first().getAttribute('open'), null);
    await page.goto(url + '#downloads');
    assert.equal(await page.locator('.package').count(), 6);
    for (const width of [390, 768, 1440]) {
      await page.setViewportSize({ width, height: 900 });
      await page.goto(url + '#home');
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth), width);
      if (process.env.TUTORIAL_SCREENSHOTS) {
        await page.screenshot({ path: path.join(process.env.TUTORIAL_SCREENSHOTS, `tutorial-${width}.png`), fullPage: false });
      }
    }
    await page.setViewportSize({ width: 390, height: 900 });
    await page.locator('.menu-button').click();
    assert(await page.locator('.rail').isVisible());
    await page.locator('.rail a[href="#setup"]').click();
    assert(!(await page.locator('.rail').isVisible()));
    await page.locator('#setup').waitFor({ state: 'visible' });
    assert.deepEqual(errors, []);
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.goto(url + '#qc-filter');
    if (process.env.TUTORIAL_SCREENSHOTS) {
      await page.screenshot({ path: path.join(process.env.TUTORIAL_SCREENSHOTS, 'tutorial-qc.png'), fullPage: false });
    }
    const cdp = await page.context().newCDPSession(page);
    await cdp.send('Emulation.setScriptExecutionDisabled', { value: true });
    await page.goto(url);
    await page.reload();
    assert.equal(await page.locator('article.page:visible').count(), 7);
    assert.equal(await page.locator('form').count(), 0);
    assert.equal(await page.locator('[data-os-panel]:visible').count(), 3);
    console.log('PASS: navigation, OS panels, copy fallback, checklist persistence, slider, quiz, worked explanations, six downloads, mobile menu, widths 390/768/1440 and no-JS reading.');
  } finally {
    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
