/* GA4 events for SiteKPI itself → gtag.js straight to GA4 (no Tag Manager). Design: docs/plan #analytics.
   Rule (Google API Limited Use): never send anything read from the user's GA4 — no property id or
   name, no metric values, no event names they picked, no channel names. Only SiteKPI's own keys
   (screen, button, metric / industry / goal catalog keys, period) and choices the user made. */
(function () {
  "use strict";
  window.dataLayer = window.dataLayer || [];

  function cookie(name) {
    const hit = document.cookie.split("; ").find((c) => c.startsWith(name + "="));
    return hit ? decodeURIComponent(hit.slice(name.length + 1)) : "";
  }
  const path = location.pathname;
  const isBoard = !!document.getElementById("s-l0");
  const screen = path === "/" ? "home"
    : path.startsWith("/connect") ? "connect"
    : path.startsWith("/glossary") ? "glossary"
    : path.startsWith("/samples") ? "samples"
    : path.startsWith("/builder") ? "builder"
    : path.startsWith("/settings") ? "settings"
    : path.startsWith("/policy") ? "policy"
    : path.startsWith("/terms") ? "terms"
    : isBoard ? "board" : "other";
  const connection = cookie("sk_conn") || "none"; // none · demo · live (set by the server, no ids)
  const lang = (document.documentElement.lang || "ja").slice(0, 2);

  // gtag.js is on the page only when GA4_ID is set (Cloud Run); elsewhere events stay in dataLayer for tests
  function send(command, a, b) {
    if (typeof window.gtag === "function") window.gtag(command, a, b);
    else window.dataLayer.push(Object.assign({ event: command === "event" ? a : "set" }, b || {}));
  }
  function track(event, params) {
    const row = Object.assign({ screen: screen }, params || {});
    Object.keys(row).forEach((k) => { if (row[k] === undefined || row[k] === "") delete row[k]; });
    send("event", event, row);
  }
  window.SiteKPITrack = track;
  // user properties (register ui_language and connection as user-scoped custom dimensions in GA4)
  send("set", "user_properties", { ui_language: lang, connection: connection });

  // one-shot events the server queued in a cookie: login · oauth_error.denied · demo_start.hero …
  const queued = cookie("sk_ev");
  if (queued) {
    document.cookie = "sk_ev=; Max-Age=0; path=/; SameSite=Lax";
    queued.split(",").forEach((item) => {
      const [ev, arg] = item.split(".");
      if (ev === "login") track("login", { method: "google" });
      else if (ev === "oauth_error") track("oauth_error", { reason: arg || "other" });
      else if (ev === "demo_start") track("demo_start", { location: arg });
    });
  }

  // board_view: once per page load; first_in_session marks the activation (mode: live · sample; demo is dev only)
  if (isBoard) {
    const mode = path === "/live" ? (connection === "demo" ? "demo" : "live") : "sample";
    const sel = document.querySelector("form[data-period] select[name=period]");
    let first = "true";
    try { first = sessionStorage.getItem("sk_bv") ? "false" : "true"; sessionStorage.setItem("sk_bv", "1"); } catch (e) { /* private mode */ }
    track("board_view", { mode: mode, period: sel ? sel.value : "28d", first_in_session: first });
  }

  function paramsFrom(el) {
    const out = {};
    Object.keys(el.dataset).forEach((k) => {
      if (k.length > 5 && k.startsWith("track")) out[k.charAt(5).toLowerCase() + k.slice(6)] = el.dataset[k];
    });
    return out;
  }

  document.addEventListener("click", (e) => {
    const t = e.target;
    if (!(t instanceof Element)) return;
    const tagged = t.closest("[data-track]");
    if (tagged) { track(tagged.dataset.track, paramsFrom(tagged)); return; }

    const a = t.closest("a[href]");
    const href = a ? a.getAttribute("href") : "";
    if (a && href.startsWith("https://script.google.com/macros/")) {
      track("contact_click", { location: a.closest("footer") ? "footer" : screen });
      return;
    }
    if (a && href === "/connect/google") { track("oauth_start", { location: screen }); return; }
    if (t.closest("[data-feedback-open]")) { track("feedback_open"); return; }
    if (t.closest("[data-memo-toggle]")) { track("memo_toggle"); return; }

    if (isBoard) {
      const help = t.closest(".help-btn[data-help]");
      if (help) { track("explain_open", { metric: help.dataset.help, location: "details" }); return; }
      const pop = t.closest("[data-pop-open]");
      if (pop) {
        const id = pop.dataset.popOpen || "";
        const holder = pop.closest("[data-metric]");
        if (id.startsWith("tile-")) track("explain_open", { metric: holder ? holder.dataset.metric : "", location: "tile" });
        else if (id.startsWith("watch-")) track("explain_open", { metric: holder ? holder.dataset.metric : "", location: "watch" });
        return;
      }
      const edit = t.closest("[data-edit-open], a[href*='edit=1'], [data-edit-step]");
      if (edit) {
        track("flow_edit_start", { location: edit.closest(".notice") ? "notice" : edit.closest(".flow-nudge") || edit.hasAttribute("data-edit-step") ? "nudge" : "flow", mode: path === "/live" ? "live" : "sample" });
        return;
      }
      const ch = t.closest("[data-flow-ch]");
      if (ch && ch.dataset.flowCh !== "all") { track("channel_filter"); return; }
    }

    if (screen === "glossary") {
      const kind = t.closest(".gl-kind[data-kind]");
      if (kind) { track("glossary_filter", { category: kind.dataset.kind || "all" }); return; }
      const sum = t.closest("details.gl-card > summary");
      if (sum && !sum.parentElement.open) { track("glossary_open", { metric: sum.parentElement.dataset.id }); return; }
    }

    if (screen === "samples" && a) {
      const u = new URL(a.href, location.href);
      if (u.pathname === "/samples" && u.searchParams.get("b")) {
        track("sample_view", { behavior: u.searchParams.get("b"), industry: u.searchParams.get("i") || "" });
      } else if (u.pathname === "/connect" || a.classList.contains("sp-btn-primary")) {
        const cur = new URL(location.href).searchParams;
        track("sample_to_board", { behavior: cur.get("b") || "", industry: cur.get("i") || "", cta: u.pathname === "/connect" ? "connect" : "board" });
      }
    }
  }, true);

  document.addEventListener("toggle", (e) => {
    const d = e.target;
    if (d instanceof HTMLDetailsElement && d.open && d.dataset.trackFaq) track("faq_open", { faq_id: d.dataset.trackFaq });
  }, true);

  document.addEventListener("change", (e) => {
    const t = e.target;
    if (t instanceof HTMLSelectElement && t.name === "period" && t.closest("form[data-period]")) track("period_change", { period: t.value });
  }, true);

  document.addEventListener("submit", (e) => {
    const f = e.target;
    if (!(f instanceof HTMLFormElement)) return;
    const action = f.getAttribute("action") || "";
    if (action === "/setup/keep") track("guess_confirm");
    else if (action === "/connect/property") track("property_select");
    else if (action === "/connect/disconnect") track("disconnect");
    else if (action === "/setup/industry") {
      const pick = f.querySelector("input[name=industry]:checked");
      track("industry_change", { industry: pick ? pick.value : "", from_guess: document.querySelector(".notice") ? "true" : "false" });
    } else if (f.id === "edit-form") track("flow_save", { change: "flow" });
    else if (f.matches("[data-bench-form]")) {
      const low = f.querySelector("input[name^=low_]");
      track("benchmark_save", { metric: low ? low.name.slice(4) : "" });
    } else if (action === "/settings") {
      const loc = f.querySelector("[name=locale]:checked, select[name=locale]");
      if (loc && loc.value !== lang) track("lang_change", { language: loc.value, location: "settings" });
    }
  }, true);

  // 指標辞典 search: when typing pauses for a second (first 40 characters only)
  const q = document.getElementById("gl-q");
  if (q) {
    let timer = 0;
    q.addEventListener("input", () => {
      clearTimeout(timer);
      timer = setTimeout(() => { const v = q.value.trim(); if (v) track("search", { search_term: v.slice(0, 40) }); }, 1000);
    });
  }
})();
