const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const { randomUUID } = require('node:crypto');
const code = fs.readFileSync(require('node:path').join(__dirname, '../assets/jmai-analytics.js'), 'utf8');

function browser({ url = 'https://www.japanmedai.com/weight/', storage = new Map(), referrer = '', automated = false, blockedStorage = false, response = { ok: true, status: 201 } } = {}) {
  const requests = [];
  let now = 1791248400000;
  const window = {
    location: new URL(url), document: { referrer, documentElement: { lang: 'zh-CN' } },
    navigator: { webdriver: automated, userAgent: 'Browser' }, crypto: { randomUUID },
    sessionStorage: {
      getItem(key) { if (blockedStorage) throw new Error('blocked'); return storage.get(key) || null; },
      setItem(key, value) { if (blockedStorage) throw new Error('blocked'); storage.set(key, value); }
    },
    fetch: async (url, init) => { requests.push({ url, init, body: JSON.parse(init.body) }); return response; }
  };
  vm.runInNewContext(code, { window, URL, URLSearchParams, Date: { now: () => now } });
  const create = () => window.JMAIAnalytics.create({ table: 'jw_weight_events', scope: 'weight', sessionKey: 'jmai_weight_sid_v1', pageVersion: 'v1-next-step-20261006' });
  return { create, requests, storage, advance: ms => { now += ms; } };
}

test('local, preview, QA and automated checks send no production rows', async () => {
  for (const config of [
    { url: 'http://127.0.0.1:8765/weight/' },
    { url: 'https://preview.vercel.app/weight/' },
    { url: 'https://www.japanmedai.com/weight/?jmai_qa=1' },
    { automated: true }
  ]) {
    const b = browser(config);
    await b.create().track('landing_view');
    assert.equal(b.requests.length, 0);
  }
  const storage = new Map();
  await browser({ url: 'https://www.japanmedai.com/weight/?jmai_qa=1', storage }).create().track('landing_view');
  const refresh = browser({ storage });
  await refresh.create().track('landing_view');
  assert.equal(refresh.requests.length, 0);
});

test('refresh preserves browser-tab session and first source; idle creates a new session', async () => {
  const b = browser({ url: 'https://www.japanmedai.com/weight/?utm_source=wechat&utm_campaign=v1_geo_01' });
  const a = b.create();
  await a.track('landing_view');
  const refresh = browser({ storage: b.storage });
  const a2 = refresh.create();
  await a2.track('result_viewed');
  assert.equal(a2.sessionId, a.sessionId);
  assert.equal(refresh.requests[0].body.source, 'wechat');
  const oldId = a2.sessionId;
  refresh.advance(31 * 60 * 1000);
  await a2.track('landing_view');
  assert.notEqual(a2.sessionId, oldId);
});

test('payload includes version and CTA, but excludes answers, summaries and referrer query', async () => {
  const b = browser({ referrer: 'https://www.threads.com/post/abc?private=do-not-store' });
  await b.create().track('next_step_clicked', { cta_id: 'plan_v1', cta_position: 'result_primary', diagnosis: 'private', summary: 'private', docs_count: 4, profile_type: 'private' });
  const { body, init } = b.requests[0];
  assert.equal(body.source, 'threads');
  assert.equal(body.event_data.page_version, 'v1-next-step-20261006');
  assert.equal(body.event_data.cta_id, 'plan_v1');
  assert.equal(body.referrer, 'https://www.threads.com');
  assert.equal(JSON.stringify(body).includes('private'), false);
  assert.equal(Object.hasOwn(init.headers, 'Authorization'), false);
});

test('blocked browser storage does not break the tool or UUID event insert', async () => {
  const b = browser({ blockedStorage: true });
  await b.create().track('quiz_started');
  assert.match(b.requests[0].body.session_id, /^[0-9a-f-]{36}$/i);
});

test('trackOnce deduplicates and permits retry after rejected writes', async () => {
  const b = browser();
  const a = b.create();
  await a.trackOnce('quiz_completed');
  await a.trackOnce('quiz_completed');
  assert.equal(b.requests.length, 1);
  const failed = browser({ response: { ok: false, status: 403 } });
  const af = failed.create();
  assert.equal((await af.trackOnce('result_viewed')).ok, false);
  await af.trackOnce('result_viewed');
  assert.equal(failed.requests.length, 2);
});
