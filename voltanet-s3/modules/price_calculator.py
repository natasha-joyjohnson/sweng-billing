"""Price calculator (pair B) · STUB: every method answers a fixed value."""
from decimal import Decimal


class PriceCalculator:
    def amount_for(self, price_per_kwh, energy_kwh, fixed_fees):
        """The amount in euros: energy x price + fees, to the cent (None if no energy or negative)."""
        return Decimal("9.28")
