/* Minimal stand-in for the Design canvas runtime: renders <x-dc> templates
   ({{expr}}, <sc-for list as>, <sc-if value>, onX handlers) with the file's Component. */
(function () {
  const BOOL = new Set(["checked", "disabled", "hidden", "selected", "open", "required"]);
  window.DCLogic = class {
    constructor(props) { this.props = props || {}; this.state = {}; }
    setState(p) { this.state = Object.assign({}, this.state, typeof p === "function" ? p(this.state) : p); window.__dcRender && window.__dcRender(); }
  };
  const cache = new Map();
  function ev(expr, scope) {
    let f = cache.get(expr);
    if (!f) { try { f = new Function("__s", "with(__s){return (" + expr + ")}"); } catch (e) { f = () => undefined; } cache.set(expr, f); }
    try { return f(scope); } catch (e) { return undefined; }
  }
  const ONE = /^\s*\{\{([\s\S]*?)\}\}\s*$/;
  function raw(str, scope) { const m = str.match(ONE); return m ? ev(m[1], scope) : interp(str, scope); }
  function interp(str, scope) {
    return str.replace(/\{\{([\s\S]*?)\}\}/g, (_, e) => { const v = ev(e, scope); return v == null ? "" : String(v); });
  }
  function kids(node, scope, out) { node.childNodes.forEach((c) => one(c, scope, out)); }
  function one(node, scope, out) {
    if (node.nodeType === 3) { out.appendChild(document.createTextNode(interp(node.nodeValue, scope))); return; }
    if (node.nodeType !== 1) return;
    const tag = node.localName;
    if (tag === "sc-for") {
      const list = raw(node.getAttribute("list") || "", scope) || [];
      const as = node.getAttribute("as") || "item";
      Array.from(list).forEach((it, i) => { const s = Object.create(scope); s[as] = it; s.index = i; kids(node, s, out); });
      return;
    }
    if (tag === "sc-if") { if (raw(node.getAttribute("value") || "", scope)) kids(node, scope, out); return; }
    const el = document.createElementNS(node.namespaceURI, node.tagName.toLowerCase() === node.tagName ? node.tagName : node.localName);
    for (const a of Array.from(node.attributes)) {
      const n = a.name;
      if (n.startsWith("hint-")) continue;
      if (/^on[a-z]+$/.test(n) && a.value.includes("{{")) {
        const fn = raw(a.value, scope);
        if (typeof fn === "function") el.addEventListener(n.slice(2), (e) => fn(e));
        continue;
      }
      if (!a.value.includes("{{")) { el.setAttribute(n, a.value); continue; }
      const v = raw(a.value, scope);
      if (BOOL.has(n) && (v === false || v == null || v === "false")) continue;
      if (n === "value" && "value" in el) el.value = v == null ? "" : v;
      el.setAttribute(n, v == null ? "" : String(v));
    }
    kids(node, scope, el);
    out.appendChild(el);
  }
  document.addEventListener("DOMContentLoaded", () => {
    const host = document.querySelector("x-dc");
    const scr = document.querySelector("script[data-dc-script]");
    if (!host || !scr) return;
    const helmet = host.querySelector("helmet");
    if (helmet) { Array.from(helmet.childNodes).forEach((n) => document.head.appendChild(n)); helmet.remove(); }
    const frag = document.createDocumentFragment();
    Array.from(host.childNodes).forEach((n) => frag.appendChild(n));
    const defaults = {};
    try { const p = JSON.parse(scr.dataset.props || "{}"); for (const k in p) if (k[0] !== "$" && p[k] && "default" in p[k]) defaults[k] = p[k].default; } catch (e) {}
    const Comp = new Function("DCLogic", scr.textContent + "\n;return Component;")(window.DCLogic);
    const inst = new Comp(Object.assign(defaults, window.__dcProps || {}));
    const root = document.createElement("div");
    root.style.display = "contents";
    host.replaceWith(root);
    window.__dcInst = inst;
    window.__dcRender = () => { const out = document.createDocumentFragment(); kids(frag, inst.renderVals(), out); root.replaceChildren(out); };
    window.__dcRender();
    document.documentElement.setAttribute("data-dc-ready", "1");
  });
})();
