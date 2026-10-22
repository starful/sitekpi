/* Custom builder: palette → canvas (Sortable), saved to localStorage. Data: #builder-data */
const BUILDER_DATA = JSON.parse(document.getElementById("builder-data").textContent);
const CATALOG = BUILDER_DATA.catalog;
const COLORS = BUILDER_DATA.colors;
const STORAGE_KEY = "kpistarter.builder.v3";
const LEGACY_KEYS = ["kpistarter.builder.v2", "kpistarter.builder.v1"];
const FOLD_KEY = "kpistarter.builder.folds.v1";
const GROUP_LABEL = {
  business: "業務",
  digital: "デジタル",
  event: "イベント",
  traffic: "流入",
};

const canvas = document.getElementById("canvas");
const statusEl = document.getElementById("status");
const countLabel = document.getElementById("count-label");
const searchInput = document.getElementById("pal-search");
const searchEmpty = document.getElementById("search-empty");
let foldsLockedBySearch = false;

function getOpenFolds() {
  try {
    const raw = JSON.parse(localStorage.getItem(FOLD_KEY) || "null");
    if (Array.isArray(raw)) return new Set(raw);
  } catch (_) {}
  return new Set(["layout"]);
}

function saveOpenFolds() {
  if (foldsLockedBySearch) return;
  const open = [...document.querySelectorAll(".pal-group:not(.is-collapsed)")]
    .map((g) => g.dataset.groupKey)
    .filter(Boolean);
  localStorage.setItem(FOLD_KEY, JSON.stringify(open));
}

function setGroupCollapsed(group, collapsed) {
  group.classList.toggle("is-collapsed", collapsed);
  const btn = group.querySelector("[data-toggle-group]");
  if (btn) btn.setAttribute("aria-expanded", collapsed ? "false" : "true");
}

function applySavedFolds() {
  const open = getOpenFolds();
  document.querySelectorAll(".pal-group").forEach((group) => {
    const key = group.dataset.groupKey;
    setGroupCollapsed(group, !open.has(key));
  });
}

function expandAll() {
  foldsLockedBySearch = false;
  document.querySelectorAll(".pal-group").forEach((g) => setGroupCollapsed(g, false));
  saveOpenFolds();
}

function collapseAll() {
  foldsLockedBySearch = false;
  document.querySelectorAll(".pal-group").forEach((g) => setGroupCollapsed(g, true));
  saveOpenFolds();
}

function setStatus(msg, ok) {
  statusEl.textContent = msg;
  statusEl.classList.toggle("ok", !!ok);
}

function usedIds() {
  return [...canvas.querySelectorAll(".dash-card")].map((el) => el.dataset.id);
}

function colorRowHtml(active) {
  return (
    '<div class="color-row" role="group" aria-label="色">' +
    COLORS.map((c) => {
      const on = c.id === active ? " is-active" : "";
      return (
        '<button type="button" class="swatch' + on + '" data-color="' +
        c.id + '" title="' + c.label + '" aria-label="' + c.label + '"></button>'
      );
    }).join("") +
    "</div>"
  );
}

function applyTone(el, color) {
  const c = color || "default";
  el.dataset.color = c;
  COLORS.forEach((x) => el.classList.remove("tone-" + x.id));
  el.classList.add("tone-" + c);
  el.querySelectorAll(".swatch").forEach((s) => {
    s.classList.toggle("is-active", s.dataset.color === c);
  });
}

function bindColorRow(el) {
  el.querySelector(".color-row")?.addEventListener("click", (e) => {
    const btn = e.target.closest(".swatch");
    if (!btn) return;
    e.stopPropagation();
    applyTone(el, btn.dataset.color);
    setStatus("未保存");
  });
}

function refreshPaletteState() {
  const used = new Set(usedIds());
  document.querySelectorAll('.pal-item[data-type="widget"]').forEach((el) => {
    el.classList.toggle("in-canvas", used.has(el.dataset.id));
  });
  const nCards = canvas.querySelectorAll(".dash-card").length;
  const nSec = canvas.querySelectorAll(".dash-section").length;
  countLabel.textContent = nCards + " 項目" + (nSec ? " · " + nSec + " 見出し" : "");
  canvas.classList.toggle("empty", nCards + nSec === 0);
  applySearch();
}

const fltHasValue = document.getElementById("flt-has-value");
const fltValueStats = document.getElementById("flt-value-stats");

function updateValueStats() {
  const widgets = [...document.querySelectorAll('.pal-item[data-type="widget"]')];
  const withVal = widgets.filter((el) => el.dataset.hasValue === "1").length;
  if (fltValueStats) {
    fltValueStats.textContent = "値あり " + withVal + " / " + widgets.length;
  }
}

function applySearch() {
  const q = (searchInput.value || "").trim().toLowerCase();
  const onlyVal = !!(fltHasValue && fltHasValue.checked);
  let visible = 0;
  const filtering = !!(q || onlyVal);
  if (!filtering) {
    foldsLockedBySearch = false;
    document.querySelectorAll(".pal-item").forEach((el) => el.classList.remove("is-hidden"));
    document.querySelectorAll(".pal-group").forEach((g) => g.classList.remove("is-hidden"));
    applySavedFolds();
    searchEmpty.classList.remove("show");
    updateValueStats();
    return;
  }
  foldsLockedBySearch = true;
  document.querySelectorAll(".pal-group").forEach((group) => {
    let groupVisible = 0;
    group.querySelectorAll(".pal-item").forEach((el) => {
      if (el.dataset.type === "section") {
        el.classList.toggle("is-hidden", onlyVal); // hide layout when filtering values
        if (!onlyVal && !q) {
          groupVisible += 1;
          visible += 1;
        } else if (!onlyVal) {
          const label = (el.querySelector(".pal-label")?.textContent || "").toLowerCase();
          const match = !q || label.includes(q);
          el.classList.toggle("is-hidden", !match);
          if (match) { groupVisible += 1; visible += 1; }
        }
        return;
      }
      const label = (el.querySelector(".pal-label")?.textContent || "").toLowerCase();
      const hint = (el.querySelector(".pal-hint")?.textContent || "").toLowerCase();
      const val = (el.querySelector(".pal-value")?.textContent || "").toLowerCase();
      const id = (el.dataset.id || "").toLowerCase();
      const textOk = !q || label.includes(q) || hint.includes(q) || id.includes(q) || val.includes(q);
      const valOk = !onlyVal || el.dataset.hasValue === "1";
      const match = textOk && valOk;
      el.classList.toggle("is-hidden", !match);
      if (match) {
        groupVisible += 1;
        visible += 1;
      }
    });
    group.classList.toggle("is-hidden", groupVisible === 0);
    if (groupVisible > 0) setGroupCollapsed(group, false);
  });
  searchEmpty.classList.toggle("show", visible === 0);
  updateValueStats();
}

function bindRemove(el) {
  el.querySelector(".rm").addEventListener("click", (e) => {
    e.stopPropagation();
    el.remove();
    refreshPaletteState();
    setStatus("未保存");
  });
}

function makeCard(id, color) {
  const w = CATALOG[id];
  if (!w) return null;
  const el = document.createElement("article");
  el.className = "dash-card g-" + w.group;
  el.dataset.type = "widget";
  el.dataset.id = w.id;
  el.innerHTML =
    '<button type="button" class="rm" aria-label="削除">×</button>' +
    '<span class="kind">' + (GROUP_LABEL[w.group] || w.group) + "</span>" +
    '<div class="label">' + escapeHtml(w.label) + "</div>" +
    '<div class="value">' + escapeHtml(w.value) + "</div>" +
    '<div class="hint">' + escapeHtml(w.hint) + "</div>" +
    colorRowHtml(color || "default");
  bindRemove(el);
  bindColorRow(el);
  applyTone(el, color || "default");
  return el;
}

function makeSection(title, color) {
  const el = document.createElement("div");
  el.className = "dash-section";
  el.dataset.type = "section";
  el.innerHTML =
    '<button type="button" class="rm" aria-label="削除">×</button>' +
    '<span class="sec-badge">カテゴリ</span>' +
    '<input class="sec-title" type="text" maxlength="40" placeholder="カテゴリ名" />' +
    colorRowHtml(color || "blue");
  const input = el.querySelector(".sec-title");
  input.value = title || "新しいカテゴリ";
  input.addEventListener("click", (e) => e.stopPropagation());
  input.addEventListener("mousedown", (e) => e.stopPropagation());
  input.addEventListener("input", () => setStatus("未保存"));
  bindRemove(el);
  bindColorRow(el);
  applyTone(el, color || "blue");
  return el;
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function serialize() {
  return [...canvas.children].map((el) => {
    if (el.classList.contains("dash-section")) {
      return {
        type: "section",
        title: el.querySelector(".sec-title")?.value || "カテゴリ",
        color: el.dataset.color || "blue",
      };
    }
    return {
      type: "widget",
      id: el.dataset.id,
      color: el.dataset.color || "default",
    };
  }).filter((x) => x.type === "section" || (x.type === "widget" && x.id));
}

function save() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(serialize()));
  setStatus("保存しました", true);
}

function normalizeItems(raw) {
  if (!Array.isArray(raw)) return [];
  if (raw.length && typeof raw[0] === "string") {
    return raw.map((id) => ({ type: "widget", id, color: "default" }));
  }
  return raw
    .filter((x) => x && (x.type === "section" || x.type === "widget"))
    .map((x) => ({
      ...x,
      color: x.color || (x.type === "section" ? "blue" : "default"),
    }));
}

function readStorage() {
  for (const key of [STORAGE_KEY, ...LEGACY_KEYS]) {
    try {
      const raw = JSON.parse(localStorage.getItem(key) || "null");
      if (raw != null) return raw;
    } catch (_) {}
  }
  return [];
}

function load() {
  const items = normalizeItems(readStorage());
  canvas.innerHTML = "";
  items.forEach((item) => {
    if (item.type === "section") {
      canvas.appendChild(makeSection(item.title || "カテゴリ", item.color));
    } else if (item.id) {
      const card = makeCard(item.id, item.color);
      if (card) canvas.appendChild(card);
    }
  });
  refreshPaletteState();
  if (items.length) setStatus("読み込み済み", true);
  else setStatus("未保存");
}

function clearAll() {
  if (!canvas.children.length) return;
  if (!confirm("ダッシュボードを空にしますか？")) return;
  canvas.innerHTML = "";
  refreshPaletteState();
  setStatus("未保存");
}

document.getElementById("btn-save").addEventListener("click", save);
document.getElementById("btn-clear").addEventListener("click", clearAll);
document.getElementById("btn-expand-all").addEventListener("click", expandAll);
document.getElementById("btn-collapse-all").addEventListener("click", collapseAll);
searchInput.addEventListener("input", applySearch);
fltHasValue?.addEventListener("change", applySearch);
updateValueStats();

document.querySelectorAll("[data-toggle-group]").forEach((btn) => {
  btn.addEventListener("click", () => {
    if (foldsLockedBySearch) return;
    const group = btn.closest(".pal-group");
    if (!group) return;
    setGroupCollapsed(group, !group.classList.contains("is-collapsed"));
    saveOpenFolds();
  });
});

applySavedFolds();

document.querySelectorAll(".pal-list").forEach((list) => {
  Sortable.create(list, {
    group: { name: "kpi", pull: "clone", put: false },
    sort: false,
    animation: 150,
    ghostClass: "sortable-ghost",
    chosenClass: "sortable-chosen",
    filter: ".in-canvas, .is-hidden",
    onClone: (evt) => {
      evt.item.dataset.pendingId = evt.item.dataset.id;
      evt.item.dataset.pendingType = evt.item.dataset.type || "widget";
    },
  });
});

Sortable.create(canvas, {
  group: { name: "kpi", pull: true, put: true },
  animation: 150,
  ghostClass: "sortable-ghost",
  chosenClass: "sortable-chosen",
  filter: ".sec-title, .rm, .swatch, .color-row",
  preventOnFilter: false,
  onAdd: (evt) => {
    const type = evt.item.dataset.type || evt.item.dataset.pendingType || "widget";
    const id = evt.item.dataset.id || evt.item.dataset.pendingId;

    if (type === "section" || id === "__section__") {
      const sec = makeSection("新しいカテゴリ", "blue");
      evt.item.replaceWith(sec);
      refreshPaletteState();
      setStatus("未保存");
      const input = sec.querySelector(".sec-title");
      input?.focus();
      input?.select();
      return;
    }

    if (!id || !CATALOG[id]) {
      evt.item.remove();
      return;
    }
    const existing = [...canvas.querySelectorAll(".dash-card")].filter(
      (c) => c.dataset.id === id && c !== evt.item
    );
    if (existing.length) {
      evt.item.remove();
      setStatus("すでに追加済み");
      refreshPaletteState();
      return;
    }
    if (evt.item.classList.contains("pal-item")) {
      const card = makeCard(id, "default");
      if (!card) {
        evt.item.remove();
        return;
      }
      evt.item.replaceWith(card);
    }
    refreshPaletteState();
    setStatus("未保存");
  },
  onUpdate: () => setStatus("未保存"),
  onRemove: () => {
    refreshPaletteState();
    setStatus("未保存");
  },
});

load();
