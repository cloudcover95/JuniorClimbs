# path: src/finance/second_brain_ledger.py
# The on-suite business second brain (JuniorMemSys) has full control here.
# It can create offers, run promotions, inject global or member-specific discounts,
# and maintain immutable audit trails for taxes and balance sheets.

from .ledger import FinanceLedger

class SecondBrainLedger(FinanceLedger):
    def create_global_offer(self, percent: float, valid_until: str, target_tiers: list = None):
        """Second brain autonomously creates and broadcasts offers."""
        offer = {
            "type": "global_discount",
            "percent": percent,
            "valid_until": valid_until,
            "target_tiers": target_tiers or ["all"]
        }
        # In real system this would be pushed to all active POS terminals + member apps
        return offer

    def auto_renewal_check(self):
        """Second brain runs periodic audit and flags members for renewal."""
        flagged = []
        for member in self.data_store.get_all_members():
            if member.get("renewal_date") and member["renewal_date"] < "2026-07-01":
                flagged.append(member)
        return flagged
