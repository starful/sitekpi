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


