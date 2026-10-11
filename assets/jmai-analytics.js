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

(function () {
  "use strict";

  const LOGO = "/assets/bunto-official-logo.png";
  const WECHAT_ID = "JAPANYAO111";
  const CODE_STORE_KEY = "jmai_content_code_v1";
  const LANG = (document.documentElement.lang || "").toLowerCase();
  const T = LANG.indexOf("en") === 0 ? {
    btn: "Copy WeChat ID ", done: "✓ WeChat ID copied", copied: "WeChat ID copied: ", manual: "Please copy the WeChat ID manually: ",
    withCode: "When adding us, please write this code in the request note: ",
    noCode: "When adding us, please write the code you saw in the video or post (e.g. H07) in the request note; if none, write \"website\"."
  } : LANG.indexOf("zh-hant") === 0 ? {
    btn: "複製微信號 ", done: "✓ 微信號已複製", copied: "微信號已複製：", manual: "請手動複製微信號 ",
    withCode: "添加好友時請備註來源口令：",
    noCode: "添加好友時請在驗證信息裡備註你在影片或貼文中看到的口令（例如 H07）；沒有口令就備註「官網」"
  } : {
    btn: "复制微信号 ", done: "✓ 微信号已复制", copied: "微信号已复制：", manual: "请手动复制微信号 ",
    withCode: "添加好友时请备注来源口令：",
    noCode: "添加好友时请在验证信息里备注你在视频或帖子中看到的口令（例如 H07）；没有口令就备注“官网”"
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

    const urlCode = getContentCode();
    const code = urlCode || "官网";
    /* No code in URL: ask the visitor (non-blocking) to write the code they saw in the
       friend-request note; customer service records it. No prompt()/alert() dialogs. */
    const ask = urlCode ? T.withCode + urlCode : T.noCode;
    showToast((copied ? T.copied : T.manual) + WECHAT_ID + (LANG.indexOf("en") === 0 ? ". " : "。") + ask);

    if (button && copied) {
      const old = button.textContent;
      button.textContent = T.done;
      setTimeout(function () { button.textContent = old; }, 1800);
    }

    const a = contactAnalytics();
    if (a) a.track("wechat_click", { source_code: code, code_from_url: !!urlCode });
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
