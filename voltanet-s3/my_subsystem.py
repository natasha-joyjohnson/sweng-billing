"""Your subsystem: S3 · billing and tariffs.

FROM US, YOU COMPLETE IT. These methods are the EDGE of your subsystem: what
the rest of VoltaNet calls. Their names and what they are given come from the
published contracts and use cases; what happens behind them is yours.

Each docstring says who calls the method, and which of YOUR modules (from your
cards of 28 September) will answer it.

Step 1: replace each raise line with a fixed answer. After that, KEEP THIS FILE
AS IT IS: in step 4 you copy it to my_subsystem_with_modules.py and change the
copy, so that this version always runs (python run.py).

`self.others` is the rest of VoltaNet, played by us: others.s1, others.s2, others.s4.
The calls your use case expects you to make through it:
  others.s1.session_record (row 4), others.s4.price_accepted (row 5),
  others.s4.session_cost (row 6)
"""
from datetime import datetime, timedelta
from decimal import Decimal


class S3Subsystem:
    def __init__(self, others):
        self.others = others

    def price_quote(self, unit_id, at, energy_kwh=None, departure=None):
        """Contract s3-price-quote (S4 asks; use case #3): a binding price before charging starts.
        Answers a quote with its reference, price per kWh, fixed fees,
        which tariff won, and until when it is valid.
        Answered by: Billing desk (your r1), using Tariff book, Quotes register, Price calculator."""
        raise NotImplementedError("price_quote in my_subsystem.py")

    def session_ended(self, session_id):
        """Use case #12: price this completed session.
        Who tells S3 that a session has ended is a gap your team found (#12 row 3);
        until it is settled, run.py plays that part.
        Answers the amount owed.
        Answered by: Billing desk (your r2), using Quotes register, Price calculator, Billing ledger."""
        raise NotImplementedError("session_ended in my_subsystem.py")
