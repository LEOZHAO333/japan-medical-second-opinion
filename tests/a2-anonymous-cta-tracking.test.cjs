"use strict";
// Run with: node --test tests/a2-anonymous-cta-tracking.test.cjs
// Uses a fake DOM and a fake analytics sink. No network or production data writes.
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const original = fs.readFileSync(path.join(__dirname, "../assets/jmai-analytics.js"), "utf8");
const marker = "/* JMAI_INTERNAL_LINK_TRACKING_V2";
const start = original.indexOf(marker);
assert.ok(start >= 0, "A2 tracking module must be present");
const isolatedModule = original.slice(start);

function fixture() {
  const events = [];
  let click;
  const window = {
    location: { origin: "https://www.japanmedai.com" },
    JMAIAnalytics: {
      create(options) {
        return {
          track(name, metadata) {
            // Cross-realm objects are copied for deterministic assertions.
            events.push(JSON.parse(JSON.stringify({ name, metadata, options })));
          }
        };
      }
    }
  };
  const document = {
    addEventListener(type, callback, options) {
      if (type === "click") {
        click = callback;
        assert.equal(options.passive, true);
      }
    }
  };
  vm.runInNewContext(isolatedModule, { window, document }, { filename: "jmai-analytics-A2.js" });
  assert.equal(typeof click, "function");
  function link(href, { inA2 = false, attributes = {} } = {}) {
    const target = new URL(href, window.location.origin);
    return {
      origin: target.origin,
      pathname: target.pathname,
      hasAttribute(name) { return Object.hasOwn(attributes, name); },
      getAttribute(name) {
        return name === "href" ? href : (Object.hasOwn(attributes, name) ? attributes[name] : null);
      },
      closest(selector) { return selector === ".a2Module" && inA2 ? { className: "a2Module" } : null; }
    };
  }
  function emit(anchor) {
    click({ target: { closest(selector) { return selector === "a" ? anchor : null; } } });
  }
  return { events, link, emit };
}

test("A2 checklist CTA creates one anonymous event on existing unannotated pages", () => {
  const f = fixture();
  f.emit(f.link("/tools/second-opinion-records/", { inA2: true }));
  assert.equal(f.events.length, 1);
  assert.deepEqual(f.events[0], {
    name: "internal_link_click",
    metadata: { kind: "second_opinion_records", cta_id: "a2_records_primary", cta_position: "article_footer" },
    options: { table: "jmai_site_events", scope: "site", pageVersion: "topic-cluster-v2" }
  });
});

test("ordinary checklist link outside A2 is not misattributed", () => {
  const f = fixture();
  f.emit(f.link("/tools/second-opinion-records/"));
  assert.equal(f.events.length, 0);
});

test("the A2 informational CTA does not count as the checklist CTA", () => {
  const f = fixture();
  f.emit(f.link("/second-opinion/", { inA2: true }));
  assert.equal(f.events.length, 0);
});

test("external link with matching pathname is not mistaken for internal CTA", () => {
  const f = fixture();
  f.emit(f.link("https://example.org/tools/second-opinion-records/", { inA2: true }));
  assert.equal(f.events.length, 0);
});

test("legacy explicitly annotated links continue to be tracked", () => {
  const f = fixture();
  f.emit(f.link("/guide/047/", {
    attributes: { "data-jmai-track": "topic_next", "data-jmai-id": "guide_related", "data-jmai-position": "body" }
  }));
  assert.equal(f.events.length, 1);
  assert.deepEqual(f.events[0].metadata, {
    kind: "topic_next", cta_id: "guide_related", cta_position: "body"
  });
});

test("future A2 markup with an explicit tracking tag still emits exactly one event", () => {
  const f = fixture();
  f.emit(f.link("/tools/second-opinion-records/", {
    inA2: true,
    attributes: { "data-jmai-track": "second_opinion_records", "data-jmai-id": "a2_records_primary", "data-jmai-position": "article_footer" }
  }));
  assert.equal(f.events.length, 1);
});

test("click handler ignores non-anchor targets and does not send form answers", () => {
  const f = fixture();
  f.emit(null);
  assert.equal(f.events.length, 0);
});
