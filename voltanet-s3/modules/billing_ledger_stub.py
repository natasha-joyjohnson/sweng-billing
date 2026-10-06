"""Billing ledger (pair A) · STUB, step 3.
Knows every priced or pending session for ten years.
Each method only returns the fixed answer from interfaces-S3-pairA.txt."""
from datetime import datetime
from decimal import Decimal


class BillingLedger:
    def record(self, session_id, driver_id, unit_id, started, stopped,
               start_reading_kwh, end_reading_kwh, energy_kwh,
               quote_reference, amount_eur, status):
        """Answers the ledger entry (entry_id, status, keep_until); an already recorded session: the existing entry."""
        return {"entry_id": "L-0001", "status": "recorded",
                "keep_until": datetime(2036, 10, 5, 14, 30)}

    def sessions_of(self, driver_id):
        """Answers that driver's ledger entries, newest first; [] if none."""
        return [{"session_id": "S-1", "unit_id": "U3",
                 "started": datetime(2026, 10, 5, 13, 20),
                 "energy_kwh": Decimal("18.400"), "amount_eur": Decimal("9.28"),
                 "status": "recorded"}]

    def remove_personal_data(self, driver_id):
        """Answers how many entries had the driver removed (an int); 0 if none."""
        return 1
