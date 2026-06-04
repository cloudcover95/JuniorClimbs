# path: src/admin/reporting.py

from fastapi import FastAPI
from typing import Optional

app = FastAPI(title="JuniorClimbs Reporting")

# In real deployment these would query the data store / ledger

@app.get("/maintenance/overdue")
def get_overdue_maintenance():
    # Would call maintenance.get_overdue()
    return {"overdue": "[Live data from MaintenanceSystem]"}

@app.get("/finance/balance-sheet")
def get_balance_sheet(as_of: Optional[str] = None):
    # Would call finance_reporting.generate_balance_sheet()
    return {"balance_sheet": "[Live data from FinanceReporting]"}

@app.get("/finance/ledger")
def get_ledger(member_id: Optional[str] = None):
    # Would call ledger.get_audit_trail(member_id)
    return {"ledger": "[Live immutable audit trail]"}
