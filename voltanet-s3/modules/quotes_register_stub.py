"""Quotes register (pair B) · STUB: every method answers a fixed value."""
from datetime import datetime
from decimal import Decimal


class QuotesRegister:
    def store_quote(self, unit_id, price_per_kwh, fixed_fees, tariff, valid_until):
        """The new quote's reference (None if a price is negative)."""
        return "Q-0001"

    def quote_by_reference(self, reference):
        """The quote with that reference, even if expired (None if there is none)."""
        return {"reference": "Q-0001", "unit_id": "U3", "price_per_kwh": Decimal("0.45"),
                "fixed_fees": Decimal("1.00"), "tariff": "site standard",
                "valid_until": datetime(2026, 10, 5, 13, 45)}
