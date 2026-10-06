"""Quotes register (pair B) · FIRST REAL VERSION (step 5).

Knows every quote issued: unit price, fixed fees, tariff, reference, valid until.
A quote is binding (F7): once stored it is never changed. It does not know which
quote the driver accepted (S4 does) and does not decide whether a quote has
expired (Billing desk compares valid_until).
The stub this replaces is kept as quotes_register_stub.py.
"""
from datetime import datetime
from decimal import Decimal


class QuotesRegister:
    def __init__(self):
        self._quotes = {}          # reference (text) -> quote (dict)
        self._last_number = 0      # references count up: Q-0001, Q-0002, ...

    def store_quote(self, unit_id, price_per_kwh, fixed_fees, tariff, valid_until):
        """Stores a new quote and answers its reference (text); None if a price is negative."""
        if price_per_kwh < 0 or fixed_fees < 0:
            return None
        self._last_number += 1
        reference = f"Q-{self._last_number:04d}"
        self._quotes[reference] = {
            "reference": reference,
            "unit_id": unit_id,
            "price_per_kwh": price_per_kwh,
            "fixed_fees": fixed_fees,
            "tariff": tariff,
            "valid_until": valid_until,
        }
        return reference

    def quote_by_reference(self, reference):
        """The quote with that reference, even if expired (a dict); None if there is none."""
        quote = self._quotes.get(reference)
        return dict(quote) if quote is not None else None   # a copy: callers cannot change it


# ---------------------------------------------------------------------------
# Tests: one per acceptance criterion (interfaces-S3-pairB.txt, Quotes register)
# ---------------------------------------------------------------------------

def test_stored_quote_is_found_by_its_reference():
    register = QuotesRegister()
    ref = register.store_quote("U3", Decimal("0.45"), Decimal("1.00"), "site standard",
                               datetime(2026, 10, 5, 13, 45))
    assert ref == "Q-0001"
    quote = register.quote_by_reference("Q-0001")
    assert quote["unit_id"] == "U3"
    assert quote["price_per_kwh"] == Decimal("0.45")
    assert quote["fixed_fees"] == Decimal("1.00")
    assert quote["tariff"] == "site standard"
    assert quote["valid_until"] == datetime(2026, 10, 5, 13, 45)


def test_unknown_reference_answers_none():
    register = QuotesRegister()
    assert register.quote_by_reference("Q-9999") is None


def test_new_quote_gets_new_reference_and_old_one_is_unchanged():
    register = QuotesRegister()
    register.store_quote("U3", Decimal("0.45"), Decimal("1.00"), "site standard",
                         datetime(2026, 10, 5, 13, 45))
    ref = register.store_quote("U3", Decimal("0.99"), Decimal("1.00"), "site standard",
                               datetime(2026, 10, 5, 14, 15))
    assert ref == "Q-0002"
    assert register.quote_by_reference("Q-0001")["price_per_kwh"] == Decimal("0.45")


if __name__ == "__main__":
    test_stored_quote_is_found_by_its_reference()
    test_unknown_reference_answers_none()
    test_new_quote_gets_new_reference_and_old_one_is_unchanged()
    print("Quotes register: all 3 tests passed.")
