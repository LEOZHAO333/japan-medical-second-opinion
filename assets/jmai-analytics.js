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
  function aiSource(value) {
    switch (String(value || "").toLowerCase().trim()) {
      case "chatgpt.com": return "chatgpt";
      case "perplexity.ai": return "perplexity";
      case "copilot.microsoft.com": return "copilot";
      case "gemini.google.com": return "gemini";
      default: return null;
    }
  }
  function sourceTag(value) {
    return aiSource(value) || tag(value);
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
    if (aiSource(value) || (!value && aiSource(host))) return "ai_assistant";
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
        utm_source: sourceTag(params.get("utm_source")),
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
      // WeChat source code from #62 (video/post code such as G6A, or "官网" when none).
      if (data && (/^[A-Z0-9_-]{1,24}$/.test(data.source_code || "") || data.source_code === "官网")) details.source_code = data.source_code;
      if (data && typeof data.code_from_url === "boolean") details.code_from_url = data.code_from_url;
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

(function () {
  "use strict";

  const LOGO = "/assets/bunto-official-logo.png";
  const WECHAT_ID = "JAPANYAO111";
  const CODE_STORE_KEY = "jmai_content_code_v1";
  const LANG = (document.documentElement.lang || "").toLowerCase();
  const T = LANG.indexOf("en") === 0 ? {
    btn: "Copy WeChat ID ", done: "✓ WeChat ID copied", copied: "WeChat ID copied: ", manual: "Please copy the WeChat ID manually: ",
    withCode: "When adding us, please write this code in the request note: ",
    noCode: "When adding us, please write the code you saw in the video or post (e.g. H07) in the request note; if none, write \"website\".",
    askTitle: "WeChat ID copied. Which video or post did you see? Enter its code (e.g. H07):", ok: "OK", skip: "Skip", site: "website"
  } : LANG.indexOf("zh-hant") === 0 ? {
    btn: "複製微信號 ", done: "✓ 微信號已複製", copied: "微信號已複製：", manual: "請手動複製微信號 ",
    withCode: "添加好友時請備註來源口令：",
    noCode: "添加好友時請在驗證信息裡備註你在影片或貼文中看到的口令（例如 H07）；沒有口令就備註「官網」",
    askTitle: "微信號已複製。你是在哪條影片或貼文看到我們的？請填寫口令（例如 H07）：", ok: "確定", skip: "略過", site: "官網"
  } : {
    btn: "复制微信号 ", done: "✓ 微信号已复制", copied: "微信号已复制：", manual: "请手动复制微信号 ",
    withCode: "添加好友时请备注来源口令：",
    noCode: "添加好友时请在验证信息里备注你在视频或帖子中看到的口令（例如 H07）；没有口令就备注“官网”",
    askTitle: "微信号已复制。你是在哪条视频或帖子看到我们的？请填写口令（例如 H07）：", ok: "确定", skip: "跳过", site: "官网"
  };

  function cleanCode(value) {
    const code = String(value || "").trim().toUpperCase();
    return /^[A-Z0-9_-]{1,24}$/.test(code) ? code : "";
  }

  function getContentCode() {
    const params = new URLSearchParams(location.search);
    const fromUrl = cleanCode(params.get("code") || params.get("src") || params.get("utm_content"));
    if (fromUrl) {
      try { sessionStorage.setItem(CODE_STORE_KEY, fromUrl); } catch (_) {}
      return fromUrl;
    }
    try { return cleanCode(sessionStorage.getItem(CODE_STORE_KEY)); } catch (_) { return ""; }
  }

  function showToast(message) {
    let toast = document.getElementById("jmaiToast");
    if (!toast) {
      toast = document.createElement("div");
      toast.id = "jmaiToast";
      toast.className = "jmaiToast";
      toast.setAttribute("role", "status");
      toast.setAttribute("aria-live", "polite");
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    /* Pages without jmai.css (e.g. weight-v3): minimal inline styling so the toast is visible. */
    const styled = getComputedStyle(toast).position === "fixed";
    if (!styled) {
      toast.style.cssText = "position:fixed;left:50%;bottom:22px;transform:translateX(-50%);z-index:10001;max-width:92vw;padding:13px 17px;border-radius:14px;background:#10233f;color:#fff;font-weight:700;line-height:1.55;box-shadow:0 14px 42px rgba(16,35,63,.24)";
    }
    toast.classList.add("on");
    if (!styled) toast.style.display = "block";
    clearTimeout(showToast.timer);
    showToast.timer = setTimeout(function () {
      toast.classList.remove("on");
      if (!styled) toast.style.display = "none";
    }, 4200);
  }

  function patchBranding() {
    document.querySelectorAll("img.footerLogo").forEach(function (img) {
      img.src = LOGO;
      img.alt = "BUNTO.CO 文腾株式会社";
    });
  }

  function contactAnalytics() {
    try {
      const isSecondOpinion = location.pathname.indexOf("/second-opinion") === 0;
      return JMAIAnalytics.create({
        table: isSecondOpinion ? "jmai_second_opinion_events" : "jmai_site_events",
        scope: isSecondOpinion ? "second_opinion" : "site"
      });
    } catch (_) {
      return null;
    }
  }

  async function copyWechat(button) {
    let copied = false;
    try {
      await navigator.clipboard.writeText(WECHAT_ID);
      copied = true;
    } catch (_) {
      const ta = document.createElement("textarea");
      ta.value = WECHAT_ID;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      try { copied = document.execCommand("copy"); } catch (_) {}
      ta.remove();
    }

    if (button && copied) {
      const old = button.textContent;
      button.textContent = T.done;
      setTimeout(function () { button.textContent = old; }, 1800);
    }

    const head = (copied ? T.copied : T.manual) + WECHAT_ID + (LANG.indexOf("en") === 0 ? ". " : "。");
    const urlCode = getContentCode();
    if (urlCode) {
      showToast(head + T.withCode + urlCode);
      trackWechat(urlCode, true);
      return;
    }
    askForCode(function (entered) {
      showToast(head + T.withCode + (entered || T.site));
      trackWechat(entered || "官网", false);
    });
  }

  function trackWechat(code, fromUrl) {
    const a = contactAnalytics();
    if (a) a.track("wechat_click", { source_code: code, code_from_url: fromUrl });
  }

  /* Non-blocking in-page input (no prompt()/alert()). Finalizes once: on OK/Enter,
     on Skip, after 30 s, or when the page is hidden (visitor switched to WeChat). */
  function askForCode(done) {
    const old = document.getElementById("jmaiCodeAsk");
    if (old) old.remove();
    const box = document.createElement("div");
    box.id = "jmaiCodeAsk";
    box.setAttribute("role", "dialog");
    box.style.cssText = "position:fixed;left:50%;bottom:18px;transform:translateX(-50%);z-index:10002;width:min(92vw,420px);box-sizing:border-box;padding:14px;border-radius:16px;background:#fff;color:#10233f;border:1px solid #d9e7f5;box-shadow:0 14px 42px rgba(16,35,63,.24);font-size:15px;line-height:1.5";
    const label = document.createElement("label");
    label.textContent = T.askTitle;
    label.style.cssText = "display:block;font-weight:700;margin-bottom:8px";
    const input = document.createElement("input");
    input.type = "text"; input.maxLength = 24; input.placeholder = "H07";
    input.setAttribute("autocapitalize", "characters");
    input.style.cssText = "width:100%;box-sizing:border-box;padding:10px 12px;border:1px solid #c7d7ea;border-radius:10px;font-size:16px";
    label.appendChild(input);
    const row = document.createElement("div");
    row.style.cssText = "display:flex;gap:8px;justify-content:flex-end;margin-top:10px";
    const skip = document.createElement("button");
    skip.type = "button"; skip.textContent = T.skip;
    skip.style.cssText = "padding:9px 14px;border-radius:10px;border:1px solid #c7d7ea;background:#fff;color:#395d86;font-weight:700";
    const ok = document.createElement("button");
    ok.type = "button"; ok.textContent = T.ok;
    ok.style.cssText = "padding:9px 16px;border-radius:10px;border:0;background:#155db4;color:#fff;font-weight:700";
    row.appendChild(skip); row.appendChild(ok);
    box.appendChild(label); box.appendChild(row);
    document.body.appendChild(box);

    let finished = false;
    function finish(useInput) {
      if (finished) return;
      finished = true;
      clearTimeout(timer);
      document.removeEventListener("visibilitychange", onHide);
      window.removeEventListener("pagehide", onHide);
      const code = useInput ? cleanCode(input.value) : "";
      if (code) { try { sessionStorage.setItem(CODE_STORE_KEY, code); } catch (_) {} }
      box.remove();
      done(code);
    }
    function onHide(ev) { if (ev.type === "pagehide" || document.visibilityState === "hidden") finish(true); }
    const timer = setTimeout(function () { finish(true); }, 30000);
    ok.addEventListener("click", function () { finish(true); });
    skip.addEventListener("click", function () { finish(false); });
    input.addEventListener("keydown", function (ev) { if (ev.key === "Enter") finish(true); });
    document.addEventListener("visibilitychange", onHide);
    window.addEventListener("pagehide", onHide);
    try { input.focus({ preventScroll: true }); } catch (_) {}
  }

  function patchContacts() {
    /* Defense in depth: CSS hides WhatsApp before render; JS removes it when available. */
    document.querySelectorAll(".contactItem, .contact").forEach(function (item) {
      const title = item.querySelector("h3");
      if (title && title.textContent.trim().toLowerCase() === "whatsapp") item.remove();
    });

    document.querySelectorAll(".contactItem, .contact").forEach(function (item) {
      const title = item.querySelector("h3");
      const name = title ? title.textContent.trim().toLowerCase() : "";
      if (!title || !["微信", "wechat"].includes(name) || item.querySelector(".jmaiWechatCopy")) return;
      const button = document.createElement("button");
      button.type = "button";
      button.className = "btn alt jmaiWechatCopy";
      button.textContent = T.btn + WECHAT_ID;
      button.addEventListener("click", function () { copyWechat(button); });
      item.appendChild(button);
    });
  }

  function bindAttributionEvents() {
    const a = contactAnalytics();
    if (!a) return;

    document.querySelectorAll('a[href^="mailto:"]').forEach(function (link) {
      link.addEventListener("click", function () { a.track("email_click"); });
    });

    document.querySelectorAll('a[href="/second-opinion/"],a[href^="/second-opinion/?"],a[href^="/second-opinion/#"]').forEach(function (link) {
      link.addEventListener("click", function () { a.track("second_opinion_click"); });
    });
  }

  function init() {
    patchBranding();
    patchContacts();
    bindAttributionEvents();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
/* JMAI_INTERNAL_LINK_TRACKING_V1
   Tracks only anonymous navigation metadata (no free text, medical answers or contact fields). */
(function () {
  "use strict";
  document.addEventListener("click", function (event) {
    var link = event.target && event.target.closest ? event.target.closest("[data-jmai-track]") : null;
    if (!link) return;
    try {
      var tracker = window.JMAIAnalytics && window.JMAIAnalytics.create({
        table: "jmai_site_events",
        scope: "site",
        pageVersion: "topic-cluster-v2"
      });
      if (!tracker) return;
      tracker.track("internal_link_click", {
        kind: link.getAttribute("data-jmai-track") || "internal",
        cta_id: link.getAttribute("data-jmai-id") || "internal_link",
        cta_position: link.getAttribute("data-jmai-position") || "body"
      });
    } catch (_) {}
  }, { passive: true });
})();
