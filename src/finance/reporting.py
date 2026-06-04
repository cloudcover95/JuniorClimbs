# path: src/finance/reporting.py

import csv
from typing import List, Dict
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

class FinanceReporting:
    """
    Portable CSV/Excel reporting layer on top of the Second Brain ledger.
    Fills gaps for balance sheets, tax exports, P&L style reports.
    """

    def __init__(self, ledger):
        self.ledger = ledger

    def export_ledger_to_csv(self, filepath: str, member_id: str = None):
        entries = self.ledger.get_audit_trail(member_id)
        if not entries:
            return False
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=entries[0].keys())
            writer.writeheader()
            writer.writerows(entries)
        return True

    def generate_balance_sheet(self, as_of: str = None) -> Dict:
        # Simple aggregated view; can be extended
        total_income = sum(e["amount"] for e in self.ledger.chain if e["amount"] > 0)
        total_expenses = sum(abs(e["amount"]) for e in self.ledger.chain if e["amount"] < 0)
        return {
            "as_of": as_of or "latest",
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net": total_income + total_expenses
        }

    def export_balance_sheet_to_excel(self, filepath: str):
        if not HAS_PANDAS:
            return False
        data = [self.generate_balance_sheet()]
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False)
        return True
