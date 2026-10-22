/* GA4 connect: A 訪問者の行動 (flow, editable) × B 業種 (standards) */
(function () {
  const form = document.querySelector("[data-choose]");
  if (!form) return;
  const C = window.SITEKPI_CONNECT || {};
  const tpl = document.getElementById("fe-step-tpl");
  const sum = form.querySelector("[data-beh-summary]");
  const scope = form.querySelector("[data-ind-scope]");
  const groups = form.querySelector("[data-ind-groups]");

  const checked = (name) => form.querySelector(`input[name=${name}]:checked`);

  function renumber(list) {
    let n = 0;
    list.querySelectorAll("[data-fe-step]").forEach((li) => { n += 1; li.querySelector(".fe-num").textContent = n; });
    const add = list.closest(".fe-body").querySelector("[data-fe-add]");
    if (add) add.disabled = n >= Number(list.dataset.max || 6);
    list.querySelectorAll("[data-fe-del]").forEach((b) => { b.disabled = n <= 1; });
  }

  function newRow(cat, step) {
    const li = tpl.content.firstElementChild.cloneNode(true);
    li.querySelectorAll("[data-n]").forEach((el) => { el.name = `${cat}-${el.dataset.n}`; });
    if (step) {
      li.querySelector("[data-n=key]").value = step.key;
      li.querySelector("[data-n=event]").value = step.event;
      li.querySelector("[data-n=label]").value = step.label;
    }
    return li;
  }

  function edited(box) { const f = box.querySelector("[data-fe-edited]"); if (f) f.value = "1"; }

  function sync() {
    const b = checked("behavior");
    const i = checked("industry");
    const cat = b ? b.value : "";
    form.querySelectorAll(".beh-card").forEach((c) => c.classList.toggle("is-selected", c.dataset.beh === cat));
    form.querySelectorAll("[data-edit]").forEach((e) => { e.hidden = e.dataset.edit !== cat; });
    /* industries of the same kind first: their funnel standards apply too */
    form.querySelectorAll(".ind-group").forEach((g) => g.classList.toggle("is-match", g.dataset.cat === cat));
    if (groups && cat) {
      const match = groups.querySelector(`.ind-group[data-cat="${cat}"]`);
      if (match) groups.prepend(match);
    }
    if (scope) {
      scope.hidden = !(b && i);
      if (b && i) scope.textContent = i.dataset.cat === cat ? C.scopeAll : C.scopeSite;
    }
    const parts = [b && b.dataset.label, i && i.dataset.label].filter(Boolean);
    if (parts.length) {
      sum.textContent = "";
      sum.append(C.prefix || "");
      const s = document.createElement("strong"); s.textContent = parts.join(C.join || " × "); sum.append(s);
    }
  }

  form.addEventListener("change", (e) => {
    if (e.target.closest("[data-edit]")) edited(e.target.closest("[data-edit]"));
    sync();
  });
  form.addEventListener("input", (e) => { const box = e.target.closest("[data-edit]"); if (box) edited(box); });

  form.addEventListener("click", (e) => {
    const box = e.target.closest("[data-edit]");
    if (!box) return;
    const list = box.querySelector("[data-fe-steps]");
    const row = e.target.closest("[data-fe-step]");
    if (e.target.closest("[data-fe-toggle]")) {
      const body = box.querySelector("[data-fe-body]");
      body.hidden = !body.hidden;
      return;
    }
    if (!list) return;
    if (e.target.closest("[data-fe-up]") && row) {
      const prev = row.previousElementSibling;
      if (prev && prev.matches("[data-fe-step]")) list.insertBefore(row, prev);
    } else if (e.target.closest("[data-fe-down]") && row) {
      const next = row.nextElementSibling;
      if (next) list.insertBefore(next, row);
    } else if (e.target.closest("[data-fe-del]") && row) {
      if (list.querySelectorAll("[data-fe-step]").length > 1) row.remove();
    } else if (e.target.closest("[data-fe-add]")) {
      const r = newRow(box.dataset.edit);
      list.append(r);
      r.querySelector("[data-n=label]").focus();
    } else if (e.target.closest("[data-fe-reset]")) {
      list.querySelectorAll("[data-fe-step]").forEach((li) => li.remove());
      JSON.parse(box.dataset.std || "[]").forEach((st) => list.append(newRow(box.dataset.edit, st)));
    } else {
      return;
    }
    edited(box);
    renumber(list);
  });

  form.querySelectorAll("[data-fe-steps]").forEach(renumber);
  sync();
})();
