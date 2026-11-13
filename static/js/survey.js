/* 30秒アンケート (top of the メモ・ご意見 panel). Design: canvas 「11 30秒アンケート」, docs/plan #visitlog.
   When: 20 s after the first board view, or right away from the 2nd board view. One question per step;
   choosing moves on. 答えた / もう聞かない → never again (localStorage sk_sv); あとで → next visit (sessionStorage).
   Panel closed → only a blue dot on its tab. Saved by POST /survey with the same anonymous id as the visitor log. */
(function () {
  "use strict";
  const box = document.querySelector("[data-memo]");
  const sv = box && box.querySelector("[data-survey]");
  if (!sv || !document.getElementById("s-l0")) return; // board pages only
  const lget = (k) => { try { return localStorage.getItem(k); } catch (e) { return null; } };
  const lset = (k, v) => { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } };
  const sget = (k) => { try { return sessionStorage.getItem(k); } catch (e) { return null; } };
  const sset = (k, v) => { try { sessionStorage.setItem(k, v); } catch (e) { /* private mode */ } };
  if (lget("sk_sv") || sget("sk_sv_later")) return;

  const steps = Array.from(sv.querySelectorAll("[data-sv-q]"));
  const stepEl = sv.querySelector("[data-sv-step]");
  const bar = sv.querySelector("[data-sv-bar]");
  const back = sv.querySelector("[data-sv-back]");
  const done = box.querySelector("[data-sv-done]");
  const answers = {};
  let at = 0;

  function show(i) {
    at = i;
    steps.forEach((el, n) => { el.hidden = n !== i; });
    stepEl.textContent = (i + 1) + " / " + steps.length;
    bar.style.width = ((i + 1) / steps.length * 100) + "%";
    back.hidden = i === 0;
  }
  function open() {
    sv.hidden = false;
    box.classList.add("has-ask");
    const tab = box.querySelector(".memo-tab");
    if (tab && sv.dataset.dot) tab.title = sv.dataset.dot;
    show(0);
    if (window.SiteKPITrack) window.SiteKPITrack("survey_view");
  }
  function close(state) {
    sv.hidden = true;
    box.classList.remove("has-ask");
    if (state === "later") sset("sk_sv_later", "1"); else lset("sk_sv", state);
  }

  sv.addEventListener("click", (e) => {
    const a = e.target.closest("[data-sv-a]");
    if (a) {
      const q = a.closest("[data-sv-q]");
      answers[q.dataset.svQ] = a.dataset.svA;
      q.querySelectorAll("[data-sv-a]").forEach((b) => b.setAttribute("aria-pressed", b === a ? "true" : "false"));
      setTimeout(() => show(Math.min(at + 1, steps.length - 1)), 160);
      return;
    }
    if (e.target.closest("[data-sv-back]")) { show(Math.max(0, at - 1)); return; }
    if (e.target.closest("[data-sv-later]")) { close("later"); if (window.SiteKPITrack) window.SiteKPITrack("survey_skip", { reason: "later", step: String(at + 1) }); return; }
    if (e.target.closest("[data-sv-never]")) { close("never"); if (window.SiteKPITrack) window.SiteKPITrack("survey_skip", { reason: "never", step: String(at + 1) }); return; }
    const send = e.target.closest("[data-sv-send]");
    if (send) {
      const text = (sv.querySelector("[data-sv-text]").value || "").trim().slice(0, 200);
      send.disabled = true;
      fetch("/survey", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answers: answers, text: text, lang: (document.documentElement.lang || "ja").slice(0, 2) }) })
        .catch(() => {})
        .finally(() => {
          close("done");
          if (window.SiteKPITrack) window.SiteKPITrack("survey_submit", { has_comment: text ? "true" : "false" });
          done.hidden = false;
          setTimeout(() => { done.hidden = true; }, 6000);
        });
    }
  });

  // when to ask: 2nd board view → now; otherwise 20 s after this one
  const seen = Number(lget("sk_sv_boards") || "0") + 1;
  lset("sk_sv_boards", String(seen));
  if (seen >= 2) open(); else setTimeout(open, 20000);
})();
