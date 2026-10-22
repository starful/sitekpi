"""Shared app chrome: left rail navigation (+ mobile drawer) for every page.

One rail markup / CSS / JS used by the board, builder, connect and settings
pages so they cannot drift apart.
"""

from __future__ import annotations

from html import escape
from typing import Any

from sitekpi.i18n import t
from sitekpi.i18n.pack_l10n import pack_text
from sitekpi.views.branding import brand_logo_html

_RAIL_CSS = """
    .shell {
      display: grid;
      grid-template-columns: var(--rail-w) 1fr;
      min-height: 100vh;
    }
    .rail {
      background: #fff; color: var(--ink);
      border-right: 1px solid var(--line);
      padding: 18px 12px 20px; position: sticky; top: 0; height: 100vh;
      display: flex; flex-direction: column; min-height: 0;
      box-sizing: border-box;
      font-family: var(--font-ui);
    }
    .rail .logo {
      margin: 0 8px 18px; flex-shrink: 0;
    }
    .rail nav {
      flex: 1 1 auto; min-height: 0; overflow-y: auto; overflow-x: hidden;
      padding-right: 2px; overscroll-behavior: contain;
      scrollbar-width: thin; scrollbar-color: #cbd5e1 transparent;
    }
    .rail nav::-webkit-scrollbar { width: 5px; }
    .rail nav::-webkit-scrollbar-thumb {
      background: #cbd5e1; border-radius: 999px;
    }
    .rail nav a {
      display: block; padding: 7px 10px; border-radius: 6px;
      color: #3d4a5c; text-decoration: none; font-size: 0.9rem; font-weight: 600;
      margin-bottom: 1px;
    }
    .rail nav a:hover { background: #f3f6fa; color: var(--ink); }
    .rail nav a.is-on { background: #eef4ff; color: var(--accent); }
    .rail .nav-group {
      margin: 16px 0 6px; padding: 0 10px;
      font-size: 0.66rem; font-weight: 700; letter-spacing: 0.04em;
      color: #8b97a8; text-transform: none;
    }
    .rail .nav-group:first-child { margin-top: 0; }
    .rail .pack-search-wrap { padding: 0 10px 8px; }
    .rail .pack-search {
      width: 100%; box-sizing: border-box;
      border: 1px solid var(--line); border-radius: 8px;
      padding: 7px 10px; font: inherit; font-size: 0.78rem;
      background: #fff; color: var(--ink);
    }
    .rail .pack-search:focus {
      outline: none; border-color: #bfd2f8; box-shadow: 0 0 0 2px #eaf1ff;
    }
    .rail .pack-search-empty {
      margin: 6px 0 0; font-size: 0.72rem; color: #94a3b8; font-weight: 600;
    }
    .visually-hidden {
      position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
      overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0;
    }
    .rail .nav-sub {
      margin: 0 0 4px; padding: 0; background: transparent;
    }
    .rail .nav-sub a {
      font-size: 0.9rem; font-weight: 600; padding: 9px 10px;
    }
    .rail .nav-sub a .pack-name {
      display: block; line-height: 1.35; color: inherit; font-weight: 600;
    }
    .rail .nav-sub a .pack-hint {
      display: none; margin-top: 3px;
      font-size: 0.66rem; font-weight: 500; color: #8b97a8; line-height: 1.3;
    }
    .rail .nav-sub a.is-on .pack-hint { display: block; color: #6b8fd4; }
    /* Findy-like: category = Noto + chevron; packs = Plex */
    .rail .pack-cat { margin: 0 0 8px; border: none; background: transparent; }
    .rail .pack-cat summary {
      list-style: none; cursor: pointer; user-select: none;
      display: flex; align-items: center; gap: 4px;
      padding: 8px 10px; border-radius: 4px;
      font-family: "Noto Sans JP", sans-serif;
      font-size: 0.9rem; font-weight: 700; letter-spacing: 0.02em;
      color: #8b97a8; background: transparent;
    }
    .rail .pack-cat[open] summary { color: #6b7788; }
    .rail .pack-cat summary:hover { color: #5a6575; background: transparent; }
    .rail .pack-cat summary::-webkit-details-marker { display: none; }
    .rail .pack-cat summary::before {
      content: "▸"; flex: 0 0 auto; width: 0.75em;
      color: #a8b2c1; font-size: 0.8rem; line-height: 1;
    }
    .rail .pack-cat[open] summary::before { content: "▾"; }
    .rail .pack-cat-label { flex: 1 1 auto; min-width: 0; }
    .rail .pack-cat-body {
      padding: 2px 0 8px; margin: 0; border: none;
    }
    .rail .pack-cat-body a {
      margin: 0 0 2px; padding: 9px 10px 9px 26px;
      border-radius: 6px; background: transparent;
    }
    .rail .pack-cat-body a:hover { background: transparent; color: inherit; }
    .rail .pack-cat-body a.is-on { background: #eef4ff; color: var(--accent); }
    .rail .pack-cat-body a.is-on:hover { background: #eef4ff; color: var(--accent); }
    .rail .pack-cat-body a .pack-name {
      font-family: var(--font-ui);
      font-size: 0.9rem; font-weight: 600;
    }
    .rail .nav-muted { color: #8b97a8 !important; font-weight: 500 !important; }
    .rail .nav-add {
      color: var(--accent) !important; font-size: 0.75rem !important; font-weight: 600 !important;
    }
    .rail .nav-close { display: none; }
    .mobile-bar { display: none; }
    @media (max-width: 900px) {
      .shell { grid-template-columns: 1fr; }
      .rail {
        position: fixed; top: 0; left: 0; bottom: 0; height: auto;
        width: min(86vw, 300px); z-index: 60;
        transform: translateX(-102%); transition: transform 0.2s ease;
        visibility: hidden;
      }
      body.rail-open { overflow: hidden; }
      body.rail-open .rail {
        transform: none; visibility: visible;
        box-shadow: 0 0 0 100vmax rgba(15, 23, 42, 0.38);
      }
      .rail .nav-close {
        display: block; position: absolute; top: 14px; right: 12px;
        border: 1px solid var(--line); background: #fff; border-radius: 8px;
        font: inherit; font-size: 0.8rem; font-weight: 700; color: var(--muted, #6b7788);
        padding: 4px 10px; cursor: pointer;
      }
      .mobile-bar {
        display: flex; align-items: center; gap: 12px;
        position: sticky; top: 0; z-index: 40;
        background: #fff; border-bottom: 1px solid var(--line);
        padding: 10px 16px;
      }
      .mobile-bar .logo { font-size: 1.05rem; }
      .mobile-bar .logo .logo-mark { width: 24px; height: 24px; }
      .menu-btn {
        display: inline-flex; align-items: center; gap: 6px;
        border: 1px solid var(--line); background: #fff; border-radius: 8px;
        font: inherit; font-size: 0.85rem; font-weight: 700; color: var(--ink);
        padding: 6px 10px; cursor: pointer;
      }
      .menu-btn svg { width: 16px; height: 16px; }
    }
"""

_RAIL_JS = """
<script>
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
</script>
"""

_MENU_ICON = (
    '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 4h12M2 8h12M2 12h12" '
    'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" fill="none"/></svg>'
)


def rail_css() -> str:
    return _RAIL_CSS


def rail_js() -> str:
    return _RAIL_JS


def mobile_bar_html(locale: str) -> str:
    """Top bar with the menu button — only visible under 900px."""
    return (
        '<div class="mobile-bar">'
        f'<button type="button" class="menu-btn" data-rail-toggle aria-controls="rail" aria-expanded="false">'
        f'{_MENU_ICON}{escape(t("nav.menu", locale))}</button>'
        f"{brand_logo_html()}"
        "</div>"
    )


def rail_html(rail_nav: str, locale: str) -> str:
    """The <aside> rail itself (logo + nav), with a close button for the mobile drawer."""
    return (
        f'<aside class="rail" id="rail" aria-label="{escape(t("nav.menu", locale))}">'
        f'<button type="button" class="nav-close" data-rail-close>{escape(t("close", locale))}</button>'
        f"{brand_logo_html()}<nav>{rail_nav}</nav></aside>"
    )


def app_nav_html(
    *,
    nav_active: str,
    locale: str,
    connected: dict[str, str] | None = None,
    industry: str = "",
    pack_groups: Any = None,
) -> str:
    """Rail markup for pages that are not a pack board (builder, connect, settings)."""
    return rail_html(
        _rail_nav_html(
            industry=industry,
            nav_active=nav_active,
            connected=connected,
            pack_groups=pack_groups,
            locale=locale,
        ),
        locale,
    )


def _rail_nav_html(
    *,
    industry: str,
    pack_links: list[tuple[str, str]] | list[tuple[str, str, str]] | None = None,
    nav_active: str,
    connected: dict[str, str] | None = None,
    pack_groups: list[tuple[str, str, list[tuple[str, str, str]]]] | None = None,
    locale: str = "ja",
) -> str:
    """サンプルパック（カテゴリ内訳）/ 接続済み / アプリ — separate categories."""

    def _pack_link(slug: str, label: str, hint: str) -> str:
        on = "is-on" if nav_active == f"pack:{slug}" else ""
        shown_label = pack_text(slug, "label", locale, label)
        shown_hint = pack_text(slug, "hint", locale, hint) if hint else ""
        hint_html = (
            f'<span class="pack-hint">{escape(shown_hint)}</span>' if shown_hint else ""
        )
        q = f"{shown_label} {shown_hint} {slug}".strip().lower()
        return (
            f'<a href="/{escape(slug)}" class="{on}" data-pack-q="{escape(q)}">'
            f'<span class="pack-name">{escape(shown_label)}</span>{hint_html}</a>'
        )

    if pack_groups is None:
        from sitekpi.packs import packs_by_category

        pack_groups = packs_by_category()
    elif not pack_groups and pack_links:
        items: list[tuple[str, str, str]] = []
        for item in pack_links:
            if len(item) >= 3:
                items.append((item[0], item[1], item[2]))
            else:
                items.append((item[0], item[1], ""))
        pack_groups = [("all", t("cat.all", locale), items)]

    active_slug = ""
    if nav_active.startswith("pack:"):
        active_slug = nav_active.removeprefix("pack:")

    pack_nav_parts: list[str] = []
    for cid, cat_label, items in pack_groups:
        links = "".join(_pack_link(s, lab, h) for s, lab, h in items)
        is_open = active_slug and any(s == active_slug for s, _, _ in items)
        open_attr = " open" if is_open else ""
        shown = t(f"cat.{cid}", locale) if cid != "all" else cat_label
        if shown.startswith("cat."):
            shown = cat_label
        pack_nav_parts.append(
            f'<details class="pack-cat"{open_attr}>'
            f'<summary><span class="pack-cat-label">{escape(shown)}</span></summary>'
            f'<div class="pack-cat-body">{links}</div></details>'
        )
    pack_nav = "".join(pack_nav_parts)

    if connected:
        live_cls = "is-on" if nav_active == "live" else ""
        connected_nav = (
            f'<a href="/live" class="{live_cls}" title="{escape(connected.get("email") or "")}">'
            f'{escape(connected.get("name") or t("nav.property", locale))}</a>'
            f'<a href="/connect" class="nav-add">{escape(t("nav.change_property", locale))}</a>'
        )
    else:
        connected_nav = (
            f'<a href="/connect" class="nav-muted">{escape(t("nav.disconnected", locale))}</a>'
            f'<a href="/connect" class="nav-add">{escape(t("nav.add_ga4", locale))}</a>'
        )

    search = f"""
        <div class="pack-search-wrap">
          <label class="visually-hidden" for="pack-search">{escape(t("nav.pack_search", locale))}</label>
          <input type="search" id="pack-search" class="pack-search"
            placeholder="{escape(t("nav.pack_search_ph", locale))}"
            autocomplete="off" data-pack-search />
          <p class="pack-search-empty" data-pack-search-empty hidden>
            {escape(t("nav.pack_search_empty", locale))}
          </p>
        </div>
    """
    return f"""
        <div class="nav-group">{escape(t("nav.samples", locale))}</div>
        {search}
        <div class="nav-sub" role="navigation" aria-label="{escape(t("nav.packs_aria", locale))}" data-pack-nav>{pack_nav}</div>
        <div class="nav-group">{escape(t("nav.connected", locale))}</div>
        <div class="nav-sub" role="navigation" aria-label="{escape(t("nav.ga4_aria", locale))}">{connected_nav}</div>
        <div class="nav-group">{escape(t("nav.app", locale))}</div>
        <a href="/builder" class="{"is-on" if nav_active == "builder" else ""}">{escape(t("nav.builder", locale))}</a>
        <a href="/connect" class="{"is-on" if nav_active == "connect" else ""}">{escape(t("nav.connect", locale))}</a>
        <a href="/settings" class="{"is-on" if nav_active == "settings" else ""}">{escape(t("nav.settings", locale))}</a>
        <script>
        (function () {{
          if (window.__sitekpiPackSearch) return;
          window.__sitekpiPackSearch = true;
          const input = document.querySelector("[data-pack-search]");
          const empty = document.querySelector("[data-pack-search-empty]");
          const nav = document.querySelector("[data-pack-nav]");
          if (!input || !nav) return;
          const cats = () => Array.from(nav.querySelectorAll(".pack-cat"));
          input.addEventListener("input", () => {{
            const q = (input.value || "").trim().toLowerCase();
            let any = false;
            cats().forEach((cat) => {{
              let hit = false;
              cat.querySelectorAll(".pack-cat-body a").forEach((a) => {{
                const hay = (a.getAttribute("data-pack-q") || a.textContent || "").toLowerCase();
                const show = !q || hay.includes(q);
                a.hidden = !show;
                if (show) hit = true;
              }});
              cat.hidden = Boolean(q) && !hit;
              if (q && hit) cat.open = true;
              if (hit) any = true;
            }});
            if (empty) empty.hidden = !(q && !any);
          }});
        }})();
        </script>
    """
