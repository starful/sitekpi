/* ダッシュボードを作る: purpose templates → sections of metric cards → add drawer.
   Saved in this browser (localStorage). Data: #builder-data (views/builder.py). Every value is set with textContent. */
(function () {
  const D = JSON.parse(document.getElementById("builder-data").textContent);
  const CATALOG = D.catalog;
  const L = D.i18n;
  const KEY = "sitekpi.builder.v4";
  const OLD_KEYS = ["kpistarter.builder.v3", "kpistarter.builder.v2", "kpistarter.builder.v1"];
  const KIND_OF = { digital: "digital", event: "event", traffic: "traffic", business: "business" };

  const $ = (id) => document.getElementById(id);
  const el = (tag, cls, text) => {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  };
  const fill = (tpl, map) => Object.keys(map).reduce((s, k) => s.split("{" + k + "}").join(map[k]), tpl);
  const isEmpty = (v) => ["", "—", "-", "–", "N/A", "n/a"].includes(String(v == null ? "" : v).trim());
  const store = {
    get(k) { try { return JSON.parse(localStorage.getItem(k) || "null"); } catch (_) { return null; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch (_) { return false; } },
  };

  const sectionsEl = $("sections");
  const statusEl = $("status");
  const drawer = $("drawer");
  let state = null;          // { tpl, sections: [{title, ids}] }
  let target = null;         // index of the section the drawer adds to
  let kind = "";

  const clone = (secs) => secs.map((s) => ({ title: s.title, ids: s.ids.slice() }));
  const fromTpl = (id) => ({ tpl: id, sections: clone(D.templates[id] || D.templates.blank) });

  /* v3 and older: a flat list of {type: section|widget}. A section starts a new group. */
  function migrate(raw) {
    if (!Array.isArray(raw)) return null;
    const secs = [];
    for (const x of raw) {
      const item = typeof x === "string" ? { type: "widget", id: x } : x;
      if (!item) continue;
      if (item.type === "section") secs.push({ title: item.title || L.new, ids: [] });
      else if (item.id && CATALOG[item.id]) {
        if (!secs.length) secs.push({ title: L.new, ids: [] });
        secs[secs.length - 1].ids.push(item.id);
      }
    }
    return secs.length ? { tpl: "", sections: secs } : null;
  }

  function loadState() {
    const v4 = store.get(KEY);
    if (v4 && Array.isArray(v4.sections)) {
      v4.sections = v4.sections.map((s) => ({ title: String(s.title || L.new), ids: (s.ids || []).filter((i) => CATALOG[i]) }));
      return v4;
    }
    for (const k of OLD_KEYS) {
      const m = migrate(store.get(k));
      if (m) return m;
    }
    return null;
  }

  function setSaved(saved) {
    statusEl.textContent = saved ? L.saved : L.unsaved;
    statusEl.classList.toggle("is-dirty", !saved);
  }
  function changed() { setSaved(false); }

  /* ---------- templates ---------- */
  function renderTpls() {
    document.querySelectorAll("[data-tpl]").forEach((b) => {
      b.setAttribute("aria-checked", b.dataset.tpl === state.tpl ? "true" : "false");
    });
  }
  document.querySelectorAll("[data-tpl]").forEach((b) => b.addEventListener("click", () => {
    if (window.SiteKPITrack) window.SiteKPITrack("builder_template", { template: b.dataset.tpl });
    state = fromTpl(b.dataset.tpl);
    closeDrawer();
    render();
    changed();
  }));

  /* ---------- sections ---------- */
  function card(id, si) {
    const m = CATALOG[id] || {};
    const c = el("div", "bx-card");
    c.dataset.id = id;
    const top = el("div", "bx-card-top");
    top.appendChild(el("span", "bx-card-name", m.label || id));
    const x = el("button", "bx-card-x", "×");
    x.type = "button";
    x.setAttribute("aria-label", L.remove + ": " + (m.label || id));
    x.addEventListener("click", () => {
      state.sections[si].ids = state.sections[si].ids.filter((i) => i !== id);
      render();
      changed();
    });
    top.appendChild(x);
    c.appendChild(top);
    const v = m.value;
    c.appendChild(el("span", "bx-card-value" + (isEmpty(v) ? " is-empty" : ""), isEmpty(v) ? "—" : String(v)));
    if (m.hint) c.appendChild(el("span", "bx-card-hint", m.hint));
    return c;
  }

  function render() {
    renderTpls();
    const nodes = state.sections.map((s, si) => {
      const sec = el("section", "bx-sec");
      const head = el("div", "bx-sec-head");
      const title = el("input", "bx-sec-title");
      title.type = "text";
      title.maxLength = 40;
      title.value = s.title;
      title.setAttribute("aria-label", L.heading);
      title.addEventListener("input", () => {
        s.title = title.value;
        if (target === si) drawerTitle();
        changed();
      });
      head.appendChild(title);
      head.appendChild(el("span", "bx-sec-n", fill(L.n_metrics, { n: s.ids.length })));
      if (state.sections.length > 1) {
        const del = el("button", "bx-sec-del", L.remove_section);
        del.type = "button";
        del.addEventListener("click", () => {
          state.sections.splice(si, 1);
          if (target !== null) closeDrawer();
          render();
          changed();
        });
        head.appendChild(del);
      }
      sec.appendChild(head);

      const grid = el("div", "bx-cards");
      grid.dataset.si = si;
      s.ids.forEach((id) => grid.appendChild(card(id, si)));
      if (!s.ids.length) grid.appendChild(el("p", "bx-empty", L.empty));
      const add = el("button", "bx-add" + (target === si ? " is-on" : ""), L.add_metric);
      add.type = "button";
      add.addEventListener("click", () => openDrawer(si));
      grid.appendChild(add);
      sec.appendChild(grid);
      return sec;
    });
    sectionsEl.replaceChildren(...nodes);
    makeSortable();
    if (target !== null) renderPicks();
  }

  /* drag to reorder (also between sections) — the DOM order becomes the state */
  function makeSortable() {
    if (!window.Sortable) return;
    sectionsEl.querySelectorAll(".bx-cards").forEach((grid) => {
      window.Sortable.create(grid, {
        group: "cards", animation: 150, draggable: ".bx-card", filter: ".bx-card-x", preventOnFilter: false,
        onEnd: () => {
          sectionsEl.querySelectorAll(".bx-cards").forEach((g) => {
            state.sections[Number(g.dataset.si)].ids = [...g.querySelectorAll(".bx-card")].map((c) => c.dataset.id);
          });
          render();
          changed();
        },
      });
    });
  }

  $("btn-add-section").addEventListener("click", () => {
    state.sections.push({ title: L.new, ids: [] });
    openDrawer(state.sections.length - 1);
    changed();
  });

  /* ---------- add drawer ---------- */
  function drawerTitle() {
    $("drawer-title").textContent = fill(L.drawer, { name: state.sections[target].title || L.new });
  }
  function openDrawer(si) {
    target = si;
    drawer.hidden = false;
    drawerTitle();
    render();
    $("drawer-q").focus();
  }
  function closeDrawer() {
    target = null;
    drawer.hidden = true;
    sectionsEl.querySelectorAll(".bx-add.is-on").forEach((b) => b.classList.remove("is-on"));
  }
  $("drawer-close").addEventListener("click", closeDrawer);
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !drawer.hidden) closeDrawer(); });

  function renderPicks() {
    const q = $("drawer-q").value.trim().toLowerCase();
    const here = new Set(state.sections[target].ids);
    const ids = (D.order || Object.keys(CATALOG)).filter((id) => {
      const m = CATALOG[id];
      if (!m) return false;
      if (!KIND_OF[m.group]) return false;
      if (kind && m.group !== kind) return false;
      return !q || (id + " " + (m.label || "") + " " + (m.hint || "")).toLowerCase().includes(q);
    });
    const list = $("drawer-list");
    if (!ids.length) { list.replaceChildren(el("li", "bx-picks-empty", L.no_match)); return; }
    list.replaceChildren(...ids.map((id) => {
      const m = CATALOG[id];
      const on = here.has(id);
      const li = el("li", "bx-pick");
      const name = el("span", "bx-pick-name", m.label || id);
      name.appendChild(el("small", null, (isEmpty(m.value) ? "—" : String(m.value)) + (m.hint ? " · " + m.hint : "")));
      const b = el("button", "bx-pick-btn", on ? "✓" : "＋");
      b.type = "button";
      b.setAttribute("aria-pressed", on ? "true" : "false");
      b.setAttribute("aria-label", fill(L.add_x, { name: m.label || id }));
      b.addEventListener("click", () => {
        if (on) return;
        if (window.SiteKPITrack) window.SiteKPITrack("builder_metric_add", { metric: id });
        state.sections[target].ids.push(id);
        render();
        changed();
      });
      li.append(name, b);
      return li;
    }));
  }
  $("drawer-q").addEventListener("input", renderPicks);
  document.querySelectorAll("#drawer-kinds [data-kind]").forEach((b) => b.addEventListener("click", () => {
    kind = b.dataset.kind;
    document.querySelectorAll("#drawer-kinds [data-kind]").forEach((x) => {
      const on = x === b;
      x.classList.toggle("is-on", on);
      x.setAttribute("aria-pressed", on ? "true" : "false");
    });
    renderPicks();
  }));

  /* ---------- save ---------- */
  $("btn-save").addEventListener("click", () => {
    if (store.set(KEY, state)) setSaved(true);
  });

  /* ---------- live values (GA4) ---------- */
  async function fetchLive() {
    try {
      const res = await fetch("/builder/values", { headers: { Accept: "application/json" } });
      const j = await res.json();
      (j.widgets || []).forEach((w) => {
        if (!CATALOG[w.id]) return;
        CATALOG[w.id].value = w.value;
        if (w.hint) CATALOG[w.id].hint = w.hint;
      });
      const banner = $("live-banner");
      if (banner && D.loadedMsg) banner.textContent = banner.textContent.replace(" · " + D.loadingMsg, "");
      render();
    } catch (_) { /* keep — values */ }
  }

  const saved = loadState();
  state = saved || fromTpl("weekly");
  render();
  if (saved) setSaved(true); else statusEl.textContent = "";
  if (D.liveFetch) fetchLive();
})();
