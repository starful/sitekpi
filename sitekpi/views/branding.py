"""SiteKPI brand chrome — logo link + favicon head tags."""

from __future__ import annotations

BRAND_NAME = "SiteKPI"
BRAND_DOMAIN = "sitekpi.net"


def brand_head_links() -> str:
    """Favicon / touch icon link tags for HTML <head>."""
    return """
  <link rel="icon" href="/static/favicon.ico" sizes="any" />
  <link rel="icon" href="/static/favicon.svg" type="image/svg+xml" />
  <link rel="icon" href="/static/favicon-32.png" type="image/png" sizes="32x32" />
  <link rel="apple-touch-icon" href="/static/apple-touch-icon.png" />
""".rstrip()


def brand_logo_html(*, href: str = "/", css_class: str = "logo") -> str:
    """Rail / header logo: mark + SiteKPI word (Site navy, KPI blue)."""
    return (
        f'<a class="{css_class}" href="{href}">'
        f'<img class="logo-mark" src="/static/favicon.svg" width="36" height="36" alt="" />'
        f'<span class="logo-text"><span class="logo-site">Site</span>'
        f'<span class="logo-kpi">KPI</span></span></a>'
    )


def brand_logo_css() -> str:
    """Shared CSS for brand_logo_html (rail or top bar)."""
    return """
    .logo, a.brand.logo {
      display: inline-flex; align-items: center; gap: 12px;
      text-decoration: none; color: #152033;
      font-family: "DM Sans", "IBM Plex Sans JP", "Noto Sans JP", sans-serif;
      font-weight: 800; font-size: 1.4rem; letter-spacing: -0.02em;
    }
    .logo .logo-mark, a.brand.logo .logo-mark {
      flex: 0 0 auto; width: 36px; height: 36px; display: block;
    }
    .logo .logo-text, a.brand.logo .logo-text {
      display: inline-flex; align-items: baseline;
    }
    .logo .logo-site, a.brand.logo .logo-site { color: #152033; }
    .logo .logo-kpi, a.brand.logo .logo-kpi { color: #2f6fed; }
"""
