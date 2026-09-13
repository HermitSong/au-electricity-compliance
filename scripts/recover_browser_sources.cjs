/* Public browsing only: no user profile, credentials, stealth or challenge bypass. */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {createRequire} = require('node:module');

function option(name, fallback) {
  const index = process.argv.indexOf(name);
  return index < 0 ? fallback : process.argv[index + 1];
}
const root = path.resolve(option('--root', path.join(__dirname, '..')));
const runtime = option('--node-modules', process.env.NODE_PATH);
const {chromium} = runtime ? createRequire(path.join(path.resolve(runtime), '_loader.cjs'))('playwright') : require('playwright');
const logPath = path.join(root, 'source-originals', 'recovery-browser.jsonl');
const targets = JSON.parse(fs.readFileSync(path.join(root, 'data/source-recovery-targets.json'), 'utf8')).targets;
const previous = fs.existsSync(logPath) ? fs.readFileSync(logPath, 'utf8').trim().split('\n').filter(Boolean).map(JSON.parse) : [];
const retry = process.argv.includes('--retry-failed');
const done = new Set(previous.filter(row => !retry || row.recovery_status === 'captured').map(row => row.canonical_url));
const hostFilter = option('--host', '');
const excludeHost = option('--exclude-host', '');
const queue = targets.filter(row => row.route === 'browser' && !done.has(row.canonical_url)
  && new URL(row.canonical_url).hostname !== excludeHost
  && (!hostFilter || new URL(row.canonical_url).hostname === hostFilter));
const max = Number(option('--limit', '1000'));
queue.splice(max);

function object(data, suffix) {
  const buffer = Buffer.isBuffer(data) ? data : Buffer.from(data, 'utf8');
  const sha256 = crypto.createHash('sha256').update(buffer).digest('hex');
  const relative = `source-originals/objects/${sha256.slice(0, 2)}/${sha256}${suffix}`;
  const full = path.join(root, relative);
  fs.mkdirSync(path.dirname(full), {recursive: true});
  if (fs.existsSync(full)) {
    if (crypto.createHash('sha256').update(fs.readFileSync(full)).digest('hex') !== sha256) throw Error('Existing object hash mismatch');
  } else fs.writeFileSync(full, buffer, {flag: 'wx'});
  return {path: relative, sha256, size: buffer.length};
}

async function capture(browser, target) {
  const context = await browser.newContext({viewport: {width: 1440, height: 1000}, acceptDownloads: false});
  const page = await context.newPage();
  let lastResponse;
  page.on('response', response => {
    if (response.request().isNavigationRequest() && response.frame() === page.mainFrame()) lastResponse = response;
  });
  const started = new Date().toISOString();
  try {
    const initial = await page.goto(target.canonical_url, {waitUntil: 'domcontentloaded', timeout: 45000});
    if (initial && initial.status() < 400 && /application\/pdf/i.test(initial.headers()['content-type'] || '')) {
      const data = await initial.body();
      if (data.subarray(0, 5).toString() !== '%PDF-') throw Error('PDF response has no PDF signature');
      const pdf = object(data, '.pdf');
      const row = {...target.prior, capture_status: 'bytes-preserved', acquisition_method: 'browser-navigation-original-response',
        snapshot_path: pdf.path, sha256: pdf.sha256, size_bytes: pdf.size, content_type: 'application/pdf',
        response_url: initial.url(), status_code: initial.status(), retrieved_at: new Date().toISOString(),
        extraction_status: 'browser-pdf-needs-extraction', recovery_status: 'captured'};
      for (const key of ['reason', 'text_path', 'text_sha256', 'extraction_error']) delete row[key];
      return row;
    }
    await page.waitForFunction(() => {
      const containers = [...document.querySelectorAll('#main-content, main, article, [role="main"], #main-layout')];
      return containers.some(node => node.innerText.trim().length > 250 ||
        (node.innerText.trim().length > 40 && node.querySelector('a[href*=".pdf"]')));
    }, null, {timeout: 25000});
    await page.waitForTimeout(1500);
    const rendered = await page.evaluate(() => {
      const selectors = ['#main-content', 'main', 'article', '[role="main"]', '#main-layout'];
      const nodes = selectors.flatMap(selector => [...document.querySelectorAll(selector)].map(node => ({selector, node})));
      nodes.sort((a, b) => b.node.innerText.length - a.node.innerText.length);
      const chosen = nodes[0];
      return {url: location.href, title: document.title, selector: chosen?.selector,
        text: chosen?.node.innerText.trim() || '',
        links: [...(chosen?.node || document).querySelectorAll('a[href]')].map(a => ({url: a.href, label: a.innerText.trim()}))};
    });
    const attachmentIndex = rendered.text.length > 40 && rendered.links.some(link => /\.pdf(?:$|\?)/i.test(link.url));
    if ((!attachmentIndex && rendered.text.length < 250) || (lastResponse && lastResponse.status() >= 400)
      || /access denied|page not found|^404\b|just a moment|request rejected|^sign in|^log in/i.test(rendered.title)
      || /the requested page could not be found|the page you are looking for (?:could not|cannot|can't|couldn.t) be found/i.test(rendered.text)) {
      throw Error('No substantive source text, or access/error page');
    }
    const html = object(await page.content(), '.html');
    const text = object(JSON.stringify([{locator: `browser:${rendered.selector}`, text: rendered.text}], null, 2) + '\n', '.json');
    const row = {...target.prior, capture_status: 'browser-text-preserved', acquisition_method: 'browser-rendered-main-text',
      representation: 'browser-rendered-html-and-text-not-original-http-bytes', attempted_at: started,
      retrieved_at: new Date().toISOString(), response_url: rendered.url, title: rendered.title,
      snapshot_path: html.path, sha256: html.sha256, size_bytes: html.size,
      text_path: text.path, text_sha256: text.sha256, text_character_count: rendered.text.length,
      content_type: 'text/html', extraction_status: 'extracted-unreviewed', content_class: 'browser-rendered-main-text',
      links: rendered.links, browser_engine: 'playwright-chromium-clean-context',
      legal_review_status: 'not-reviewed', current_law_release: false, redistribution_status: 'not-cleared',
      browser_capture_provenance: {url: rendered.url, selector: rendered.selector, observed_characters: rendered.text.length}};
    if (rendered.text.length < 250) row.content_class = 'browser-attachment-index-needs-linked-originals';
    for (const key of ['reason', 'extraction_error', 'page_count', 'pages_without_text', 'extraction_revision', 'response_headers', 'status_code']) delete row[key];
    if (lastResponse) {
      row.status_code = lastResponse.status();
      try {
        const raw = object(await lastResponse.body(), '.html');
        row.raw_response_path = raw.path;
        row.raw_response_sha256 = raw.sha256;
        row.raw_response_url = lastResponse.url();
      } catch (error) { row.raw_response_error = String(error).slice(0, 300); }
    }
    try {
      const screenshot = object(await page.screenshot({fullPage: true, timeout: 20000}), '.png');
      row.screenshot_path = screenshot.path;
      row.screenshot_sha256 = screenshot.sha256;
    } catch (error) { row.screenshot_error = String(error).slice(0, 300); }
    return {...row, recovery_status: 'captured'};
  } catch (error) {
    return {canonical_url: target.canonical_url, recovery_status: 'failed', attempted_at: started,
      response_url: page.url(), reason: String(error).slice(0, 700)};
  } finally { await context.close(); }
}

(async () => {
  console.log(JSON.stringify({queued: queue.length, mode: 'clean-public-browser'}));
  const browser = await chromium.launch({executablePath: option('--executable', undefined), headless: true});
  const busy = new Set();
  let completed = 0;
  async function worker() {
    while (queue.length) {
      const index = queue.findIndex(row => !busy.has(new URL(row.canonical_url).hostname));
      if (index < 0) { await new Promise(resolve => setTimeout(resolve, 300)); continue; }
      const target = queue.splice(index, 1)[0];
      const host = new URL(target.canonical_url).hostname;
      busy.add(host);
      try {
        const row = await capture(browser, target);
        fs.appendFileSync(logPath, JSON.stringify(row).replace(/[\u007f-\uffff]/g, c => '\\u' + c.charCodeAt(0).toString(16).padStart(4, '0')) + '\n');
        console.log(JSON.stringify({completed: ++completed, remaining: queue.length, status: row.recovery_status, url: row.canonical_url, reason: row.reason}));
        await new Promise(resolve => setTimeout(resolve, 1000));
      } finally { busy.delete(host); }
    }
  }
  try { await Promise.all(Array.from({length: 3}, () => worker())); }
  finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
