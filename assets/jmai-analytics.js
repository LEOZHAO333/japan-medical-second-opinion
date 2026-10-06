(function (w) {
  "use strict";
  const API = "https://pcuofvwabfjoumjahgsh.supabase.co/rest/v1/";
  const KEY = "sb_publishable_MoVlOTrEIZqqbHlmg_L5KA_Q3fm8YaV";
  const SESSION_IDLE_MS = 30 * 60 * 1000;
  function store(key, value) {
    try {
      if (value === undefined) return w.sessionStorage.getItem(key);
      w.sessionStorage.setItem(key, value);
    } catch (_) {}
    return null;
  }
  function hostOf(url) {
    try { return new URL(url).hostname.toLowerCase(); } catch (_) { return ""; }
  }
  function tag(value) {
    // Campaign identifiers must never contain answers or free text.
    return /^[a-z0-9_-]{1,80}$/i.test(value || "") ? value : null;
  }
  function normalizeSource(raw, referrer) {
    const value = String(raw || "").toLowerCase().trim();
    const host = hostOf(referrer);
    if (["facebook", "fb"].includes(value) || /(^|\.)facebook\.com$/.test(host)) return "facebook";
    if (["x", "twitter"].includes(value) || /(^|\.)(x|twitter)\.com$/.test(host) || host === "t.co") return "x";
    if (value === "threads" || /(^|\.)threads\.(net|com)$/.test(host)) return "threads";
    if (["wechat_official", "mp"].includes(value)) return "wechat_official";
    if (["wechat", "weixin", "wechat_group"].includes(value) || /(^|\.)weixin\.qq\.com$/.test(host)) return "wechat";
    if (["friend", "buddy", "challenge", "challenge_done", "return"].includes(value)) return "friend_referral";
    if (value) return tag(value) || "external_campaign";
    if (!host) return "direct";
    if (host === w.location.hostname.toLowerCase()) return "internal";
    if (/(google|bing|yahoo|baidu)\./.test(host)) return "organic_search";
    return "external_referral";
  }
  function uuid() {
    if (w.crypto && w.crypto.randomUUID) return w.crypto.randomUUID();
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
      const r = Math.floor(Math.random() * 16);
      return (c === "x" ? r : (r & 3) | 8).toString(16);
    });
  }
  function create(options) {
    const scope = options.scope || options.table;
    const params = new URLSearchParams(w.location.search);
    const referrer = w.document.referrer || "";
    const sidKey = options.sessionKey || "jmai_sid_" + scope + "_v1";
    const activityKey = "jmai_activity_" + scope + "_v2";
    const attributionKey = "jmai_attr_" + scope + "_v1";
    if (params.get("jmai_qa") === "1") store("jmai_qa_v1", "1");
    if (params.get("jmai_qa") === "0") store("jmai_qa_v1", "0");
    const hostname = w.location.hostname.toLowerCase();
    const isTest = params.get("jmai_qa") === "1" || store("jmai_qa_v1") === "1";
    const isPreview = !["japanmedai.com", "www.japanmedai.com"].includes(hostname);
    const isAutomated = !!w.navigator.webdriver || /bot|crawler|spider|headless/i.test(w.navigator.userAgent || "");
    const excluded = isTest || isPreview || isAutomated;
    let sessionId = store(sidKey);
    let lastActivity = Number(store(activityKey)) || 0;
    let attribution = null;
    try { attribution = JSON.parse(store(attributionKey) || "null"); } catch (_) {}
    const sent = new Set();
    function newAttribution() {
      return {
        source: normalizeSource(params.get("utm_source"), referrer),
        utm_source: tag(params.get("utm_source")),
        utm_medium: tag(params.get("utm_medium")),
        utm_campaign: tag(params.get("utm_campaign")),
        utm_content: tag(params.get("utm_content")),
        referrer_host: hostOf(referrer)
      };
    }
    function ensureSession() {
      const now = Date.now();
      if (!sessionId || (lastActivity && now - lastActivity > SESSION_IDLE_MS)) {
        sessionId = uuid();
        attribution = newAttribution();
        sent.clear();
        store(sidKey, sessionId);
      }
      if (!attribution) attribution = newAttribution();
      lastActivity = now;
      store(activityKey, String(now));
      store(attributionKey, JSON.stringify(attribution));
    }
    ensureSession();
    function track(eventName, data) {
      if (excluded) return Promise.resolve({ skipped: true, reason: "test_preview_or_automation" });
      ensureSession();
      const details = {
        page_version: options.pageVersion || "legacy",
        locale: w.document.documentElement.lang || "unknown",
        is_test: false,
        utm_content: tag(attribution.utm_content),
        referrer_host: attribution.referrer_host || null
      };
      // Never send type, answers, medical summaries or contact fields.
      ["kind", "invite_kind", "funnel_step", "cta_id", "cta_position"].forEach(function (key) {
        if (data && tag(data[key])) details[key] = data[key];
      });
      ["day_index", "days"].forEach(function (key) {
        if (data && Number.isInteger(data[key]) && data[key] >= 0 && data[key] <= 7) details[key] = data[key];
      });
      return w.fetch(API + options.table, {
        method: "POST", keepalive: true,
        headers: { apikey: KEY, "Content-Type": "application/json", Prefer: "return=minimal" },
        body: JSON.stringify({
          session_id: sessionId, event_name: eventName, source: attribution.source,
          utm_source: tag(attribution.utm_source), utm_medium: tag(attribution.utm_medium),
          utm_campaign: tag(attribution.utm_campaign), page_path: w.location.pathname,
          referrer: attribution.referrer_host ? "https://" + attribution.referrer_host : null,
          event_data: details
        })
      }).then(function (response) { return { ok: response.ok, status: response.status }; })
        .catch(function () { return { ok: false, reason: "network" }; });
    }
    function trackOnce(eventName, data) {
      ensureSession();
      if (sent.has(eventName)) return Promise.resolve({ skipped: true, reason: "already_sent" });
      sent.add(eventName);
      return track(eventName, data).then(function (result) {
        if (result && result.ok === false) sent.delete(eventName);
        return result;
      });
    }
    return {
      get sessionId() { return sessionId; }, get source() { return attribution.source; },
      excluded: excluded, track: track, trackOnce: trackOnce
    };
  }
  w.JMAIAnalytics = { create: create };
})(window);
