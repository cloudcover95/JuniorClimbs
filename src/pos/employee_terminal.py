# path: src/pos/employee_terminal.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict

@dataclass
class MemberInfo:
    member_id: str
    name: str
    tier: str
    balance: float
    keychain_id: str
    status: str
    last_visit: Optional[str] = None

class EmployeeTerminal:
    """
    Employee terminal.
    Shows customer information on requisition (hard copy / privacy option available).
    Maintains hard land lines so enthusiasts are not deterred.
    """

    def __init__(self, data_store, pos_system):
        self.data_store = data_store
        self.pos = pos_system

    def on_keychain_swipe(self, barcode: str, privacy_mode: bool = False) -> dict:
        member = self.data_store.get_member_by_keychain(barcode)
        if not member:
            return {"status": "unknown"}

        info = MemberInfo(
            member_id=member["id"],
            name=member["name"],
            tier=member["tier"],
            balance=member.get("balance", 0.0),
            keychain_id=barcode,
            status=member.get("status", "active"),
            last_visit=member.get("last_visit")
        )

        display = {
            "name": info.name,
            "tier": info.tier,
            "balance": round(info.balance, 2),
            "status": info.status,
            "last_visit": info.last_visit or "First visit"
        }

        if privacy_mode:
            display["hard_copy_mode"] = True  # Print or secondary screen only

        return {
            "status": "recognized",
            "display": display,
            "session": self.pos.swipe_keychain(barcode)
        }

    def add_item_to_account(self, barcode: str, amount: float, item: str):
        return self.pos.add_purchase(barcode, amount, item)
