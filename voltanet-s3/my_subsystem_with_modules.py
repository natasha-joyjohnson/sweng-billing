"""Your subsystem: S3 · billing and tariffs.

FROM US, YOU COMPLETE IT. These methods are the EDGE of your subsystem: what
the rest of VoltaNet calls. Their names and what they are given come from the
published contracts and use cases; what happens behind them is yours.

Each docstring says who calls the method, and which of YOUR modules (from your
cards of 28 September) will answer it.

Step 4 (pair A): THIS IS THE COPY. Each method hands its request to the
Billing desk, which calls our modules row by row. The original, with fixed
answers, is still my_subsystem.py (python run.py).

`self.others` is the rest of VoltaNet, played by us: others.s1, others.s2, others.s4.
The calls your use case expects you to make through it:
  others.s1.session_record (row 4), others.s4.price_accepted (row 5),
  others.s4.session_cost (row 6)
"""
from billing_desk import BillingDesk
from billing_ledger import BillingLedger
from price_calculator import PriceCalculator
from quotes_register import QuotesRegister
from tariff_book import TariffBook


class S3Subsystem:
    def __init__(self, others):
        self.others = others
        # one object per module; the Billing desk (coordinator) gets the others
        self.tariff_book = TariffBook()
        self.quotes_register = QuotesRegister()
        self.price_calculator = PriceCalculator()
        self.billing_ledger = BillingLedger()
        self.billing_desk = BillingDesk(others, self.tariff_book, self.quotes_register,
                                        self.price_calculator, self.billing_ledger)

    def price_quote(self, unit_id, at, energy_kwh=None, departure=None):
        """Contract s3-price-quote (S4 asks; use case #3): a binding price before charging starts.
        Answers a quote with its reference, price per kWh, fixed fees,
        which tariff won, and until when it is valid.
        Answered by: Billing desk (your r1), using Tariff book, Quotes register, Price calculator."""
        return self.billing_desk.price_quote(unit_id, at, energy_kwh, departure)

    def session_ended(self, session_id):
        """Use case #12: price this completed session.
        Who tells S3 that a session has ended is a gap your team found (#12 row 3);
        until it is settled, run.py plays that part.
        Answers the amount owed.
        Answered by: Billing desk (your r2), using Quotes register, Price calculator, Billing ledger."""
        return self.billing_desk.session_ended(session_id)
