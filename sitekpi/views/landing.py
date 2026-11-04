"""Public landing page (/) — purpose, who it's for, features, how it works, FAQ (ja / en / ko)."""

from __future__ import annotations

from typing import Any

from sitekpi.i18n.landing_l10n import LANDING
from sitekpi.templating import render
from sitekpi.views.seo import base_url, seo_context


def _counts() -> dict[str, int]:
    from sitekpi.metrics.help import HELP
    from sitekpi.packs import INDUSTRIES
    from sitekpi.selection import BEHAVIORS

    n_ind = sum(1 for s, m in INDUSTRIES.items() if not m.get("virtual") and not s.startswith("type-"))
    return {"n_ind": n_ind, "n_beh": len(BEHAVIORS), "n_metric": len(HELP)}


def render_landing(*, locale: str) -> str:
    loc = locale if locale in LANDING else "ja"
    c = LANDING[loc]
    n = _counts()
    features = [[k, v.format(**n)] for k, v in c["features"]]
    jsonld = [
        {
            "@context": "https://schema.org", "@type": "SoftwareApplication",
            "name": "SiteKPI", "url": base_url() + "/", "applicationCategory": "BusinessApplication",
            "operatingSystem": "Web", "description": c["meta_desc"], "inLanguage": loc,
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
        },
        {
            "@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in c["faq"]],
        },
    ]
    return render(
        "landing.html", loc=loc, c=c, features=features, n=n, page="home",
        lq="" if loc == "ja" else f"?lang={loc}", path="/",
        seo=seo_context(path="/", loc=loc, title=c["meta_title"], description=c["meta_desc"], jsonld=jsonld),
    )
