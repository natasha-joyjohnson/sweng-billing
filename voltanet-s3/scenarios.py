"""One use case per team, the one walked on Monday 5 October. run.py runs
the team's one. Each step says who calls whom, and what the published
resolution expects to cross the edge.
"""
from datetime import timedelta

from standins import NOW

UNITS = [{"unit_id": f"U{i}", "state": s, "power_kw": p, "last_heard": NOW - timedelta(seconds=a)}
         for i, s, p, a in [(1, "charging", 22.0, 10), (2, "available", 0.0, 15), (3, "charging", 22.0, 12),
                            (4, "available", 0.0, 9), (5, "charging", 50.0, 400), (6, "faulted", 0.0, 30)]]


def s1(me):
    return [
        ("#4 · A driver wants to start charging at a unit they have not booked", None, None, None),
        ("row 1 · the charge point calls your cable_connected(): a cable is connected at U3, driver D-17",
         lambda: me.cable_connected("U3", "D-17", NOW),
         [("S4", "departure_and_reservation", "row 2 · S1 asks S4: is this unit reserved?"),
          ("S2", "share_out_power", "row 5 · S1 asks S2 to share out the site's power"),
          ("unit", "start", "row 1 · S1 tells the unit to start at its limit"),
          ("S4", "session_started", "row 7 · S1 tells S4 a session has started")], None),
        ("then · S4 calls your session_state(): what is U3 doing now?", lambda: me.session_state("U3"), [], None),
    ]


def s2(me):
    return [
        ("#31 · A charge point wants to be told the most it may deliver right now", None, None, None),
        ("row 2 · S1 calls your share_out_power(): share out SITE-1's power (a session ended at U4; limit 150 kW)",
         lambda: me.share_out_power("SITE-1", UNITS, 150.0, "session S-3 ended at U4"),
         [("S4", "departure_and_reservation", "row 3 · S2 asks S4: when does each driver want to leave?"),
          ("S4", "power_reduced", "row 5 · S2 tells S4 of each reduction (only if a limit went down)")], None),
    ]


def s3(me):
    return [
        ("#12 · A driver wants to pay for a completed session", None, None, None),
        ("first · S4 calls your price_quote(): a quote for U3 (as in #3, before the session)",
         lambda: me.price_quote("U3", NOW - timedelta(hours=1, minutes=15)), [], None),
        ("row 3 · run.py calls your session_ended(): price the completed session S-1 (who tells S3 is a gap you found)",
         lambda: me.session_ended("S-1"),
         [("S1", "session_record", "row 4 · S3 asks S1: what happened in this session?"),
          ("S4", "price_accepted", "row 5 · S3 asks S4: which quote did the driver accept?"),
          ("S4", "session_cost", "row 6 · S3 tells S4 what the session cost")], None),
    ]


def s4(me):
    return [
        ("#2 · A driver wants to reserve a charge point up to 30 minutes ahead", None, None, None),
        ("row 1 · the driver's app calls your reserve(): reserve U2, from 20 minutes from now",
         lambda: me.reserve("D-7", "U2", NOW + timedelta(minutes=20), NOW),
         [("S1", "session_state", "row 2 · S4 asks S1: is it working and free?")], None),
        ("then · S1 calls your departure_and_reservation(): is U2 reserved? (as in #4, row 2)",
         lambda: me.departure_and_reservation("U2"), [], None),
    ]


SCENARIOS = {"S1": s1, "S2": s2, "S3": s3, "S4": s4}
