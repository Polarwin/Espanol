const { chromium } = require(process.env.PLAYWRIGHT_MODULE || '/home/justin/tmp-reinforcement-browser/node_modules/playwright');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: process.env.CHROMIUM_PATH || '/home/justin/.cache/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-linux64/chrome-headless-shell' });
  try {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 }, offline: true });
    const page = await context.newPage();
    await page.goto('file:///srv/files/static/SpanishReading/dw-brasil-20261005/escuchar.html');
    assert.equal(await page.getByRole('heading', { name: 'Transcripción', exact: true }).isVisible(), false);
    assert.equal(await page.getByRole('link', { name: 'Respuestas orientativas', exact: true }).isVisible(), false);
    assert.equal(await page.locator('textarea').count(), 5);
    await page.waitForFunction(() => document.querySelector('audio')?.readyState >= 1);
    assert.ok(await page.locator('audio').evaluate(audio => audio.duration > 10));
    await page.locator('textarea').first().fill('Mi respuesta de escucha');
    await page.locator('summary').click();
    assert.equal(await page.getByRole('heading', { name: 'Transcripción', exact: true }).isVisible(), true);
    assert.equal(await page.locator('textarea').first().inputValue(), 'Mi respuesta de escucha');
    assert.equal(await page.getByRole('link', { name: 'Respuestas orientativas', exact: true }).isVisible(), true);
    console.log('PASS: offline listening page, real MP3 metadata, five questions, hidden transcript/help and explicit reveal.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1 });
