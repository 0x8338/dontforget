const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const site = path.join(__dirname, '..', 'site');

async function render(page, routes, now = '2026-09-21T00:00:00Z') {
  const elements = new Map();
  const requests = [];
  const chips = ['all', 'kept', 'broken', 'partial', 'pending'].map(filter => ({
    dataset: { filter },
    classList: { add() {}, remove() {} },
    addEventListener(event, callback) { this.click = callback; }
  }));
  const getElementById = id => {
    if (!elements.has(id)) elements.set(id, { innerHTML: '', textContent: '', hidden: true });
    return elements.get(id);
  };
  class Clock extends Date {
    constructor(...args) { super(...(args.length ? args : [now])); }
  }
  const context = vm.createContext({
    Date: Clock, URL, URLSearchParams,
    window: { location: { search: '?date=09-21' } },
    document: { getElementById, querySelectorAll: () => chips },
    fetch: async url => {
      requests.push(url);
      if (!(url in routes)) throw new Error('Unexpected request: ' + url);
      const value = routes[url];
      if (value instanceof Error) throw value;
      return { ok: value !== null, json: async () => value };
    }
  });
  vm.runInContext(fs.readFileSync(path.join(site, 'assets/data.js'), 'utf8'), context);
  const html = fs.readFileSync(path.join(site, page), 'utf8');
  vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1], context);
  await new Promise(resolve => setImmediate(resolve));
  return { get: getElementById, requests, chips, data: context.DontforgetData };
}

function promise(overrides = {}) {
  return { person: 'Example', role: 'Organization', promise: 'A commitment',
    due_date: '2026-09-20', status: 'kept', description: 'Evidence summary',
    sources: ['Public record'], source_urls: ['https://example.org/evidence'], ...overrides };
}

test('counts use the current UTC date and include delayed fulfillment as kept', async () => {
  const page = await render('promises/index.html', {
    '../_data/promises/index.json': { due_total: 0, due_status: {}, months: [
      { key: '2026-10', file: 'promises/2026-10.json', due: false },
      { key: '2026-09', file: 'promises/2026-09.json', due: false }
    ] },
    '../_data/promises/2026-09.json': [
      promise({ status: 'kept (delayed)' }), promise({ status: 'pending' }),
      promise({ due_date: '2026-09-22' })
    ]
  });
  assert.equal(page.get('promise-count').textContent, 2);
  assert.equal(page.get('stat-kept').textContent, 1);
  assert.equal(page.get('stat-pending').textContent, 1);
  assert.equal(page.requests.length, 2);
  assert.doesNotMatch(page.get('promises-container').innerHTML, /undefined/);
  page.chips.find(chip => chip.dataset.filter === 'kept').click();
  assert.match(page.get('promises-container').innerHTML, /kept \(delayed\)/);
  assert.equal((page.get('promises-container').innerHTML.match(/<article /g) || []).length, 1);
});

test('a new month loads without rebuilding the manifest', async () => {
  const page = await render('promises/index.html', {
    '../_data/promises/index.json': { months: [
      { key: '2026-10', file: 'promises/2026-10.json', due: false }
    ] },
    '../_data/promises/2026-10.json': [promise({ due_date: '2026-10-01' })]
  }, '2026-10-01T00:00:00Z');
  assert.equal(page.get('promise-count').textContent, 1);
});

test('a failed promise chunk does not hide subsequent months', async () => {
  const page = await render('promises/index.html', {
    '../_data/promises/index.json': { months: [
      { key: '2026-09', file: 'promises/2026-09.json' },
      { key: '2026-08', file: 'promises/2026-08.json' }
    ] },
    '../_data/promises/2026-09.json': null,
    '../_data/promises/2026-08.json': [promise({ due_date: '2026-08-01' })]
  });
  assert.equal(page.get('promise-count').textContent, 1);
  assert.equal(page.get('load-error').hidden, false);
  assert.match(page.get('load-error').textContent, /incomplete/);
});

test('empty due-month lists produce zero counts', async () => {
  const page = await render('promises/index.html', {
    '../_data/promises/index.json': { months: [] }
  });
  assert.equal(page.get('promise-count').textContent, 0);
  assert.equal(page.get('stat-kept').textContent, 0);
});

test('review notes do not hide collected promises or alter their status', async () => {
  const page = await render('promises/index.html', {
    '../_data/promises/index.json': { months: [{ key: '2026-09', file: 'promises/2026-09.json' }] },
    '../_data/promises/2026-09.json': [promise({ status: 'broken', source_urls: undefined,
      review: { as_of: '2026-09-21', fields: ['date_promised'], note: 'Date <not established>',
        sources: [{ name: 'Review source', url: 'https://example.org/review' }] } })]
  });
  assert.equal(page.get('promise-count').textContent, 1);
  assert.equal(page.get('stat-broken').textContent, 1);
  page.chips.find(chip => chip.dataset.filter === 'broken').click();
  assert.match(page.get('promises-container').innerHTML, /Details under review/);
  assert.match(page.get('promises-container').innerHTML, /Date &lt;not established&gt;/);
  assert.match(page.get('promises-container').innerHTML, /https:\/\/example.org\/review/);
});

test('source links and record text are escaped; unsafe URLs are not linked', async () => {
  const page = await render('promises/index.html', {
    '../_data/promises/index.json': { months: [
      { key: '2026-09', file: 'promises/2026-09.json' }
    ] },
    '../_data/promises/2026-09.json': [promise({ promise: '<script>unsafe</script>',
      evidence: ['Outcome evidence <checked>', 'Second finding'] })]
  });
  const html = page.get('promises-container').innerHTML;
  assert.match(html, /&lt;script&gt;unsafe/);
  assert.match(html, /Outcome evidence &lt;checked&gt;/);
  assert.match(html, /<p>Second finding<\/p>/);
  assert.match(html, /href="https:\/\/example.org\/evidence"/);
  assert.equal(page.data.sourcesHtml({ sources: ['<source>'], source_urls: ['javascript:alert(1)'] }), '&lt;source&gt;');
});

test('events continue after a failed window and display source links', async () => {
  const page = await render('index.html', {
    '_data/events/index.json': { windows: [
      { file: 'events/2025-2026.json', days: { '09-21': 1 } },
      { file: 'events/2020-2024.json', days: { '09-21': 1 } }
    ] },
    '_data/events/2025-2026.json': new Error('Network failure'),
    '_data/events/2020-2024.json': [{ date: '2020-09-21', title: '<Event>',
      location: 'Location', category: 'industrial', lives_lost: 2,
      description: 'A record.', sources: ['Public record'], source_urls: ['https://example.org/event'] }]
  });
  assert.equal(page.get('load-error').hidden, false);
  assert.match(page.get('events-container').innerHTML, /&lt;Event&gt;/);
  assert.match(page.get('events-container').innerHTML, /href="https:\/\/example.org\/event"/);
  assert.equal(page.get('lives-total').textContent, '~2');
});

test('a retracted fatality stays visible without adding to the death count', async () => {
  const page = await render('index.html', {
    '_data/events/index.json': { windows: [
      { file: 'events/2025-2026.json', days: { '09-21': 2 } }
    ] },
    '_data/events/2025-2026.json': [0, 2].map(lives_lost => ({
      date: '2026-09-21', title: lives_lost ? 'Another event' : 'Corrected report',
      location: 'Location', category: 'industrial', lives_lost,
      description: 'Evidence summary', sources: ['Source A']
    }))
  });
  assert.equal(page.get('lives-total').textContent, '~2');
  assert.match(page.get('events-container').innerHTML, /Corrected report/);
  assert.match(page.get('events-container').innerHTML, /Fatality report corrected/);
  assert.equal((page.get('events-container').innerHTML.match(/<article /g) || []).length, 2);
});
