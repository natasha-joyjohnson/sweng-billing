"""The rest of VoltaNet, played by us.

Each class below stands in for one subsystem. It answers the published
contracts (28 September) with plausible, fixed answers, and it writes down
every call your subsystem makes to it, so that run.py can show the use case
crossing the edge.

You do not change this file. Your subsystem talks to these classes through
the object called `others` that it receives when it is created:

    others.s1.session_record("S-1")
    others.s4.departure_and_reservation("U2")
"""
from datetime import datetime, timedelta
from decimal import Decimal

CALLS = []          # every call made across the edge, in order: (from, to, what, answer)


def _log(frm, to, what, answer):
    CALLS.append((frm, to, what, answer))
    return answer


NOW = datetime(2026, 10, 5, 14, 30)


class S1StandIn:
    """S1 · sessions and charge-point gateway, as the other subsystems see it."""

    def session_record(self, session_id):
        """Contract s1-session-record (S3 asks): what happened in this session?"""
        record = {"session_id": session_id, "unit_id": "U3", "driver_id": "D-17",
                  "started": NOW - timedelta(hours=1, minutes=10), "stopped": NOW,
                  "start_reading_kwh": Decimal("10234.120"), "end_reading_kwh": Decimal("10252.520"),
                  "energy_kwh": Decimal("18.400"), "why_ended": "unplugged",
                  "decided_offline": False}
        return _log("?", "S1", f"session_record({session_id!r})", record)

    def session_state(self, unit_id):
        """Contract s1-session-state (S4 asks): what is this unit doing now?"""
        state = {"unit_id": unit_id, "state": "available", "power_kw": 0.0,
                 "last_heard": NOW - timedelta(seconds=20)}
        return _log("?", "S1", f"session_state({unit_id!r})", state)

    def stations_near_driver(self, latitude, longitude):
        """Contract s1-stations-near-driver (S4 asks): which units near here are working and free?"""
        units = [{"unit_id": "U2", "site_id": "SITE-1", "state": "available", "how_old_s": 20},
                 {"unit_id": "U5", "site_id": "SITE-1", "state": "available", "how_old_s": 35}]
        return _log("?", "S1", f"stations_near_driver({latitude}, {longitude})", units)


class S2StandIn:
    """S2 · load management, as the other subsystems see it."""

    def share_out_power(self, site_id, units, site_limit_kw, what_changed):
        """Contract s2-share-out-power (S1 asks): a limit for every unit whose limit changes."""
        limits = {"U3": {"limit_kw": 22.0, "why": "a session is starting"},
                  "U1": {"limit_kw": 11.0, "why": "another car arrived"}}
        return _log("?", "S2", f"share_out_power({site_id!r}, {len(units)} units, {site_limit_kw} kW, {what_changed!r})", limits)

    def power_estimate(self, unit_id, starts, ends):
        """Contract s2-power-estimate (S3 asks): how much power will a session probably get?"""
        estimate = {"low_kw": 7.0, "high_kw": 22.0, "confidence": "medium"}
        return _log("?", "S2", f"power_estimate({unit_id!r})", estimate)

    def latest_power_notice(self, session_id):
        """Contract s2-power-reduced (S4 asks, after reconnecting): the latest notice for a session."""
        notice = {"session_id": session_id, "new_power_kw": 11.0, "reason": "another car arrived",
                  "at": NOW - timedelta(minutes=3)}
        return _log("?", "S2", f"latest_power_notice({session_id!r})", notice)


class S4StandIn:
    """S4 · driver app and reservations, as the other subsystems see it."""

    def __init__(self):
        self.accepted = {"S-1": {"reference": "Q-0001", "accepted_at": NOW - timedelta(hours=1, minutes=12)}}

    def departure_and_reservation(self, unit_or_site):
        """Contract s4-departure-and-reservation (S1 and S2 ask)."""
        answer = {"reservation": None,
                  "departures": {"S-1": NOW + timedelta(minutes=50), "S-2": NOW + timedelta(hours=2)}}
        return _log("?", "S4", f"departure_and_reservation({unit_or_site!r})", answer)

    def price_accepted(self, session_id):
        """Contract s4-price-accepted (S3 asks): which quote did the driver accept?"""
        return _log("?", "S4", f"price_accepted({session_id!r})", self.accepted.get(session_id))

    def session_started(self, session_id, driver_id, unit_id, power_kw):
        """S1 tells S4 a session has started (#4, row 7). No contract was written for it: a known gap."""
        return _log("?", "S4", f"session_started({session_id!r}, {driver_id!r}, {unit_id!r}, {power_kw})", "received")

    def power_reduced(self, session_id, new_power_kw, reason):
        """Contract s2-power-reduced (S2 tells S4)."""
        return _log("?", "S4", f"power_reduced({session_id!r}, {new_power_kw}, {reason!r})", "received")

    def session_cost(self, session_id, amount_eur):
        """Contract s3-session-cost (S3 tells S4)."""
        return _log("?", "S4", f"session_cost({session_id!r}, {amount_eur})", "received")


class ChargePoints:
    """The units at the site, as S1 sees them: S1 is the only subsystem that talks to them."""

    def start(self, unit_id, limit_kw):
        return _log("?", "unit", f"start({unit_id!r}, {limit_kw} kW)", "delivering")

    def apply_limit(self, unit_id, limit_kw):
        return _log("?", "unit", f"apply_limit({unit_id!r}, {limit_kw} kW)", "applied")


class Others:
    """What your subsystem receives as `others`: the subsystems that are not yours.
    Yours is not here: others.sN is None for your own N, and this file has no
    class for it. Your own subsystem answers only through your own code."""

    def __init__(self, mine):
        self.s1 = _pick("S1", mine, lambda: S1StandIn())
        self.s2 = _pick("S2", mine, lambda: S2StandIn())
        self.s3 = _pick("S3", mine, lambda: S3StandIn())
        self.s4 = _pick("S4", mine, lambda: S4StandIn())
        self.charge_points = ChargePoints() if mine == "S1" else None
        for name in ("s1", "s2", "s3", "s4", "charge_points"):
            standin = getattr(self, name)
            if standin is not None:
                _wrap(standin, mine)


def _pick(name, mine, standin):
    """Subsystem `name` as yours sees it: None if it is yours, else played by us."""
    return None if name == mine else standin()


def _wrap(standin, mine):
    """Record the caller as `mine` on every call."""
    for attr in dir(standin):
        if attr.startswith("_"):
            continue
        method = getattr(standin, attr)
        if callable(method):
            def called(*args, _m=method, **kwargs):
                before = len(CALLS)
                answer = _m(*args, **kwargs)
                if len(CALLS) > before:
                    frm, to, what, ans = CALLS[-1]
                    CALLS[-1] = (mine, to, what, ans)
                return answer
            setattr(standin, attr, called)
