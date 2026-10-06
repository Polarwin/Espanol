// Run: node tools/test_reading_ui.cjs (uses this host's installed Playwright).
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || '/home/justin/tmp-reinforcement-browser/node_modules/playwright');
const assert = require('node:assert/strict');

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: process.env.CHROMIUM_PATH || '/home/justin/.cache/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-linux64/chrome-headless-shell' });
  try {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    let saved = {};
    let job = null;
    let audioFailure = false;
    const pack = { title: 'Una visita al mercado', reading: 'María visita el mercado de su barrio. Compra fruta y habla con los vendedores.', translation: 'Mary visits the market in her neighbourhood.', review_status: 'draft', start: 0, duration: 180,
      questions: Array.from({ length: 5 }, (_, i) => ({ question: `¿Qué hace María? ${i + 1}`, suggested_answer: 'María compra fruta.' })),
      vocabulary: Array.from({ length: 8 }, (_, i) => ({ term: `palabra ${i}`, spanish: 'Una explicación sencilla en español.', english: 'A simple explanation in English.' })) };
    await page.addInitScript(() => { localStorage.setItem('vamos.token', 'ui-test'); localStorage.setItem('vamos.placement-completed', 'true'); });
    await page.route('**/api/**', async route => {
      const path = new URL(route.request().url()).pathname;
      if (path.endsWith('/audio')) {
        assert.equal(route.request().headers().authorization, 'Bearer ui-test');
        if (audioFailure) return route.fulfill({ status: 404, json: { detail: 'Removed audio' } });
        // Valid short PCM WAV: test real browser decoding without model work.
        const wav = Buffer.alloc(44 + 16000);
        wav.write('RIFF'); wav.writeUInt32LE(wav.length - 8, 4); wav.write('WAVEfmt ', 8);
        wav.writeUInt32LE(16, 16); wav.writeUInt16LE(1, 20); wav.writeUInt16LE(1, 22);
        wav.writeUInt32LE(8000, 24); wav.writeUInt32LE(16000, 28); wav.writeUInt16LE(2, 32);
        wav.writeUInt16LE(16, 34); wav.write('data', 36); wav.writeUInt32LE(16000, 40);
        return route.fulfill({ contentType: 'audio/wav', body: wav });
      }
      let body = {};
      if (path === '/api/reading' && route.request().method() === 'POST') {
        job = { id: 'fixture', status: 'running', stage: 'Creando la lectura', source: 'news', source_title: 'Noticias de prueba', level: 'A2', answers: saved, pack: null };
        body = job;
      } else if (path === '/api/reading') body = job ? [job] : [];
      else if (path === '/api/reading/fixture/answers') {
        saved = route.request().postDataJSON().answers;
        body = { ...job, answers: saved };
      } else if (path === '/api/reading/fixture') { job = { ...job, status: 'ready', pack, answers: saved }; body = job; }
      await route.fulfill({ json: body });
    });
    await page.goto('http://127.0.0.1:5173/practica/lectura');
    await page.getByRole('button', { name: 'Crear una lectura sorpresa' }).click();
    await page.getByRole('heading', { name: pack.title }).waitFor();
    assert.equal(await page.locator('textarea').count(), 5);
    assert.equal(await page.getByText(pack.reading, { exact: true }).count(), 0);
    assert.equal(await page.getByRole('heading', { name: 'Palabras para llevarte' }).count(), 0);
    assert.equal(await page.getByRole('button', { name: 'Respuestas orientativas', exact: true }).count(), 0);
    await page.getByRole('button', { name: 'Cargar audio' }).click();
    await page.waitForFunction(() => document.querySelector('audio')?.readyState >= 1);
    await page.getByLabel('Velocidad del audio').selectOption('0.75');
    assert.equal(await page.locator('audio').evaluate(el => el.playbackRate), 0.75);
    await page.getByRole('button', { name: 'Escuchar otra vez' }).click();
    await page.waitForFunction(() => !document.querySelector('audio').paused);
    assert.equal(await page.getByText(pack.translation, { exact: true }).count(), 0);
    assert.equal(await page.getByText('Ejemplo: María compra fruta.', { exact: true }).count(), 0);
    await page.locator('textarea').first().fill('Compra fruta.');
    await page.getByRole('button', { name: 'Guardar mis respuestas' }).click();
    await page.getByText('Guardadas', { exact: true }).waitFor();
    assert.equal(saved['0'], 'Compra fruta.');
    await page.getByRole('button', { name: 'Mostrar transcripción y ayudas' }).click();
    await page.getByText(pack.reading, { exact: true }).waitFor();
    assert.equal(await page.locator('textarea').first().inputValue(), 'Compra fruta.');
    await page.getByRole('button', { name: 'English translation', exact: true }).click();
    await page.getByText(pack.translation, { exact: true }).waitFor();
    assert.equal(await page.locator('textarea').count(), 0);
    await page.getByRole('button', { name: 'Respuestas orientativas', exact: true }).click();
    assert.equal(await page.getByText('Ejemplo: María compra fruta.', { exact: true }).count(), 5);
    await page.reload();
    await page.locator('textarea').first().waitFor();
    assert.equal(await page.locator('textarea').first().inputValue(), 'Compra fruta.');
    assert.equal(await page.getByText(pack.reading, { exact: true }).count(), 0);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    await page.setViewportSize({ width: 320, height: 700 });
    audioFailure = true;
    await page.getByRole('button', { name: 'Cargar audio' }).click();
    await page.getByText('Este audio ya no está disponible.', { exact: false }).waitFor();
    assert.equal(await page.getByText(pack.reading, { exact: true }).count(), 0);
    audioFailure = false;
    await page.getByRole('button', { name: 'Cargar audio' }).click();
    await page.waitForFunction(() => document.querySelector('audio')?.readyState >= 1);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    assert.deepEqual(errors, []);
    if (process.env.SCREENSHOT_PATH) await page.screenshot({ path: process.env.SCREENSHOT_PATH, fullPage: true });
    console.log('PASS: mobile flow, background polling, open questions, bilingual vocabulary, separate supplements, saved answers after reload.');
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
