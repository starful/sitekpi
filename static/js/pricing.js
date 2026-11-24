// 料金ページ: monthly/yearly toggle swaps which pr-price-note is shown (price itself is TBD either way).
(function () {
  "use strict";
  const toggle = document.querySelector(".pr-toggle");
  if (!toggle) return;

  toggle.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-cycle]");
    if (!btn) return;
    const cycle = btn.dataset.cycle;
    toggle.querySelectorAll("[data-cycle]").forEach((b) => {
      const on = b === btn;
      b.classList.toggle("is-on", on);
      b.setAttribute("aria-pressed", on ? "true" : "false");
    });
    document.querySelectorAll("[data-cycle-note]").forEach((note) => {
      note.hidden = note.dataset.cycleNote !== cycle;
    });
  });
})();
