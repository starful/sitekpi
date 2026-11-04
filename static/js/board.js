/* KPI board: 説明 cards, 詳しい数字 (loaded after the page, collapsible groups), the page menu,
   right-top drawers, 行動フロー channel switch. Data: #board-data */
const BOARD = JSON.parse(document.getElementById("board-data").textContent);

/* 説明 = the 指標辞典 card in a <dialog>. Delegated: rows of 詳しい数字 and popovers arrive later. */
document.addEventListener("click", (e) => {
  const btn = e.target.closest(".help-btn[data-help]");
  if (!btn) return;
  e.preventDefault();
  e.stopPropagation();
  const dialog = document.getElementById("help-" + btn.getAttribute("data-help"));
  if (!dialog) return;
  const pop = document.getElementById("pop");
  if (pop && !pop.hidden) pop.querySelector("[data-pop-close]")?.click();
  dialog.showModal();
});
document.addEventListener("click", (e) => {
  if (e.target.matches && e.target.matches("dialog[data-help-dialog]")) e.target.close();
});

/* 詳しい数字: groups that start closed (オーディエンス・イベント) */
document.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-dgroup-toggle]");
  if (!btn) return;
  const table = document.getElementById(btn.getAttribute("aria-controls"));
  const open = btn.getAttribute("aria-expanded") !== "true";
  btn.setAttribute("aria-expanded", open ? "true" : "false");
  btn.textContent = open ? btn.dataset.close : btn.dataset.open;
  if (table) table.hidden = !open;
  const sum = btn.closest(".dgroup")?.querySelector("[data-dgroup-summary]");
  if (sum) sum.hidden = open;
});

/* 詳しい数字 loaded after the page (live GA4: the extra reports are the slow part) */
(function () {
  const box = document.querySelector("[data-details][data-src]");
  if (!box) return;
  async function load() {
    box.setAttribute("aria-busy", "true");
    try {
      const res = await fetch(box.dataset.src, { headers: { Accept: "text/html" } });
      if (!res.ok) throw new Error(String(res.status));
      box.innerHTML = await res.text(); // our own server-rendered, autoescaped fragment
      const warn = Number(box.querySelector("[data-warn]")?.dataset.warn || 0);
      const badge = document.querySelector("[data-nav-warn]");
      if (badge && warn) { badge.textContent = badge.textContent.replace(/\d+/, String(warn)); badge.hidden = false; }
      if (location.hash.startsWith("#g-")) document.querySelector(location.hash)?.scrollIntoView();
    } catch (err) {
      const p = document.createElement("p");
      p.className = "details-loading";
      p.textContent = BOARD.load_error + " ";
      const retry = document.createElement("button");
      retry.type = "button";
      retry.className = "dgroup-toggle";
      retry.textContent = BOARD.retry;
      retry.addEventListener("click", load);
      p.appendChild(retry);
      box.replaceChildren(p);
    } finally {
      box.removeAttribute("aria-busy");
    }
  }
  load();
})();

/* The page menu in the top bar follows the scroll */
(function () {
  const links = Array.from(document.querySelectorAll(".page-nav [data-nav]"));
  if (!links.length || !("IntersectionObserver" in window)) return;
  const seen = new Map();
  const io = new IntersectionObserver((entries) => {
    entries.forEach((en) => seen.set(en.target.id, en.isIntersecting ? en.intersectionRatio : 0));
    let best = null;
    links.forEach((a) => { const r = seen.get(a.dataset.nav) || 0; if (r > 0 && (!best || r > (seen.get(best.dataset.nav) || 0))) best = a; });
    if (!best) return;
    links.forEach((a) => { const on = a === best; a.classList.toggle("is-on", on); if (on) a.setAttribute("aria-current", "true"); else a.removeAttribute("aria-current"); });
  }, { rootMargin: "-120px 0px -40% 0px", threshold: [0, 0.1, 0.3, 0.6] });
  links.forEach((a) => { const el = document.getElementById(a.dataset.nav); if (el) io.observe(el); });
})();

/* Right-top drawers (比べる業種 · 段の編集): one open at a time */
window.SiteDrawer = (function () {
  let opener = null;
  function all() { return Array.from(document.querySelectorAll("[data-drawer]")); }
  function close() {
    all().forEach((d) => { d.hidden = true; });
    document.querySelectorAll("[data-drawer-open]").forEach((b) => b.setAttribute("aria-expanded", "false"));
    document.dispatchEvent(new CustomEvent("drawer:close"));
    if (opener && document.contains(opener)) opener.focus({ preventScroll: true });
    opener = null;
  }
  function open(name, from) {
    const target = document.querySelector('[data-drawer="' + name + '"]');
    if (!target) return;
    all().forEach((d) => { d.hidden = d !== target; });
    const pop = document.getElementById("pop");
    if (pop && !pop.hidden) pop.querySelector("[data-pop-close]")?.click();
    document.querySelectorAll("[data-drawer-open]").forEach((b) => b.setAttribute("aria-expanded", b.dataset.drawerOpen === name ? "true" : "false"));
    opener = from || null;
    target.querySelector("input:not([type=hidden]):checked, input:not([type=hidden]), button")?.focus({ preventScroll: true });
  }
  document.addEventListener("click", (e) => {
    const o = e.target.closest("[data-drawer-open]");
    if (o) { e.preventDefault(); open(o.dataset.drawerOpen, o); return; }
    if (e.target.closest("[data-drawer-close]")) close();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && all().some((d) => !d.hidden) && !document.querySelector("dialog[open]")) close();
  });
  return { open, close };
})();
if (BOARD.auto_open === "industry") window.SiteDrawer.open("industry");
/* 「目安を細かく調整」 (bottom of the 業種 drawer): close the drawer, then open 目安 under the 業種 chip */
document.addEventListener("click", (e) => {
  if (!e.target.closest("[data-ind-adjust]")) return;
  window.SiteDrawer.close();
  const chip = document.querySelector(".top-right .ind-chip");
  /* after this click has passed the popover's outside-click handler */
  if (chip && window.SiteKPIPop) setTimeout(() => window.SiteKPIPop.open("bench-all", chip), 0);
});

/* 行動フロー: 全体 / channel switch — swaps the numbers shown on each step */
(function () {
  const flow = document.getElementById("flow");
  if (!flow) return;
  flow.querySelectorAll("[data-flow-ch]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const ch = btn.dataset.flowCh;
      flow.dataset.ch = ch;
      flow.querySelectorAll("[data-flow-ch]").forEach((b) => {
        const on = b === btn;
        b.classList.toggle("is-on", on);
        b.setAttribute("aria-pressed", on ? "true" : "false");
      });
      flow.querySelectorAll("[data-v-all]").forEach((el) => {
        const v = el.getAttribute("data-v-" + ch);
        el.textContent = v != null ? v : el.getAttribute("data-v-all");
      });
      flow.querySelectorAll(".flow-mix i").forEach((i) => i.classList.toggle("is-on", ch !== "all" && i.dataset.ch === ch));
      flow.querySelectorAll("[data-ch-row]").forEach((r) => r.classList.toggle("is-on", r.dataset.chRow === ch));
    });
  });
})();

/* sticky offsets below the top bar (its height depends on the language and the width) */
(function () {
  const top = document.querySelector(".top");
  if (!top) return;
  const set = () => document.documentElement.style.setProperty("--top-h", top.offsetHeight + "px");
  set();
  window.addEventListener("resize", set);
})();

/* 期間: choosing a period reloads the board for it */
document.querySelectorAll("[data-period] select").forEach((sel) => sel.addEventListener("change", () => {
  const url = new URL(location.href);
  url.searchParams.set("period", sel.value);
  ["edit", "industry"].forEach((k) => url.searchParams.delete(k));
  url.hash = "";
  location.assign(url.toString());
}));
