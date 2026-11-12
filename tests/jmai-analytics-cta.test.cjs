// Offline integration checks: never call the real Supabase API or write production events.
// Run: node --test tests/jmai-analytics-cta.test.cjs
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const script = fs.readFileSync(path.join(__dirname, '../assets/jmai-analytics.js'), 'utf8');

function browser(storage, pathname, options = {}) {
  const sent = [];
  const listeners = new Map();
  const document = {
    referrer: options.referrer || '',
    readyState: 'loading',
    documentElement: { lang: 'zh-CN' },
    addEventListener(type, fn) {
      if (!listeners.has(type)) listeners.set(type, []);
      listeners.get(type).push(fn);
    },
  };
  const location = {
    origin: 'https://www.japanmedai.com',
    hostname: options.hostname || 'www.japanmedai.com',
    search: options.search || '',
    pathname
  };
  let count = 0;
  const w = {
    location,
    document,
    sessionStorage: {
      getItem(k) { return storage.has(k) ? storage.get(k) : null; },
      setItem(k, v) { storage.set(k, String(v)); }
    },
    navigator: { userAgent: 'Mozilla/5.0', webdriver: false },
    crypto: { randomUUID() { return '00000000-0000-4000-8000-' + String(++count).padStart(12, '0'); } },
    fetch(_url, init) {
      sent.push(JSON.parse(init.body));
      return Promise.resolve({ ok: true, status: 201 });
    }
  };
  const context = { window: w, document, location, URL, URLSearchParams, Date, Math, Promise, Set, JSON };
  vm.runInNewContext(script, context, { filename: 'jmai-analytics.js' });
  return {
    sent, w,
    async click(pathname, attrs = {}) {
      const link = {
        origin: location.origin, pathname,
        hasAttribute(k) { return Object.prototype.hasOwnProperty.call(attrs, k); },
        getAttribute(k) { return attrs[k] || null; },
        closest(selector) { return selector === '.a2Module' ? null : this; }
      };
      const event = { target: { closest(s) { return s === 'a' ? link : null; } } };
      for (const listener of listeners.get('click') || []) listener(event);
      await new Promise(setImmediate);
    }
  };
}

test('unannotated service and records CTAs emit fixed-schema anonymous events', async () => {
  const b = browser(new Map(), '/bnct/049/');
  await b.click('/second-opinion/');
  await b.click('/tools/second-opinion-records/');
  assert.equal(b.sent.length, 2);
  assert.deepEqual(b.sent.map(x => x.event_name), ['internal_link_click', 'internal_link_click']);
  assert.deepEqual(b.sent.map(x => x.event_data.kind), ['second_opinion_service', 'second_opinion_records']);
  assert.ok(b.sent.every(x => x.page_path === '/bnct/049/'));
  assert.ok(b.sent.every(x => !Object.prototype.hasOwnProperty.call(x, 'patient')));
});

test('unrelated link is never tracked', async () => {
  const b = browser(new Map(), '/bnct/049/');
  await b.click('/bnct/010/');
  assert.equal(b.sent.length, 0);
});

test('annotated CTA keeps its declared kind and identifiers without duplicate sends', async () => {
  const b = browser(new Map(), '/checkup/006/');
  await b.click('/second-opinion/', {
    'data-jmai-track': 'decision',
    'data-jmai-id': 's30_checkup_006',
    'data-jmai-position': 'decision'
  });
  assert.equal(b.sent.length, 1);
  assert.equal(b.sent[0].event_data.kind, 'decision');
  assert.equal(b.sent[0].event_data.cta_id, 's30_checkup_006');
});

test('separate pages share anonymous session ID and original first-touch attribution', async () => {
  const storage = new Map();
  const first = browser(storage, '/bnct/024/', {
    search: '?utm_source=facebook&utm_campaign=bnct',
    referrer: 'https://www.facebook.com/'
  });
  await first.w.JMAIAnalytics.create({ table: 'jmai_site_events', scope: 'site' }).track('landing_view');
  const second = browser(storage, '/second-opinion/', { referrer: 'https://www.japanmedai.com/bnct/024/' });
  await second.w.JMAIAnalytics.create({ table: 'jmai_second_opinion_events', scope: 'second_opinion' }).track('landing_view');
  assert.equal(first.sent[0].session_id, second.sent[0].session_id);
  assert.equal(second.sent[0].source, 'facebook');
});

test('QA and preview traffic cannot write production events', async () => {
  const qa = browser(new Map(), '/', { search: '?jmai_qa=1' });
  const preview = browser(new Map(), '/', { hostname: 'preview.example.com' });
  await qa.click('/second-opinion/');
  await preview.click('/second-opinion/');
  assert.equal(qa.sent.length, 0);
  assert.equal(preview.sent.length, 0);
});
