/* 見本ボード: picking a goal or an industry swaps only the preview (server-rendered fragment).
   Links work without JS — this just avoids a full page load and keeps the list's scroll. */
(function () {
  const pane = document.querySelector("[data-preview]");
  if (!pane || !window.fetch) return;
  let seq = 0;

  async function load(href, push) {
    const url = new URL(href, location.href);
    const mine = ++seq;
    pane.classList.add("is-loading");
    try {
      const res = await fetch("/samples/preview" + url.search, { headers: { Accept: "text/html" } });
      if (!res.ok) throw new Error(res.status);
      const html = await res.text();
      if (mine !== seq) return;
      pane.innerHTML = html; // trusted: our own server-rendered, autoescaped fragment
      const b = url.searchParams.get("b");
      document.querySelectorAll("[data-goal]").forEach((a) => {
        const on = new URL(a.href).searchParams.get("b") === b;
        a.classList.toggle("is-on", on);
        if (on) a.setAttribute("aria-current", "true"); else a.removeAttribute("aria-current");
      });
      if (push) history.pushState(null, "", url.pathname + url.search);
    } catch (e) {
      location.href = href;
    } finally {
      if (mine === seq) pane.classList.remove("is-loading");
    }
  }

  document.addEventListener("click", (e) => {
    const a = e.target.closest("[data-goal], [data-ind]");
    if (!a || e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
    e.preventDefault();
    load(a.href, true);
  });
  window.addEventListener("popstate", () => load(location.href, false));
})();
