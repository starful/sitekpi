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

/* 印刷 / PDF: one category per page, never cut in the middle (board.css 「print」).
   Units = each story card, and each 詳しい数字 category. Every unit starts a new A4 page; a unit taller than
   a page is scaled down (zoom) until it fits instead of being split. Heights are measured in a hidden
   iframe exactly as wide as the printable area, so the narrow print layout (≤900px rules) is what we measure.
   Closed folds and collapsed categories open for paper and close again afterwards. */
(function () {
  const PRINT_W = 718;   // A4 210mm − 2 × 10mm margin, in CSS px (96 per inch)
  const PRINT_H = 1020;  // A4 297mm − 2 × 10mm = 1047px, minus a little air for the browser
  const MIN_ZOOM = 0.45; // smaller than this would be unreadable; never expected on a board
  const restore = [];
  let prepared = false;

  function units(doc) {
    const content = doc.querySelector(".content");
    if (!content) return [];
    const out = [];
    content.querySelectorAll(":scope > section.card").forEach((card) => {
      if (card.classList.contains("detail")) {
        out.push({ el: card, kind: "detail" });
        card.querySelectorAll(".dgroup").forEach((g, i) => out.push({ el: g, kind: i ? "group" : "group-first", card: card }));
      } else {
        out.push({ el: card, kind: "card" });
      }
    });
    return out;
  }

  function openAll() {
    document.querySelectorAll(".content details:not([open])").forEach((el) => {
      el.open = true; restore.push(() => { el.open = false; });
    });
    document.querySelectorAll("[data-dgroup-toggle][aria-expanded='false']").forEach((btn) => {
      const table = document.getElementById(btn.getAttribute("aria-controls"));
      const group = btn.closest(".dgroup");
      btn.setAttribute("aria-expanded", "true");
      if (table) table.hidden = false;
      if (group) group.classList.add("is-open");
      restore.push(() => {
        btn.setAttribute("aria-expanded", "false");
        if (table) table.hidden = true;
        if (group) group.classList.remove("is-open");
      });
    });
    const d = document.querySelector("[data-print-date]");
    if (d) d.textContent = new Date().toLocaleDateString(document.documentElement.lang || "ja");
  }

  function docTop(el, win) { return el.getBoundingClientRect().top + (win ? win.scrollY : 0); }

  function fit(el, avail) {
    let z = 1;
    let h = el.getBoundingClientRect().height;
    for (let k = 0; k < 4 && h > avail; k++) {
      z = Math.max(MIN_ZOOM, z * (avail / h) * 0.98);
      el.style.zoom = String(z);
      el.style.width = (el.parentElement.clientWidth / z) + "px";
      h = el.getBoundingClientRect().height;
      if (z === MIN_ZOOM) break;
    }
    return z < 1 ? { zoom: z, width: el.style.width } : null;
  }

  // Plan per unit (index-aligned with units(document)), measured in `doc` (iframe, or this page).
  // A card that fits keeps whole (a slight shrink to 85% is allowed). A longer card is split only between
  // its own blocks (e.g. the sub-questions of 「誰が？」) and packed onto as few pages as fit; a block taller
  // than a page is shrunk on its own page. A 詳しい数字 category always gets its own page.
  function measure(doc, win) {
    const list = units(doc);
    return list.map((u, i) => {
      if (u.kind === "detail") return null;  // flows; its categories are the units
      const el = u.el;
      const avail = u.kind === "group-first"
        ? PRINT_H - (docTop(el) - docTop(u.card))
        : i === 0 ? PRINT_H - docTop(el, win) : PRINT_H;
      const h = el.getBoundingClientRect().height;
      if (h <= avail) return null;
      if (u.kind !== "card" || h * 0.85 <= avail) return fit(el, avail) ? { zoom: el.style.zoom, width: el.style.width } : null;
      // split between blocks
      const kids = [...el.children].filter((c) => c.getBoundingClientRect().height > 0 || c.classList.contains("story-mark"));
      const top0 = docTop(el);
      const bottom = top0 + h;
      const segs = kids.map((c, k) => {
        const t = docTop(c);
        const next = k + 1 < kids.length ? docTop(kids[k + 1]) : bottom;
        return { el: c, idx: [...el.children].indexOf(c), h: Math.max(0, next - t), lead: k === 0 ? t - top0 : 0 };
      });
      const breaks = [];
      const zooms = {};
      let used = 0;
      let budgetNow = avail;
      let onPage = 0;
      segs.forEach((sg, k) => {
        const need = sg.h + sg.lead;
        // keep headings (qk · h2 · short notes) with the block after them
        const small = sg.h < 80 && k + 1 < segs.length;
        if (onPage && used + need > budgetNow && !(small && used + need + segs[k + 1].h <= budgetNow)) {
          breaks.push(sg.idx);
          used = 0; onPage = 0; budgetNow = PRINT_H;
        }
        if (need > budgetNow && !small) {
          const z = fit(sg.el, budgetNow - used);
          if (z) zooms[sg.idx] = z;
          used += sg.el.getBoundingClientRect().height;
        } else {
          used += need;
        }
        onPage++;
      });
      return { split: true, breaks: breaks, zooms: zooms };
    });
  }

  function apply(plan) {
    const list = units(document);
    const marked = [];
    const mark = (el, page, unit) => {
      if (page) el.classList.add("print-page");
      if (unit) el.classList.add("print-unit");
      marked.push(el);
    };
    list.forEach((u, i) => {
      const p = plan[i];
      // every unit starts a page except the very first card and the detail card's first category
      const page = i > 0 && u.kind !== "group-first";
      if (p && p.split) {
        mark(u.el, page, false);
        u.el.classList.add("print-split");
        [...u.el.children].forEach((c, k) => {
          mark(c, p.breaks.includes(k), true);
          const z = p.zooms[k];
          if (z) { c.style.zoom = String(z.zoom); c.style.width = z.width; }
        });
      } else {
        mark(u.el, page, u.kind !== "detail");
        if (p) { u.el.style.zoom = String(p.zoom); u.el.style.width = p.width; }
      }
    });
    restore.push(() => marked.forEach((el) => {
      el.classList.remove("print-page", "print-unit", "print-split");
      el.style.zoom = ""; el.style.width = "";
    }));
  }

  // Measured copy: the page's current DOM (no scripts) in an iframe as wide as the paper
  function measureInFrame() {
    return new Promise((resolve) => {
      const f = document.createElement("iframe");
      f.setAttribute("aria-hidden", "true");
      f.tabIndex = -1;
      f.style.cssText = `position:fixed;left:-10000px;top:0;width:${PRINT_W}px;height:${PRINT_H}px;border:0;visibility:hidden`;
      const html = document.documentElement.cloneNode(true);
      html.querySelectorAll("script, iframe").forEach((n) => n.remove());
      html.classList.add("is-printing");
      f.srcdoc = "<!DOCTYPE html>" + html.outerHTML;
      let done = false;
      const finish = (plan) => { if (done) return; done = true; f.remove(); resolve(plan); };
      f.addEventListener("load", () => {
        const doc = f.contentDocument;
        const ready = doc && doc.fonts ? doc.fonts.ready : Promise.resolve();
        ready.then(() => setTimeout(() => { try { finish(measure(doc, f.contentWindow)); } catch (e) { finish(null); } }, 60));
      });
      setTimeout(() => finish(null), 4000);  // never block printing
      document.body.appendChild(f);
    });
  }

  let busy = false;
  async function printBoard() {
    if (busy) return;
    busy = true;
    openAll();
    let plan = await measureInFrame();
    document.documentElement.classList.add("is-printing");
    if (!plan) plan = measure(document, window);  // fallback: measure here
    apply(plan);
    prepared = true;
    busy = false;
    window.print();
  }

  addEventListener("beforeprint", () => {
    if (prepared) return;
    // browser menu print: no time for the iframe — measure on this page (close enough)
    openAll();
    document.documentElement.classList.add("is-printing");
    apply(measure(document, window));
    prepared = true;
  });
  addEventListener("afterprint", () => {
    while (restore.length) restore.pop()();
    document.documentElement.classList.remove("is-printing");
    prepared = false;
  });
  document.addEventListener("click", (e) => {
    if (e.target.closest("[data-board-print]")) printBoard();
  });
  // ⌘P / Ctrl+P on a board → the same prepared print
  document.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && !e.altKey && (e.key === "p" || e.key === "P")) { e.preventDefault(); printBoard(); }
  });
})();

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

/* Coming back to the board (saving the flow, changing the industry or period, a 「直す」 link) keeps
   the reading position instead of jumping to the top. Hash links (#q3 …) still win. */
(function () {
  "use strict";
  const KEY = "sk_board_y";
  const here = location.pathname;
  try {
    const saved = JSON.parse(sessionStorage.getItem(KEY) || "null");
    sessionStorage.removeItem(KEY);
    if (saved && saved.p === here && Date.now() - saved.t < 120000 && !location.hash && saved.y > 0) {
      if ("scrollRestoration" in history) history.scrollRestoration = "manual";
      const go = () => window.scrollTo(0, Math.min(saved.y, document.documentElement.scrollHeight));
      go();
      window.addEventListener("load", go, { once: true });
    }
  } catch (e) { /* storage blocked: the board still works, it just opens at the top */ }
  window.addEventListener("pagehide", () => {
    try { sessionStorage.setItem(KEY, JSON.stringify({ p: here, y: window.scrollY, t: Date.now() })); } catch (e) { /* ignore */ }
  });
})();
