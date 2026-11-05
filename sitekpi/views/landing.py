"""Public landing page (/) — ja / en / ko. Layout and order: docs/plan s01 (screens/01-home.dc.html)."""

from __future__ import annotations

from typing import Any

from markupsafe import Markup

from sitekpi.i18n.landing_l10n import CONTACT_URL, FEATURE_IMAGES, LANDING, SAMPLE_KEYS, WHO_STICKERS
from sitekpi.stickers import sticker_for
from sitekpi.templating import render, static_url
from sitekpi.views.seo import base_url, seo_context

# The GA4 report on the left of 「GA4 との違い」 is an illustration: made-up rows
GA_ROWS = [
    ["/", "12,480", "9,812", "58.1%", "0:52", "1.4"],
    ["/products/", "6,233", "5,410", "61.3%", "1:08", "2.1"],
    ["/cart", "2,104", "1,977", "72.4%", "0:41", "0.3"],
    ["/blog/…", "1,890", "1,702", "44.0%", "2:13", "0.0"],
    ["/contact", "812", "790", "66.8%", "0:37", "0.6"],
    ["(other)", "4,617", "3,980", "52.9%", "0:49", "0.8"],
]
GUESS_EVENTS = [["page_view", "68,500"], ["view_item", "33,904"], ["add_to_cart", "10,800"],
                ["begin_checkout", "3,620"], ["purchase", "1,580"]]
PICK_PROPS = [["Demo Shop JP", "384920117"], ["Corporate Site", "391022845"], ["Owned Media Blog", "402551390"]]
FIX_EVENTS = ["add_to_cart", "cart_add", "view_cart"]
BAR_HEIGHTS = [100, 64, 34, 12]
SAMPLE_WORST = [2, 3, 1, 2, 3, 2]  # which bar is the biggest drop (orange) on each sample card


def _counts() -> dict[str, int]:
    from sitekpi.metrics.help import HELP
    from sitekpi.packs import INDUSTRIES
    from sitekpi.selection import BEHAVIORS

    n_ind = sum(1 for s, m in INDUSTRIES.items() if not m.get("virtual") and not s.startswith("type-"))
    return {"n_ind": n_ind, "n_beh": len(BEHAVIORS), "n_metric": len(HELP)}


def _fill(value: Any, n: dict[str, int]) -> Any:
    """Put the catalog counts into every string of the copy ({n_ind} …)."""
    if isinstance(value, str):
        return value.format(**n) if "{" in value else value
    if isinstance(value, list):
        return [_fill(v, n) for v in value]
    if isinstance(value, dict):
        return {k: _fill(v, n) for k, v in value.items()}
    return value


def landing_context(loc: str) -> dict[str, Any]:
    n = _counts()
    c = _fill(LANDING[loc], n)
    img = {k: static_url(f"img/lp/{k}-{loc}.webp") for k in ("hero", "state", "flow", "watch", "notice", "gloss")}
    features = []
    for i, (f, key) in enumerate(zip(c["features"], FEATURE_IMAGES)):
        features.append({**f, "num": f"0{i + 1}", "img": key, "src": img.get(key, ""), "flip": i % 2 == 1})
    who = []
    for (k, v), sticker in zip(c["who"], WHO_STICKERS):
        st = sticker_for(sticker) or {}
        who.append({"k": k, "v": v, "img": st.get("url", ""), "still": st.get("still_url", "")})
    samples = []
    for i, ((goal, ind, steps), (b, ind_key)) in enumerate(zip(c["samples"], SAMPLE_KEYS)):
        bars = [{"h": h, "worst": j == SAMPLE_WORST[i]} for j, h in enumerate(BAR_HEIGHTS)]
        samples.append({"goal": goal, "ind": ind, "steps": steps, "bars": bars, "b": b, "i": ind_key,
                         "href": f"/samples?b={b}&i={ind_key}"})
    return {
        "c": c, "n": n, "img": img, "features": features, "who": who, "samples": samples,
        "ga_rows": GA_ROWS, "guess_events": GUESS_EVENTS, "pick_props": PICK_PROPS, "fix_events": FIX_EVENTS,
        "auth_perm": Markup(c["mock_auth_perm"]), "contact_url": CONTACT_URL,
    }


def render_landing(*, locale: str, connected: bool = False) -> str:
    loc = locale if locale in LANDING else "ja"
    ctx = landing_context(loc)
    c = ctx["c"]
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
        "landing.html", loc=loc, page="home", connected=connected, lq="" if loc == "ja" else f"?lang={loc}", path="/",
        seo=seo_context(path="/", loc=loc, title=c["meta_title"], description=c["meta_desc"], jsonld=jsonld),
        **ctx,
    )
