(function (w) {
  "use strict";

  const API = "https://pcuofvwabfjoumjahgsh.supabase.co/rest/v1/";
  const KEY = "sb_publishable_MoVlOTrEIZqqbHlmg_L5KA_Q3fm8YaV";

  function store(key, value) {
    try {
      if (value === undefined) return sessionStorage.getItem(key);
      sessionStorage.setItem(key, value);
    } catch (_) {}
    return null;
  }

  function referrerHost(referrer) {
    try { return new URL(referrer).hostname.toLowerCase(); } catch (_) { return ""; }
  }

  function normalizeSource(raw, referrer) {
    const value = String(raw || "").toLowerCase().trim();
    const host = referrerHost(referrer);
    if (["facebook", "fb"].includes(value) || /(^|\.)facebook\.com$/.test(host)) return "facebook";
    if (["x", "twitter"].includes(value) || /(^|\.)(x|twitter)\.com$/.test(host)) return "x";
    if (value === "threads" || /(^|\.)threads\.net$/.test(host)) return "threads";
    if (["wechat", "weixin", "wechat_group"].includes(value) || /weixin\.qq\.com$/.test(host)) return "wechat";
    if (["wechat_official", "公众号", "mp"].includes(value)) return "wechat_official";
    if (["friend", "buddy", "challenge", "return"].includes(value)) return "friend_referral";
    if (value) return value.slice(0, 100);
    if (!host) return "direct";
    if (host === location.hostname.toLowerCase()) return "internal";
    if (/(google|bing|yahoo|baidu)\./.test(host)) return "organic_search";
    return "external_referral";
  }

  function create(options) {
    const table = options.table;
    const scope = options.scope || table;
    const params = new URLSearchParams(location.search);
    const rawSource = params.get("utm_source");
    const referrer = document.referrer || "";
    const attributionKey = "jmai_attr_" + scope + "_v1";
    let attribution = null;
    try { attribution = JSON.parse(store(attributionKey) || "null"); } catch (_) {}
    if (!attribution || rawSource) {
      attribution = {
        source: normalizeSource(rawSource, referrer),
        utm_source: rawSource,
        utm_medium: params.get("utm_medium"),
        utm_campaign: params.get("utm_campaign"),
        utm_content: params.get("utm_content"),
        referrer_host: referrerHost(referrer)
      };
      store(attributionKey, JSON.stringify(attribution));
    }

    const sidKey = "jmai_sid_" + scope + "_v1";
    let sessionId = store(sidKey);
    if (!sessionId) {
      sessionId = (w.crypto && crypto.randomUUID) ? crypto.randomUUID() : String(Date.now()) + "-" + Math.random().toString(36).slice(2);
      store(sidKey, sessionId);
    }

    const sent = new Set();
    function track(eventName, data) {
      const details = Object.assign({}, data || {}, {
        utm_content: attribution.utm_content || null,
        referrer_host: attribution.referrer_host || null
      });
      return fetch(API + table, {
        method: "POST",
        keepalive: true,
        headers: { apikey: KEY, Authorization: "Bearer " + KEY, "Content-Type": "application/json", Prefer: "return=minimal" },
        body: JSON.stringify({
          session_id: sessionId,
          event_name: eventName,
          source: attribution.source,
          utm_source: attribution.utm_source,
          utm_medium: attribution.utm_medium,
          utm_campaign: attribution.utm_campaign,
          page_path: location.pathname,
          referrer: referrer || null,
          event_data: details
        })
      }).catch(function () {});
    }

    function trackOnce(eventName, data) {
      if (sent.has(eventName)) return Promise.resolve();
      sent.add(eventName);
      return track(eventName, data);
    }

    return { sessionId: sessionId, source: attribution.source, track: track, trackOnce: trackOnce };
  }

  w.JMAIAnalytics = { create: create };
})(window);
