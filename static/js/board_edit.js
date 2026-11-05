/* The board's 編集モード (「どこで離れているか」 → 流れを直す) and the 比べる業種 drawer preview.
   Data: #setup-data (views/setup.flow_editor_context) · #ind-data (views/setup.render_industry).
   Every value is set with textContent. Saving posts the form to /setup (→ /live). */
(function () {
  const el = (tag, cls, text) => {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  };
  const fmt = (n) => Number(n).toLocaleString();
  const $ = (s) => document.querySelector(s);

  /* ---------- 比べる業種: the preview follows the chosen card ---------- */
  const indData = document.getElementById("ind-data");
  if (indData) {
    const D = JSON.parse(indData.textContent);
    const rows = $("[data-ind-rows]");
    const title = $("[data-ind-title]");
    document.querySelectorAll("[data-ind]").forEach((r) => r.addEventListener("change", () => {
      const list = D.previews[r.value] || [];
      rows.replaceChildren(...list.map((x) => {
        const row = el("div", "sx-ind-row");
        const m = el("span", "sx-ind-metric", x.label);
        m.appendChild(el("small", null, D.you + " " + x.you + " · " + D.bench + " " + x.bench));
        row.append(m, el("span", "sx-gap tone-" + (x.judge || "na"), x.gap));
        if (x.judge) row.appendChild(el("span", "judge judge-" + x.judge, D.judge[x.judge]));
        else if (x.none) row.appendChild(el("span", "judge judge-none", D.none));
        else row.appendChild(el("span", "judge-na", "—"));
        return row;
      }));
      title.textContent = D.title_tpl.replace("__N__", D.labels[r.value] || "");
    }));
  }

  /* ---------- 編集モード ---------- */
  const dataEl = document.getElementById("setup-data");
  const section = $("[data-editable]");
  if (!dataEl || !section) return;
  const D = JSON.parse(dataEl.textContent);
  const L = D.i18n;
  const bar = $("[data-edit-bar]");
  const view = $("[data-flow-view]");
  const track = $("[data-edit-track]");
  const flowEl = track.querySelector("[data-flow]");
  const original = { behavior: D.behavior, steps: D.steps.map((s) => ({ ...s })) };
  let state = { behavior: D.behavior, steps: D.steps.map((s) => ({ ...s })), sel: -1 };
  let showAll = false;
  let removed = []; // [{ at, step }] — 「× 外す」, undone in reverse order
  const count = (ev) => (ev && D.counts[ev]) || 0;

  function setEditing(on) {
    section.classList.toggle("is-editing", on);
    bar.hidden = !on;
    track.hidden = !on;
    if (view) view.hidden = on;
    if (on) { render(); section.scrollIntoView({ block: "start" }); }
    else { state.sel = -1; window.SiteDrawer.close(); }
  }

  function renderFlow() {
    const items = [];
    const entry = el("li", "sx-step is-entry");
    const box = el("div", "sx-box");
    const bar0 = el("span", "sx-bar");
    const fill = el("i");
    fill.style.height = "100%";
    bar0.appendChild(fill);
    box.append(bar0, el("span", "sx-step-label", L.entry));
    const u = el("span", "sx-users");
    u.append(el("strong", null, D.entry ? fmt(D.entry) : "—"));
    box.appendChild(u);
    entry.appendChild(box);
    items.push(entry);
    let prev = D.entry;
    let worst = null;
    state.steps.forEach((s, i) => {
      const n = count(s.event);
      const go = n && prev ? Math.min(100, (n / prev) * 100) : null;
      if (go !== null && (worst === null || 100 - go > worst.drop)) worst = { drop: 100 - go, at: i };
      if (n) prev = n;
      const li = el("li", "sx-step" + (n ? "" : " is-missing") + (i === state.sel ? " is-on" : "") + (i === state.steps.length - 1 ? " is-last" : ""));
      const link = el("div", "sx-link-col");
      link.append(el("span", "sx-arrow"), el("b", "sx-go", go === null ? "—" : go.toFixed(1) + "%"));
      const add = el("button", "sx-add", "＋");
      add.type = "button";
      add.title = L.add_here;
      add.setAttribute("aria-label", L.add_here);
      add.addEventListener("click", () => insertAt(i));
      link.appendChild(add);
      const b = el("button", "sx-box");
      b.type = "button";
      b.setAttribute("aria-pressed", i === state.sel ? "true" : "false");
      b.addEventListener("click", () => select(i, b));
      const bar2 = el("span", "sx-bar");
      const f2 = el("i");
      f2.style.height = (n && D.entry ? Math.max(3, Math.min(100, (n / D.entry) * 100)) : 0) + "%";
      bar2.appendChild(f2);
      b.append(bar2, el("span", "sx-step-label", s.label || "—"), el("code", "sx-ev", s.event || L.no_event));
      const users = el("span", "sx-users");
      if (n) users.append(el("strong", null, fmt(n)));
      else users.append(el("span", "sx-none", L.none));
      b.appendChild(users);
      if (i === state.steps.length - 1) b.appendChild(el("span", "sx-primary-tag", L.primary));
      li.append(link, b);
      if (i < state.steps.length - 1 && state.steps.length > 1) { // the last step is the 主転換: keep it
        const rm = el("button", "sx-remove", L.remove_step);
        rm.type = "button";
        rm.setAttribute("aria-label", (s.label || "") + " " + L.remove_step);
        rm.addEventListener("click", () => {
          removed.push({ at: i, step: state.steps[i] });
          state.steps.splice(i, 1);
          state.sel = -1;
          window.SiteDrawer.close();
          render();
        });
        li.appendChild(rm);
      }
      items.push(li);
    });
    if (worst) items[worst.at + 1].classList.add("is-worst");
    flowEl.replaceChildren(...items);
    const miss = state.steps.filter((s) => !count(s.event)).length;
    const cover = track.querySelector("[data-cover]");
    cover.textContent = miss ? L.missing.replace("{n}", miss) : L.all_ok;
    cover.classList.toggle("is-warn", !!miss);
    if (removed.length) {
      const names = removed.map((r) => "「" + (r.step.label || r.step.event || "—") + "」").join(" ");
      const line = el("span", "sx-removed", " · " + L.removed.replace("{names}", names) + " ");
      const undo = el("button", "sx-undo", L.undo);
      undo.type = "button";
      undo.addEventListener("click", () => {
        while (removed.length) { const r = removed.pop(); state.steps.splice(Math.min(r.at, state.steps.length), 0, r.step); }
        render();
      });
      line.appendChild(undo);
      cover.appendChild(line);
    }
  }

  function renderEditor() {
    const s = state.steps[state.sel];
    if (!s) return;
    const last = state.sel === state.steps.length - 1;
    $("[data-edit-title]").textContent = (last ? L.step_last : L.step_n).replace("{n}", state.sel + 1);
    $("[data-label]").value = s.label || "";
    $("[data-event-input]").value = !D.counts[s.event] ? s.event : "";
    const top = D.events.slice(0, 12);
    const list = showAll ? D.events : top.concat(D.events.slice(12).filter((e) => e.name === s.event));
    const nodes = list.map((e) => {
      const b = el("button", "sx-evbtn");
      b.type = "button";
      b.setAttribute("aria-pressed", s.event === e.name ? "true" : "false");
      b.append(el("code", null, e.name), el("span", null, fmt(e.count)));
      b.addEventListener("click", () => { state.steps[state.sel].event = e.name; render(); });
      return b;
    });
    if (D.events.length > 12) {
      const more = el("button", "sx-more-ev", showAll ? L.fewer : L.more.replace("{n}", D.events.length));
      more.type = "button";
      more.addEventListener("click", () => { showAll = !showAll; renderEditor(); });
      nodes.push(more);
    }
    $("[data-events]").replaceChildren(...nodes);
  }

  function syncForm() {
    $("[data-behavior]").value = state.behavior;
    const inputs = [];
    state.steps.forEach((s) => {
      for (const [k, v] of [["key", s.key || ""], ["event", s.event || ""], ["label", s.label || ""]]) {
        const inp = document.createElement("input");
        inp.type = "hidden";
        inp.name = k;
        inp.value = v;
        inputs.push(inp);
      }
    });
    $("[data-hidden]").replaceChildren(...inputs);
  }

  function render() { renderFlow(); renderEditor(); syncForm(); }

  function select(i, from) {
    state.sel = i;
    render();
    window.SiteDrawer.open("step", from);
  }
  function insertAt(i) {
    if (state.steps.length >= D.max) { warn(L.too_many); return; }
    state.steps.splice(i, 0, { key: "", event: "", label: L.new_step });
    select(i);
    $("[data-label]").focus();
  }
  function warn(msg) {
    const c = track.querySelector("[data-cover]");
    c.textContent = msg;
    c.classList.add("is-warn");
  }

  $("[data-label]").addEventListener("input", (e) => {
    if (state.sel < 0) return;
    state.steps[state.sel].label = e.target.value;
    renderFlow(); syncForm();
  });
  $("[data-event-input]").addEventListener("change", (e) => {
    const v = e.target.value.trim();
    if (state.sel < 0 || !v || !/^[A-Za-z0-9_]+$/.test(v)) return;
    state.steps[state.sel].event = v;
    render();
  });
  $("[data-remove]").addEventListener("click", () => {
    if (state.steps.length <= 1) { warn(L.min_one); return; }
    state.steps.splice(state.sel, 1);
    state.sel = -1;
    window.SiteDrawer.close();
    render();
  });
  $("[data-template]").addEventListener("change", (e) => {
    state.behavior = e.target.value;
    state.steps = (D.templates[state.behavior] || []).map((s) => ({ ...s }));
    state.sel = -1;
    removed = [];
    window.SiteDrawer.close();
    render();
  });
  document.querySelectorAll("[data-edit-open]").forEach((b) => b.addEventListener("click", () => setEditing(true)));
  /* 「この段を直す」 on a 記録なし step: 編集モード with that step already open in the drawer */
  document.querySelectorAll("[data-edit-step]").forEach((b) => b.addEventListener("click", () => {
    const i = state.steps.findIndex((s) => s.key === b.dataset.editStep);
    setEditing(true);
    if (i >= 0) select(i, flowEl.children[i + 1]?.querySelector(".sx-box"));
  }));
  $("[data-edit-close]").addEventListener("click", () => {
    state = { behavior: original.behavior, steps: original.steps.map((s) => ({ ...s })), sel: -1 };
    removed = [];
    $("[data-template]").value = original.behavior;
    setEditing(false);
  });
  document.addEventListener("drawer:close", () => {
    if (state.sel >= 0) { state.sel = -1; if (!track.hidden) renderFlow(); }
  });
  const auto = JSON.parse(document.getElementById("board-data").textContent).auto_open;
  if (auto === "edit") setEditing(true);
})();
