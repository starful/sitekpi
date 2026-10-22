/* KPI board: 説明 dialogs, more/less, per-section view modes (localStorage). Data: #board-data */
const BOARD = JSON.parse(document.getElementById("board-data").textContent);
const I18N_CLOSE = BOARD.close;
const I18N_MORE = (n) => BOARD.more_tpl.replace("__N__", String(n));
const I18N_EVENT_SUB_OPEN = BOARD.event_sub_open;
const I18N_EVENT_SUB_CLOSED = BOARD.event_sub_closed;
document.querySelectorAll(".help-btn").forEach((btn) => {
  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    const id = btn.getAttribute("data-help");
    const dialog = document.getElementById("help-" + id);
    if (dialog) dialog.showModal();
  });
});
document.querySelectorAll("[data-help-dialog]").forEach((dialog) => {
  dialog.addEventListener("click", (e) => {
    if (e.target === dialog) dialog.close();
  });
});
document.querySelectorAll(".more-chip").forEach((btn) => {
  btn.addEventListener("click", () => {
    const key = btn.getAttribute("data-more");
    const panel = document.getElementById("panel-" + key);
    if (!panel) return;
    const open = panel.classList.toggle("is-expanded");
    const n = panel.querySelectorAll(".mode-list .is-more").length;
    btn.textContent = open ? I18N_CLOSE : I18N_MORE(n);
    const sub = panel.querySelector('[data-count-sub="' + key + '"]');
    if (sub && key === "events") {
      sub.textContent = open ? I18N_EVENT_SUB_OPEN : I18N_EVENT_SUB_CLOSED;
    }
  });
});

const VIEW_PREFIX = "kpistarter.sample.sectionView.";
const allowed = {
  funnel: ["list", "card", "compare"],
  events: ["list", "card", "bar"],
  channels: ["list", "card", "bar", "stack"],
  engage: BOARD.modes.engage,
  audience: BOARD.modes.audience,
  biz: ["list", "card"],
};
function setSectionView(section, mode) {
  const modes = allowed[section] || ["list"];
  /* legacy → settled set */
  if (mode === "gap") mode = "compare";
  if (mode === "gauge" || mode === "compact" || mode === "funnel") mode = "list";
  if ((mode === "trend" || mode === "bar") && section !== "events" && section !== "channels" && !modes.includes(mode)) mode = "list";
  if (!modes.includes(mode)) mode = "list";
  const body = document.querySelector('[data-section-body="' + section + '"]');
  if (body) body.setAttribute("data-view-mode", mode);
  document.querySelectorAll('.view-btn[data-section="' + section + '"]').forEach((b) => {
    b.classList.toggle("is-on", b.dataset.mode === mode);
  });
  localStorage.setItem(VIEW_PREFIX + section, mode);
}
const defaults = { events: "bar", channels: "stack", funnel: "list" };
Object.keys(allowed).forEach((section) => {
  const saved = localStorage.getItem(VIEW_PREFIX + section);
  setSectionView(section, saved || defaults[section] || "list");
});
document.querySelectorAll(".view-btn[data-section]").forEach((btn) => {
  btn.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    setSectionView(btn.dataset.section, btn.dataset.mode);
  });
});


/* 目安の調整 — bottom sheet */
(function () {
  const sheet = document.getElementById("bench-sheet");
  if (!sheet) return;
  const form = sheet.querySelector("[data-bench-form]");
  const errorBox = sheet.querySelector("[data-bench-error]");

  function open(key) {
    if (!sheet.open) sheet.showModal();
    sheet.querySelectorAll(".sheet-row.is-target").forEach((r) => r.classList.remove("is-target"));
    if (key) {
      const row = sheet.querySelector('[data-bench-row="' + key + '"]');
      if (row) {
        row.classList.add("is-target");
        row.scrollIntoView({ block: "center" });
        const input = row.querySelector("input");
        if (input) { input.focus(); input.select(); }
      }
    }
  }
  document.querySelectorAll("[data-bench-open]").forEach((el) => {
    el.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      open(el.getAttribute("data-bench-open"));
    });
  });
  sheet.querySelectorAll("[data-bench-close]").forEach((b) => b.addEventListener("click", () => sheet.close()));
  sheet.addEventListener("click", (e) => { if (e.target === sheet) sheet.close(); });

  function post(url, body) {
    return fetch(url, { method: "POST", body: body, headers: { Accept: "application/json" }, credentials: "same-origin" });
  }
  function showErrors(errors) {
    sheet.querySelectorAll("[data-bench-row]").forEach((row) => {
      const msg = errors[row.getAttribute("data-bench-row")];
      const p = row.querySelector("[data-row-error]");
      row.classList.toggle("has-error", Boolean(msg));
      if (p) { p.textContent = msg || ""; p.hidden = !msg; }
    });
    if (errorBox) errorBox.hidden = Object.keys(errors).length === 0;
    const first = sheet.querySelector(".sheet-row.has-error input");
    if (first) first.focus();
  }
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const res = await post(form.action, new FormData(form));
    if (res.ok) { location.reload(); return; }
    let data = {};
    try { data = await res.json(); } catch (err) { /* ignore */ }
    showErrors(data.errors || {});
  });
  sheet.querySelectorAll("[data-bench-reset]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const body = new FormData();
      body.set("pack", form.elements.pack.value);
      body.set("board", form.elements.board.value);
      body.set("metric", btn.getAttribute("data-bench-reset") || "");
      const res = await post("/benchmarks/reset", body);
      if (res.ok) location.reload();
    });
  });
  if (location.hash === "#bench") open("");
})();
