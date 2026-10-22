"""GA4 calls are batched: the board's numbers and the 行動フロー each take one round trip."""

from __future__ import annotations

from types import SimpleNamespace as NS

import sitekpi.ga4.data as d

INFO = {"property_id": "9", "property_name": "P", "account": "", "email": ""}


def _row(dims, mets):
    return NS(dimension_values=[NS(value=v) for v in dims], metric_values=[NS(value=str(v)) for v in mets])


class FakeClient:
    calls: list = []

    def __init__(self, credentials=None):
        pass

    def batch_run_reports(self, req):
        FakeClient.calls.append(req)
        reports = []
        for r in req.requests:
            dims = [x.name for x in r.dimensions]
            mets = [m.name for m in r.metrics]
            if not dims and len(mets) == 8:
                reports.append(NS(rows=[_row([], [1000, 1500, 4000, 0.6, 400, 2.6, 120, 90000])]))
            elif dims == ["sessionDefaultChannelGroup"] and mets == ["sessions"]:
                reports.append(NS(rows=[_row(["Direct"], [900]), _row(["Organic Search"], [600])]))
            elif dims == ["eventName"]:
                reports.append(NS(rows=[_row(["sign_up"], [50])]))
            elif not dims:
                reports.append(NS(rows=[_row([], [1200])]))
            elif dims == ["sessionDefaultChannelGroup"]:
                reports.append(NS(rows=[_row(["Direct"], [700]), _row(["Email"], [500])]))
            else:
                reports.append(NS(rows=[_row(["Direct", "sign_up"], [20]), _row(["Email", "sign_up"], [30])]))
        return NS(reports=reports)


def _patch(monkeypatch):
    FakeClient.calls = []
    monkeypatch.setattr(d, "BetaAnalyticsDataClient", FakeClient)
    monkeypatch.setattr(d, "connection_info", lambda s: INFO)
    monkeypatch.setattr(d, "creds_from_session", lambda s: object())
    monkeypatch.setattr(d, "HAS_DATA", True)
    monkeypatch.setattr(d, "HAS_GOOGLE_AUTH", True)


def test_overlay_is_one_round_trip(monkeypatch):
    _patch(monkeypatch)
    o, err = d.fetch_pack_overlay({}, period="28d", event_names=["sign_up", "purchase"], primary_event="sign_up")
    assert err is None and len(FakeClient.calls) == 1 and len(FakeClient.calls[0].requests) == 5
    assert o["uu"] == 1000 and o["engaged_rate"] == 60.0 and o["signups"] == 50
    assert o["event_counts"] == {"sign_up": 50, "purchase": 0} and o["_prev"]["uu"] == 1000
    assert o["channels"] == [("Direct", 60), ("Organic Search", 40)]


def test_flow_is_one_round_trip(monkeypatch):
    _patch(monkeypatch)
    f, err = d.fetch_flow({}, period="28d", events=["sign_up"])
    assert err is None and len(FakeClient.calls) == 1 and len(FakeClient.calls[0].requests) == 4
    assert f["entry"] == 1200 and f["entry_by"] == {"Direct": 700, "Email": 500}
    assert f["totals"] == {"sign_up": 50} and f["by_channel"]["Email"] == {"sign_up": 30}
