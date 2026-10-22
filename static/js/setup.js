/* サイトの設定 ③: adjust the flow (rename, change event, add / remove / reorder) */
(function () {
  const form = document.querySelector("[data-adjust]");
  if (!form) return;
  const A = window.SITEKPI_ADJUST || { counts: {}, std: [] };
  const list = form.querySelector("[data-steps]");
  const tpl = document.getElementById("adj-step-tpl");
  const max = Number(form.dataset.max || 6);
  const fmt = (n) => Number(n).toLocaleString();

  function status(li) {
    const sel = li.querySelector("[data-event]");
    const out = li.querySelector("[data-status]");
    if (!sel || !out || !Object.keys(A.counts).length) return;
    const c = A.counts[sel.value];
    li.classList.toggle("is-missing", !c);
    out.textContent = c ? "✓ " + A.found.replace("{n}", fmt(c)) : (sel.value ? "⚠ " + A.notFound : "");
  }

  function banner() {
    const warn = document.querySelector("[data-banner-missing]");
    const ok = document.querySelector("[data-banner-ok]");
    if (!warn || !ok) return;
    const n = [...list.querySelectorAll("[data-step]")].filter((li) => !A.counts[li.querySelector("[data-event]").value]).length;
    warn.hidden = n === 0;
    ok.hidden = n !== 0;
    if (n) warn.textContent = A.missing.replace("{n}", n);
  }

  function renumber() {
    banner();
    const rows = list.querySelectorAll("[data-step]");
    rows.forEach((li, i) => { li.querySelector(".adj-num").textContent = i + 1; });
    form.querySelector("[data-add]").disabled = rows.length >= max;
    rows.forEach((li) => { li.querySelector("[data-del]").disabled = rows.length <= 1; });
  }

  function row(step) {
    const li = tpl.content.firstElementChild.cloneNode(true);
    if (step) {
      li.querySelector("[name=key]").value = step.key;
      li.querySelector("[name=label]").value = step.label;
      const sel = li.querySelector("[data-event]");
      if (![...sel.options].some((o) => o.value === step.event)) {
        const o = new Option(`${step.event}（${A.none}）`, step.event);
        sel.insertBefore(o, sel.options[1] || null);
      }
      sel.value = step.event;
    }
    return li;
  }

  form.addEventListener("change", (e) => {
    const li = e.target.closest("[data-step]");
    if (li && e.target.matches("[data-event]")) {
      status(li);
      banner();
      const label = li.querySelector("[name=label]");
      if (label && !label.value) label.value = e.target.value;
    }
  });

  form.addEventListener("click", (e) => {
    const li = e.target.closest("[data-step]");
    if (e.target.closest("[data-up]") && li) {
      const prev = li.previousElementSibling;
      if (prev && prev.matches("[data-step]")) list.insertBefore(li, prev);
    } else if (e.target.closest("[data-down]") && li) {
      const next = li.nextElementSibling;
      if (next) list.insertBefore(next, li);
    } else if (e.target.closest("[data-del]") && li) {
      if (list.querySelectorAll("[data-step]").length > 1) li.remove();
    } else if (e.target.closest("[data-add]")) {
      const r = row();
      list.append(r);
      r.querySelector("[data-event]").focus();
    } else if (e.target.closest("[data-reset]")) {
      list.querySelectorAll("[data-step]").forEach((x) => x.remove());
      A.std.forEach((s) => { const r = row(s); list.append(r); status(r); });
    } else {
      return;
    }
    renumber();
  });
  renumber();
})();
