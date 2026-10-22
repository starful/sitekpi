/* Rail: mobile drawer + sample-pack search (all pages) */
(function () {
  if (window.__sitekpiRail) return;
  window.__sitekpiRail = true;
  const body = document.body;
  const btn = document.querySelector("[data-rail-toggle]");
  const rail = document.getElementById("rail");
  if (!btn || !rail) return;
  const set = (open) => {
    body.classList.toggle("rail-open", open);
    btn.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) { const f = rail.querySelector("a, input, button"); if (f) f.focus(); }
  };
  btn.addEventListener("click", () => set(!body.classList.contains("rail-open")));
  rail.querySelectorAll("[data-rail-close]").forEach((el) =>
    el.addEventListener("click", () => { set(false); btn.focus(); }));
  document.addEventListener("click", (e) => {
    if (body.classList.contains("rail-open") && !rail.contains(e.target) && !btn.contains(e.target)) set(false);
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && body.classList.contains("rail-open")) { set(false); btn.focus(); }
  });
  rail.querySelectorAll("a[href]").forEach((a) => a.addEventListener("click", () => set(false)));
})();

(function () {
  if (window.__sitekpiPackSearch) return;
  window.__sitekpiPackSearch = true;
  const input = document.querySelector("[data-pack-search]");
  const empty = document.querySelector("[data-pack-search-empty]");
  const nav = document.querySelector("[data-pack-nav]");
  if (!input || !nav) return;
  const cats = () => Array.from(nav.querySelectorAll(".pack-cat"));
  input.addEventListener("input", () => {
    const q = (input.value || "").trim().toLowerCase();
    let any = false;
    cats().forEach((cat) => {
      let hit = false;
      cat.querySelectorAll(".pack-cat-body a").forEach((a) => {
        const hay = (a.getAttribute("data-pack-q") || a.textContent || "").toLowerCase();
        const show = !q || hay.includes(q);
        a.hidden = !show;
        if (show) hit = true;
      });
      cat.hidden = Boolean(q) && !hit;
      if (q && hit) cat.open = true;
      if (hit) any = true;
    });
    if (empty) empty.hidden = !(q && !any);
  });
})();
