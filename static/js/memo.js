/* メモ・ご意見 (right panel): write any time, send to /feedback with the part of the page on screen.
   Sent notes are listed from this browser's storage only; the open / closed state is remembered. */
(function () {
  "use strict";
  const box = document.querySelector("[data-memo]");
  if (!box) return;
  const KEY_OPEN = "sk_memo_open", KEY_SENT = "sk_memo_sent";
  const text = box.querySelector("[data-memo-text]");
  const where = box.querySelector("[data-memo-where]");
  const msg = box.querySelector("[data-memo-msg]");
  const send = box.querySelector("[data-memo-send]");
  const list = box.querySelector("[data-memo-list]");
  const sentBox = box.querySelector("[data-memo-sent]");
  let mood = "";

  function get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } }

  // open / closed: remembered; on narrow screens it starts closed
  function setOpen(open, save) {
    box.classList.toggle("is-closed", !open);
    box.querySelectorAll("[data-memo-toggle]").forEach((b) => b.setAttribute("aria-expanded", open ? "true" : "false"));
    document.querySelector(".shell")?.classList.toggle("memo-open", open);
    if (save) set(KEY_OPEN, open ? "1" : "0");
  }
  const saved = get(KEY_OPEN);
  setOpen(saved ? saved === "1" : window.innerWidth >= 1600, false); // wide screens start open
  box.addEventListener("click", (e) => {
    const tg = e.target.closest("[data-memo-toggle]");
    if (tg) { const open = box.classList.contains("is-closed"); setOpen(open, true); if (open) text.focus({ preventScroll: true }); }
    const m = e.target.closest("[data-mood]");
    if (m) {
      mood = mood === m.dataset.mood ? "" : m.dataset.mood;
      box.querySelectorAll("[data-mood]").forEach((b) => b.setAttribute("aria-pressed", b.dataset.mood === mood ? "true" : "false"));
    }
  });

  // いま見ている所: the [data-memo-where] section nearest the top of the screen
  const parts = Array.from(document.querySelectorAll("[data-memo-where]")).filter((el) => !box.contains(el));
  function current() {
    let best = null;
    const line = Math.min(window.innerHeight * 0.35, 320);
    parts.forEach((el) => { const r = el.getBoundingClientRect(); if (r.top <= line && r.bottom > 80) best = el; });
    if (!best && parts.length) best = parts.find((el) => el.getBoundingClientRect().bottom > 80) || null;
    return best ? best.dataset.memoWhere : where.dataset.page;
  }
  if (parts.length) {
    let raf = 0;
    const update = () => { raf = 0; where.textContent = current(); };
    window.addEventListener("scroll", () => { if (!raf) raf = requestAnimationFrame(update); }, { passive: true });
    update();
  }

  function stamp() { const d = new Date(); return String(d.getHours()).padStart(2, "0") + ":" + String(d.getMinutes()).padStart(2, "0"); }
  function readSent() { try { return JSON.parse(get(KEY_SENT) || "[]") || []; } catch (e) { return []; } }
  function draw() {
    const rows = readSent();
    sentBox.hidden = !rows.length;
    list.replaceChildren(...rows.map((r) => {
      const p = document.createElement("p");
      p.className = "memo-item";
      const k = document.createElement("span");
      k.className = "memo-item-k";
      k.textContent = (r.where || "") + " · " + (r.at || "");
      p.append(k, document.createElement("br"), document.createTextNode((r.mood === "up" ? "👍 " : r.mood === "down" ? "👎 " : "") + (r.text || "")));
      return p;
    }));
  }
  draw();

  send.addEventListener("click", async () => {
    const comment = text.value.trim();
    if (!comment && !mood) { text.focus(); return; }
    const section = where.textContent.trim();
    send.disabled = true; msg.textContent = "";
    try {
      const r = await fetch("/feedback", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({
        vote: mood, comment: comment, screen: box.dataset.screen || "", section: section, path: location.pathname,
        website: box.querySelector("[data-memo-hp]").value || "" }) });
      if (!r.ok) throw new Error(String(r.status));
      if (window.SiteKPITrack) window.SiteKPITrack("feedback_submit", { vote: mood || "none", has_comment: comment ? "true" : "false", location: "memo" });
      const rows = [{ where: section, at: stamp(), text: comment, mood: mood }].concat(readSent()).slice(0, 10);
      set(KEY_SENT, JSON.stringify(rows));
      draw();
      text.value = ""; mood = "";
      box.querySelectorAll("[data-mood]").forEach((b) => b.setAttribute("aria-pressed", "false"));
      msg.textContent = msg.dataset.ok;
    } catch (e) {
      msg.textContent = msg.dataset.err;
    } finally {
      send.disabled = false;
    }
  });
})();
