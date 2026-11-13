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

/* 詳しい数字: each category opens / closes from its name (the chevron turns); the first three start open */
document.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-dgroup-toggle]");
  if (!btn || !btn.hasAttribute("aria-controls")) return;
  const table = document.getElementById(btn.getAttribute("aria-controls"));
  const open = btn.getAttribute("aria-expanded") !== "true";
  btn.setAttribute("aria-expanded", open ? "true" : "false");
  btn.closest(".dgroup")?.classList.toggle("is-open", open);
  if (table) table.hidden = !open;
});

/* 共有: native share sheet where available, else copy the current URL — never any GA4 data */
document.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-board-share]");
  if (!btn) return;
  const url = location.href;
  if (navigator.share) { navigator.share({ url: url, title: document.title }).catch(() => {}); return; }
  const msg = btn.parentElement.querySelector("[data-board-share-msg]");
  const done = (ok) => { if (msg) msg.textContent = ok ? msg.dataset.ok : msg.dataset.fail; };
  const fallback = () => {
    const ta = document.createElement("textarea");
    ta.value = url;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    let ok = false;
    try { ok = document.execCommand("copy"); } catch (err) { ok = false; }
    ta.remove();
    done(ok);
  };
  if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(url).then(() => done(true), fallback);
  else fallback();
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
      if (location.hash.startsWith("#g-")) document.querySelector(location.hash)?.scrollIntoView();
    } catch (err) {
      const p = document.createElement("p");
      p.className = "details-loading";
      p.textContent = BOARD.load_error + " ";
      const retry = document.createElement("button");
      retry.type = "button";
      retry.className = "link-btn";
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
  const chip = document.querySelector(".top-right [data-drawer-open=industry]");
  /* after this click has passed the popover's outside-click handler */
  if (chip && window.SiteKPIPop) setTimeout(() => window.SiteKPIPop.open("bench-all", chip), 0);
});

/* 行動フロー: 全体 / channel switch — swaps the numbers shown on each step */
(function () {
  const flow = document.getElementById("flow");
  if (!flow) return;
  const nowEl = flow.querySelector("[data-ch-now]");

  function setNow(btn) {
    if (!nowEl) return;
    const ch = btn.dataset.flowCh;
    const name = btn.dataset.chLabel || btn.textContent.trim();
    const filtered = ch !== "all";
    flow.classList.toggle("is-ch-filtered", filtered);
    nowEl.classList.toggle("is-filtered", filtered);
    nowEl.textContent = filtered
      ? (nowEl.dataset.tplNamed || "").replace("{name}", name)
      : (nowEl.dataset.tplAll || "");
    document.querySelectorAll("[data-ch-toggle]").forEach((t) => t.classList.toggle("is-filtered", filtered));
  }

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
      setNow(btn);
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

/* 流入別に見る: the channel chips and the 流入別 table stay closed until asked for */
document.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-ch-toggle]");
  if (!btn) return;
  const open = btn.getAttribute("aria-expanded") !== "true";
  btn.setAttribute("aria-expanded", open ? "true" : "false");
  document.querySelectorAll("[data-ch-part]").forEach((el) => { el.hidden = !open; });
  const grid = document.querySelector("[data-where-grid]");
  if (grid) grid.classList.toggle("is-single", !open || !grid.querySelector(".flow-chtable"));
  if (!open) document.querySelector('[data-flow-ch="all"]')?.click(); // back to 全体
  if (open && window.SiteKPITrack) window.SiteKPITrack("channel_filter");
});
