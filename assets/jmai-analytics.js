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

  const LOGO = "/assets/BUNTO-logo-version-02.svg";
  const WECHAT_ID = "JAPANYAO111";
  const CODE_STORE_KEY = "jmai_content_code_v1";

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

  function rememberContentCode(code) {
    const safe = cleanCode(code);
    if (!safe) return "";
    try { sessionStorage.setItem(CODE_STORE_KEY, safe); } catch (_) {}
    return safe;
  }

  function injectStyles() {
    if (document.getElementById("jmai-final-brand-style")) return;
    const style = document.createElement("style");
    style.id = "jmai-final-brand-style";
    style.textContent = [
      ".brand{display:flex!important;align-items:center;gap:10px}",
      ".jmaiBrandLogo{width:54px;height:54px;object-fit:contain;flex:0 0 54px}",
      ".jmaiBrandText{display:block}",
      ".contactGrid.jmaiContactTwo{grid-template-columns:repeat(2,minmax(0,1fr))}",
      ".jmaiWechatCopy{margin-top:10px;width:100%}",
      "@media(max-width:560px){.jmaiBrandLogo{width:46px;height:46px;flex-basis:46px}.contactGrid.jmaiContactTwo{grid-template-columns:1fr}}"
    ].join("");
    document.head.appendChild(style);
  }

  function patchBranding() {
    document.querySelectorAll("a.brand").forEach(function (brand) {
      if (brand.querySelector(".jmaiBrandLogo")) return;
      const img = document.createElement("img");
      img.src = LOGO;
      img.alt = "BUNTO.CO 文腾株式会社";
      img.className = "jmaiBrandLogo";
      brand.insertBefore(img, brand.firstChild);
    });
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
        scope: isSecondOpinion ? "second_opinion_contact" : "site_contact"
      });
    } catch (_) {
      return null;
    }
  }

  async function copyWechatAndPrompt(button) {
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

    if (!copied) {
      window.prompt("请复制微信号：", WECHAT_ID);
    }

    let code = getContentCode();
    if (!code) {
      const entered = window.prompt("微信号已复制。请填写你在视频或帖子中看到的来源口令（例如 H07），添加好友时一并备注：", "");
      code = rememberContentCode(entered);
    }

    if (code) {
      window.alert("微信号已复制：" + WECHAT_ID + "\n添加好友时请在验证信息中备注来源口令：" + code);
    } else {
      window.alert("微信号已复制：" + WECHAT_ID + "\n添加好友时，请备注你在视频或帖子中看到的来源口令，便于我们识别咨询来源。");
    }

    if (button) {
      const old = button.textContent;
      button.textContent = "✓ 微信号已复制";
      setTimeout(function () { button.textContent = old; }, 1800);
    }

    const a = contactAnalytics();
    if (a) a.track("wechat_click", { source_code: code || null });
  }

  function patchContacts() {
    document.querySelectorAll(".contactItem").forEach(function (item) {
      const title = item.querySelector("h3");
      if (title && title.textContent.trim().toLowerCase() === "whatsapp") item.remove();
    });

    document.querySelectorAll(".contactGrid").forEach(function (grid) {
      grid.classList.add("jmaiContactTwo");
    });

    document.querySelectorAll(".contactItem").forEach(function (item) {
      const title = item.querySelector("h3");
      if (!title || title.textContent.trim() !== "微信" || item.querySelector(".jmaiWechatCopy")) return;
      const button = document.createElement("button");
      button.type = "button";
      button.className = "btn alt jmaiWechatCopy";
      button.textContent = "复制微信号 " + WECHAT_ID;
      button.addEventListener("click", function () { copyWechatAndPrompt(button); });
      item.appendChild(button);
    });
  }

  function init() {
    injectStyles();
    patchBranding();
    patchContacts();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
