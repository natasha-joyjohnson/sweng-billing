"""Billing desk (pair A) · the COORDINATOR, written by hand in step 4.

It keeps no data and does no maths (team cards, 28 September): it does each
use case row by row, by calling the other modules and, for today, every other
subsystem (through self.others). When a module becomes real, the outside call
it needs moves into that module, as its card says.

The calls to pair B's modules use the names in interfaces-S3-pairB.txt:
  Tariff book      set_rule, prices_for
  Quotes register  record_quote (issues the reference), find_quote
  Price calculator amount
"""
from datetime import timedelta

QUOTE_VALID_FOR = timedelta(minutes=30)


class BillingDesk:
    def __init__(self, others, tariff_book, quotes_register, price_calculator, billing_ledger):
        self.others = others                        # the other subsystems
        self.tariff_book = tariff_book              # and our modules
        self.quotes_register = quotes_register
        self.price_calculator = price_calculator
        self.billing_ledger = billing_ledger

    # r1 · quotes a binding price before charging starts (#3, S4 asks)
    def price_quote(self, unit_id, at, energy_kwh=None, departure=None):
        # r1.1-r1.2: the site and campaign prices, and which one the rule in force picks
        prices = self.tariff_book.prices_for(unit_id, at)
        if prices is None or prices["applies"] is None:
            return None
        chosen = prices[prices["applies"]]
        # r1.3 (ask S2 for a power estimate) is left out: the quote is per kWh + fees,
        # nothing in it uses S2's estimate (our 28 Sep grid, #3 row 3).
        # r1.5: record the quote; the Quotes register issues its reference ("Q-0001"),
        # so the desk keeps no counter (it keeps no data).
        valid_until = at + QUOTE_VALID_FOR
        reference = self.quotes_register.record_quote(
            unit_id, chosen["price_per_kwh"], chosen["fixed_fee"], chosen["name"], valid_until)
        if reference is None:                       # the register could not record it
            return None
        return {"reference": reference, "unit_id": unit_id,
                "price_per_kwh": chosen["price_per_kwh"], "fixed_fees": chosen["fixed_fee"],
                "tariff": chosen["name"], "valid_until": valid_until}

    # r2 · prices a completed session (#12)
    def session_ended(self, session_id):
        # row 4 · ask S1 what happened in this session
        record = self.others.s1.session_record(session_id)
        if record is None:
            return None
        # r3.2 · a pending record (unit offline, no final reading yet): hold it unpriced
        if record.get("end_reading_kwh") is None:
            return self._keep(record, None, None, "pending")
        # row 5 · ask S4 which quote the driver accepted
        accepted = self.others.s4.price_accepted(session_id)
        quote = self.quotes_register.find_quote(accepted["reference"]) if accepted else None
        if quote is None:
            return self._keep(record, None, None, "review")
        # r3.5 · work out the amount (energy x quoted price + fees)
        amount = self.price_calculator.amount(
            quote["price_per_kwh"], record["energy_kwh"], quote["fixed_fees"])
        if amount is None:                          # the calculator refused the figures
            return self._keep(record, quote["reference"], None, "review")
        # r3.6 · record the priced session
        result = self._keep(record, quote["reference"], amount, "recorded")
        # row 6 · tell S4 what the session cost
        self.others.s4.session_cost(session_id, amount)
        return result

    def _keep(self, record, reference, amount, status):
        """Hands the session to the Billing ledger and answers what session_ended answers."""
        self.billing_ledger.record(
            record["session_id"], record["driver_id"], record["unit_id"],
            record["started"], record["stopped"],
            record["start_reading_kwh"], record.get("end_reading_kwh"), record["energy_kwh"],
            reference, amount, status)
        return {"session_id": record["session_id"], "amount_eur": amount, "status": status}

    # r3 · takes the rule for which tariff wins (#27, the commercial department)
    def take_tariff_rule(self, rule, valid_from, set_by):
        if not self.tariff_book.set_rule(rule, valid_from):
            return None
        return {"rule": rule, "valid_from": valid_from, "set_by": set_by}

    # r4 · gives a driver's charging history (S4, not in iteration one)
    def charging_history(self, driver_id, from_when=None, until_when=None):
        return [s for s in self.billing_ledger.sessions_of(driver_id)
                if (from_when is None or s["started"] >= from_when)
                and (until_when is None or s["started"] <= until_when)]

    # r5 · handles a request to delete personal data (S4, not in iteration one)
    def delete_personal_data(self, driver_id, when):
        count = self.billing_ledger.remove_personal_data(driver_id)
        return {"driver_id": driver_id, "sessions_anonymised": count,
                "kept": "amounts and meter readings, kept ten years (certified metering)",
                "done_at": when}
