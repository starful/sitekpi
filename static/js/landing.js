// Landing page on phones: feature accordion, sample rail dots, FAQ "more", sticky connect bar.
(function () {
  "use strict";
  const sp = window.matchMedia("(max-width: 640px)");

  document.querySelectorAll("[data-lp-acc] .lp-acc-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (!sp.matches) return;
      const box = btn.closest("[data-lp-acc]");
      const open = !box.classList.contains("is-open");
      box.classList.toggle("is-open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });

  const rail = document.querySelector("[data-lp-rail]");
  if (rail) {
    const cards = Array.from(rail.children);
    const dots = document.createElement("div");
    dots.className = "lp-rail-dots";
    dots.setAttribute("aria-hidden", "true");
    const hint = document.createElement("span");
    hint.textContent = rail.dataset.hint || "";
    const row = document.createElement("div");
    row.className = "lp-rail-nav";
    cards.forEach(() => dots.appendChild(document.createElement("i")));
    const next = document.createElement("button");
    next.type = "button";
    next.className = "lp-rail-next";
    next.setAttribute("aria-label", rail.dataset.hint || "next");
    next.textContent = "→";
    row.append(dots, hint, next);
    rail.after(row);
    const step = () => (cards[1] ? cards[1].offsetLeft - cards[0].offsetLeft : rail.clientWidth);
    const sync = () => {
      const i = Math.round(rail.scrollLeft / Math.max(1, step()));
      dots.querySelectorAll("i").forEach((d, k) => d.classList.toggle("is-on", k === i));
      rail.classList.toggle("is-end", rail.scrollLeft + rail.clientWidth >= rail.scrollWidth - 4);
    };
    next.addEventListener("click", () => {
      const end = rail.scrollLeft + rail.clientWidth >= rail.scrollWidth - 4;
      rail.scrollTo({ left: end ? 0 : rail.scrollLeft + step(), behavior: "smooth" });
    });
    rail.addEventListener("scroll", sync, { passive: true });
    sync();
  }

  const all = document.querySelector("[data-lp-faq-all]");
  if (all) all.addEventListener("click", () => {
    document.querySelectorAll(".lp-faq-more").forEach((d) => d.classList.remove("lp-faq-more"));
    all.remove();
  });

  const bar = document.querySelector("[data-lp-sp-cta]");
  if (bar && "IntersectionObserver" in window) {
    const seen = new Set();
    const io = new IntersectionObserver((es) => {
      es.forEach((e) => (e.isIntersecting ? seen.add(e.target) : seen.delete(e.target)));
      bar.classList.toggle("is-hidden", seen.size > 0);
    });
    document.querySelectorAll(".lp-hero .lp-actions, .lp-final, .pub-foot").forEach((el) => io.observe(el));
  }
})();
