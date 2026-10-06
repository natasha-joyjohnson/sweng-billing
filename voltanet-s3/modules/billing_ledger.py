"""Billing ledger (pair A) · FIRST REAL VERSION, step 5.
Knows every priced or pending session for ten years.
Made from the Billing ledger blocks and acceptance criteria in interfaces-S3-pairA.txt.
The stub it replaces is kept as billing_ledger_stub.py: copy it back if anything breaks.
Data is kept in memory only (no files, no database), as step 5 asks.
"""
from datetime import datetime
from decimal import Decimal

KEEP_YEARS = 10


def _ten_years_after(when):
    """The same date and time ten years later (29 February becomes 28 February)."""
    try:
        return when.replace(year=when.year + KEEP_YEARS)
    except ValueError:
        return when.replace(year=when.year + KEEP_YEARS, day=28)


class BillingLedger:
    def __init__(self):
        self._entries = {}            # session id -> the entry, everything that was recorded
        self._next_number = 1

    # r1 · records a priced session and keeps it ten years, or holds it as pending
    def record(self, session_id, driver_id, unit_id, started, stopped,
               start_reading_kwh, end_reading_kwh, energy_kwh,
               quote_reference, amount_eur, status):
        """Answers the ledger entry (entry_id, status, keep_until); an already recorded session: the existing entry."""
        entry = self._entries.get(session_id)
        if entry is not None:
            if entry["status"] != "pending":
                return self._answer(entry)            # already recorded: unchanged
            # a pending one is updated when its record arrives (same entry id)
            entry.update(stopped=stopped, end_reading_kwh=end_reading_kwh,
                         energy_kwh=energy_kwh, quote_reference=quote_reference,
                         amount_eur=amount_eur, status=status,
                         keep_until=_ten_years_after(stopped))
            return self._answer(entry)
        entry = {"entry_id": f"L-{self._next_number:04d}", "session_id": session_id,
                 "driver_id": driver_id, "unit_id": unit_id,
                 "started": started, "stopped": stopped,
                 "start_reading_kwh": start_reading_kwh, "end_reading_kwh": end_reading_kwh,
                 "energy_kwh": energy_kwh, "quote_reference": quote_reference,
                 "amount_eur": amount_eur, "status": status,
                 "keep_until": _ten_years_after(stopped)}
        self._next_number += 1
        self._entries[session_id] = entry
        return self._answer(entry)

    @staticmethod
    def _answer(entry):
        return {"entry_id": entry["entry_id"], "status": entry["status"],
                "keep_until": entry["keep_until"]}

    # r2 · finds a driver's sessions ...
    def sessions_of(self, driver_id):
        """Answers that driver's ledger entries, newest first; [] if none."""
        found = [e for e in self._entries.values() if e["driver_id"] == driver_id]
        found.sort(key=lambda e: e["started"], reverse=True)
        return [{"session_id": e["session_id"], "unit_id": e["unit_id"],
                 "started": e["started"], "energy_kwh": e["energy_kwh"],
                 "amount_eur": e["amount_eur"], "status": e["status"]} for e in found]

    # r2 · ... and removes their personal data, keeping amounts and readings
    def remove_personal_data(self, driver_id):
        """Answers how many entries had the driver removed (an int); 0 if none."""
        count = 0
        for entry in self._entries.values():
            if entry["driver_id"] == driver_id:
                entry["driver_id"] = None             # only the link to the driver goes
                count += 1
        return count


# ---------------------------------------------------------------------------
# Tests: one per acceptance criterion in interfaces-S3-pairA.txt
# ---------------------------------------------------------------------------
STARTED = datetime(2026, 10, 5, 13, 20)
STOPPED = datetime(2026, 10, 5, 14, 30)


def _record_s1(ledger, amount, status, end_reading=Decimal("10252.520")):
    return ledger.record("S-1", "D-17", "U3", STARTED, STOPPED,
                         Decimal("10234.120"), end_reading, Decimal("18.400"),
                         "Q-0001", amount, status)


def test_1_records_a_priced_session_for_ten_years():
    ledger = BillingLedger()
    answer = _record_s1(ledger, Decimal("9.28"), "recorded")
    assert answer == {"entry_id": "L-0001", "status": "recorded",
                      "keep_until": datetime(2036, 10, 5, 14, 30)}
    assert ledger.sessions_of("D-17") == [
        {"session_id": "S-1", "unit_id": "U3", "started": STARTED,
         "energy_kwh": Decimal("18.400"), "amount_eur": Decimal("9.28"), "status": "recorded"}]


def test_2_pending_is_updated_but_recorded_never_changes():
    ledger = BillingLedger()
    held = _record_s1(ledger, None, "pending", end_reading=None)
    assert held["entry_id"] == "L-0001" and held["status"] == "pending"
    priced = _record_s1(ledger, Decimal("9.28"), "recorded")
    assert priced["entry_id"] == "L-0001" and priced["status"] == "recorded"
    again = _record_s1(ledger, Decimal("99.99"), "recorded")
    assert again == priced
    assert ledger.sessions_of("D-17")[0]["amount_eur"] == Decimal("9.28")


def test_3_unknown_driver_and_removal():
    ledger = BillingLedger()
    assert ledger.sessions_of("D-99") == []
    assert ledger.remove_personal_data("D-99") == 0
    _record_s1(ledger, Decimal("9.28"), "recorded")
    assert ledger.remove_personal_data("D-17") == 1
    assert ledger.sessions_of("D-17") == []
    still_there = _record_s1(ledger, Decimal("9.28"), "recorded")
    assert still_there["entry_id"] == "L-0001" and still_there["status"] == "recorded"


if __name__ == "__main__":
    for test in (test_1_records_a_priced_session_for_ten_years,
                 test_2_pending_is_updated_but_recorded_never_changes,
                 test_3_unknown_driver_and_removal):
        test()
        print("passed:", test.__name__)
    print("All 3 acceptance criteria pass.")
