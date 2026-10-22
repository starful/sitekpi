/* Anchored popover — opens next to the clicked element.
   Openers: [data-pop-open="<id>"] clones <template id="pop-<id>"> into #pop.
   Forms inside with [data-bench-form] / [data-json-form] post via fetch (Accept: JSON) and reload. */
(function () {
  const pop = document.getElementById("pop");
  if (!pop) return;
  let anchor = null;

  function place() {
    if (!anchor || pop.hidden) return;
    const gap = 8, pad = 12;
    const r = anchor.getBoundingClientRect();
    const vw = document.documentElement.clientWidth, vh = window.innerHeight;
    pop.style.maxHeight = "";
    const w = pop.offsetWidth, h = pop.offsetHeight;
    let left = r.left + r.width / 2 - w / 2;
    left = Math.max(pad, Math.min(left, vw - w - pad));
    const below = vh - r.bottom - gap - pad, above = r.top - gap - pad;
    let top, side;
    if (h <= below || below >= above) {
      top = r.bottom + gap; side = "below";
      if (h > below) pop.style.maxHeight = Math.max(160, below) + "px";
    } else {
      top = Math.max(pad, r.top - gap - Math.min(h, above)); side = "above";
      if (h > above) pop.style.maxHeight = above + "px";
    }
    pop.style.left = left + window.scrollX + "px";
    pop.style.top = top + window.scrollY + "px";
    pop.dataset.side = side;
    const ax = Math.max(14, Math.min(w - 14, r.left + r.width / 2 - left));
    pop.style.setProperty("--arrow-x", ax + "px");
  }

  function close() {
    if (pop.hidden) return;
    pop.hidden = true;
    pop.innerHTML = "";
    if (anchor) { anchor.setAttribute("aria-expanded", "false"); anchor.focus({ preventScroll: true }); }
    anchor = null;
  }

  function open(id, el) {
    const tpl = document.getElementById("pop-" + id);
    if (!tpl) return;
    if (anchor && anchor !== el) anchor.setAttribute("aria-expanded", "false");
    anchor = el;
    pop.innerHTML = "";
    pop.appendChild(tpl.content.cloneNode(true));
    pop.hidden = false;
    pop.dataset.popId = id;
    el.setAttribute("aria-expanded", "true");
    place();
    const first = pop.querySelector("input:not([type=hidden]), select, .pop-row, button.primary");
    if (first) first.focus({ preventScroll: true });
  }

  document.addEventListener("click", (e) => {
    const opener = e.target.closest("[data-pop-open]");
    if (opener) {
      e.preventDefault();
      e.stopPropagation();
      const inside = pop.contains(opener);
      const id = opener.dataset.popOpen;
      /* rows inside the list popover keep the list's anchor */
      const el = inside && opener.hasAttribute("data-pop-keep-anchor") ? anchor : opener;
      if (!inside && anchor === opener && !pop.hidden) { close(); return; }
      open(id, el);
      return;
    }
    if (e.target.closest("[data-pop-close]")) { close(); return; }
    if (!pop.hidden && !pop.contains(e.target)) close();
  });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") close(); });
  window.addEventListener("resize", place);
  window.addEventListener("scroll", place, { passive: true });

  async function post(action, body) {
    const res = await fetch(action, {
      method: "POST",
      body,
      headers: { Accept: "application/json" },
      credentials: "same-origin",
    });
    let data = {};
    try { data = await res.json(); } catch (_) { /* non-JSON */ }
    return { ok: res.ok && data.ok !== false, data };
  }

  function showError(form, data) {
    const box = form.querySelector("[data-pop-error]");
    const msgs = Object.values((data && data.errors) || {});
    if (box) { box.textContent = msgs[0] || (data && data.error) || "Error"; box.hidden = false; }
    form.querySelectorAll("input").forEach((i) => i.setAttribute("aria-invalid", msgs.length ? "true" : "false"));
  }

  pop.addEventListener("submit", async (e) => {
    const form = e.target.closest("form");
    if (!form || !(form.matches("[data-bench-form], [data-bench-reset-all], [data-json-form]"))) return;
    e.preventDefault();
    const btn = form.querySelector("[type=submit]");
    if (btn) btn.disabled = true;
    const r = await post(form.getAttribute("action"), new FormData(form));
    if (r.ok) { location.reload(); return; }
    if (btn) btn.disabled = false;
    showError(form, r.data);
  });

  pop.addEventListener("click", async (e) => {
    const b = e.target.closest("[data-bench-reset]");
    if (!b) return;
    e.preventDefault();
    const form = b.closest("form");
    const fd = new FormData();
    fd.append("pack", form.elements.pack.value);
    fd.append("board", form.elements.board.value);
    fd.append("metric", b.dataset.benchReset);
    b.disabled = true;
    const r = await post("/benchmarks/reset", fd);
    if (r.ok) location.reload(); else { b.disabled = false; showError(form, r.data); }
  });

  /* old #bench links → open the list next to the header button */
  if (location.hash === "#bench") {
    const btn = document.querySelector('[data-pop-open="bench-all"]');
    if (btn) { history.replaceState(null, "", location.pathname + location.search); btn.scrollIntoView({ block: "center" }); open("bench-all", btn); }
  }
  window.SiteKPIPop = { open, close };
})();
