(function (w) {
  "use strict";
  function init(options) {
    const result = document.getElementById(options.resultId);
    const button = document.getElementById(options.buttonId);
    const panel = document.getElementById(options.panelId);
    if (!result || !button || !panel) return;
    let exposed = false;
    function recordExposure() {
      if (exposed || document.visibilityState === "hidden" || result.classList.contains("hidden")) return;
      const rect = result.getBoundingClientRect();
      if (rect.bottom <= 0 || rect.top >= w.innerHeight) return;
      exposed = true;
      options.analytics.trackOnce("result_viewed", { funnel_step: "result_viewed" }).then(function (response) {
        if (response && response.ok === false) exposed = false;
      });
    }
    if ("IntersectionObserver" in w) {
      const observer = new IntersectionObserver(function (entries) {
        if (entries.some(function (entry) { return entry.isIntersecting; })) recordExposure();
      }, { threshold: 0 });
      observer.observe(result);
    } else {
      new MutationObserver(recordExposure).observe(result, { attributes: true, attributeFilter: ["class"] });
    }
    w.addEventListener("scroll", recordExposure, { passive: true });
    w.addEventListener("online", recordExposure);
    document.addEventListener("visibilitychange", recordExposure);
    recordExposure();
    button.addEventListener("click", function () {
      recordExposure();
      if (options.beforeOpen) options.beforeOpen();
      panel.classList.remove("hidden");
      button.setAttribute("aria-expanded", "true");
      options.analytics.track("next_step_clicked", {
        funnel_step: "next_step_clicked", cta_id: options.ctaId, cta_position: "result_primary"
      });
      panel.scrollIntoView({ behavior: "smooth", block: "start" });
      panel.focus({ preventScroll: true });
    });
  }
  function copy(buttonId, textId, statusId, successText, fallbackText) {
    const button = document.getElementById(buttonId);
    const text = document.getElementById(textId);
    const status = document.getElementById(statusId);
    if (!button || !text || !status) return;
    button.addEventListener("click", async function () {
      try {
        await navigator.clipboard.writeText(text.value);
        status.textContent = successText;
      } catch (_) {
        text.classList.remove("hidden");
        text.focus(); text.select();
        status.textContent = fallbackText;
      }
    });
  }
  w.JMAINextStep = { init: init, copy: copy };
})(window);
