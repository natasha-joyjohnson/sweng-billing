"""Tariff book (pair B) · STUB: every method answers a fixed value."""
from datetime import datetime
from decimal import Decimal


class TariffBook:
    def record_rule(self, rule, valid_from, set_by):
        """True when the rule for which tariff wins is recorded (False if not a known rule)."""
        return True

    def add_tariff(self, unit_id, kind, name, price_per_kwh, fixed_fees, valid_from, valid_until):
        """True when a site or campaign tariff is recorded."""
        return True

    def tariff_for(self, unit_id, at):
        """The site and campaign prices for a unit at a time, and which applies (None if no tariff)."""
        return {"site": {"name": "site standard", "price_per_kwh": Decimal("0.45"),
                         "fixed_fees": Decimal("1.00")},
                "campaign": None,
                "applies": "site"}
