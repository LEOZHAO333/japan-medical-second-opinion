(function () {
  "use strict";
  // Anonymous, fixed-value feedback only. No medical content, free text or contact data.
  var tracker = window.JMAIAnalytics && window.JMAIAnalytics.create({
    table: "jmai_site_events", scope: "site", pageVersion: "checkup-qa-v1"
  });
  document.addEventListener("click", function (event) {
    var button = event.target && event.target.closest ? event.target.closest(".qaFeedback button[data-vote]") : null;
    if (!button) return;
    var wrap = button.closest(".qaFeedback");
    if (!wrap || wrap.dataset.submitted === "1") return;
    var vote = button.getAttribute("data-vote");
    var id = wrap.getAttribute("data-qa-id");
    if (!/^(helpful|needs_work)$/.test(vote) || !/^so-\d{3}$/.test(id || "")) return;
    var status = wrap.querySelector(".feedbackStatus");
    if (!tracker) { if (status) status.textContent = "反馈暂不可用，请稍后重试。"; return; }
    button.disabled = true;
    tracker.track("qa_feedback", { kind: vote, cta_id: id.replace("-", "_"), cta_position: "faq" })
      .then(function (result) {
        if (result && (result.ok || result.skipped)) {
          wrap.dataset.submitted = "1";
          wrap.querySelectorAll("button").forEach(function (b) { b.disabled = true; });
          if (status) status.textContent = result.skipped ? "测试环境：已记录操作，不计入正式统计。" : "感谢反馈。";
        } else {
          button.disabled = false;
          if (status) status.textContent = "提交未成功，请稍后重试。";
        }
      }).catch(function () { button.disabled = false; if (status) status.textContent = "提交未成功，请稍后重试。"; });
  });
})();
