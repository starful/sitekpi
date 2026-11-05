/* The board's story (① → ④): the 「自分の AI に聞く」 prompt (built here from #ai-data, copied by the viewer —
   SiteKPI never sends it anywhere), ④'s 「流入別に見る」 shortcut, and equal label heights in the flow. */
(function () {
  "use strict";
  const box = document.querySelector("[data-ai]");
  if (box) {
    const P = JSON.parse(document.getElementById("ai-data").textContent);
    const panel = box.querySelector("#ai-box");
    const text = box.querySelector("[data-ai-text]");
    const msg = box.querySelector("[data-ai-msg]");
    const anon = box.querySelector("[data-ai-anon]");
    const detail = box.querySelector("[data-ai-detail]");
    let ask = "cause";
    function build() {
      const site = P.has_site && anon && !anon.checked ? P.site_named : P.site_anon;
      const parts = [P.role + "\n" + site, P.body];
      if (!detail || detail.checked) parts.push(P.details);
      parts.push(P.ask_k + "\n" + P.asks[ask] + "\n" + P.tail);
      text.value = parts.join("\n\n");
      msg.textContent = "";
    }
    box.addEventListener("click", (e) => {
      const tg = e.target.closest("[data-ai-toggle]");
      if (tg) {
        const open = panel.hidden;
        panel.hidden = !open;
        tg.setAttribute("aria-expanded", open ? "true" : "false");
        if (open) build();
        return;
      }
      const a = e.target.closest("[data-ai-ask]");
      if (a) {
        ask = a.dataset.aiAsk;
        box.querySelectorAll("[data-ai-ask]").forEach((b) => b.setAttribute("aria-pressed", b === a ? "true" : "false"));
        build();
        return;
      }
      if (e.target.closest("[data-ai-copy]")) {
        const done = (ok) => {
          msg.textContent = ok ? msg.dataset.ok : msg.dataset.fail;
          if (ok && window.SiteKPITrack) window.SiteKPITrack("ai_prompt_copy", { purpose: ask, details: !detail || detail.checked ? "true" : "false" });
        };
        const fallback = () => { text.focus(); text.select(); let ok = false; try { ok = document.execCommand("copy"); } catch (err) { ok = false; } done(ok); };
        if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text.value).then(() => done(true), fallback);
        else fallback();
      }
    });
    box.addEventListener("change", (e) => { if (e.target.matches("[data-ai-anon], [data-ai-detail]")) build(); });
  }

  // ④ 「流入別に見る」: open the channel view in ② and go there
  document.addEventListener("click", (e) => {
    if (!e.target.closest("[data-ch-toggle-go]")) return;
    const tg = document.querySelector("[data-ch-toggle]");
    if (tg && tg.getAttribute("aria-expanded") !== "true") tg.click();
    document.getElementById("flow")?.scrollIntoView({ behavior: "smooth", block: "start" });
  });

  // ② every step's label gets the same height, so counts and bars line up in one row
  const labels = () => Array.from(document.querySelectorAll("#flow .flow-track .flow-node .flow-label"));
  function equal() {
    const ls = labels();
    ls.forEach((l) => { l.style.minHeight = ""; });
    const track = document.querySelector("#flow .flow-track");
    if (!track || ls.length < 2) return;
    const tops = new Set(ls.map((l) => Math.round(l.getBoundingClientRect().left)));
    if (tops.size < ls.length) return; // stacked (phone): nothing to line up
    const h = Math.max(...ls.map((l) => l.getBoundingClientRect().height));
    ls.forEach((l) => { l.style.minHeight = h + "px"; });
  }
  equal();
  let timer = 0;
  window.addEventListener("resize", () => { clearTimeout(timer); timer = setTimeout(equal, 120); });
  document.addEventListener("board:flow-updated", equal);
})();
