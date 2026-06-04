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
    Employee-facing terminal.
    Shows customer information on requisition (hard copy option available).
    Maintains hard land lines / privacy-friendly flow to not deter enthusiasts.
    """

    def __init__(self, data_store, pos_system):
        self.data_store = data_store
        self.pos = pos_system

    def on_keychain_swipe(self, barcode: str, show_hard_copy: bool = False) -> dict:
        member = self.data_store.get_member_by_keychain(barcode)
        if not member:
            return {"status": "unknown", "message": "Keychain not recognized"}

        info = MemberInfo(
            member_id=member["id"],
            name=member["name"],
            tier=member["tier"],
            balance=member.get("balance", 0.0),
            keychain_id=barcode,
            status=member.get("status", "active"),
            last_visit=member.get("last_visit")
        )

        # Employee sees clean summary on monitor
        display = {
            "name": info.name,
            "tier": info.tier,
            "balance": round(info.balance, 2),
            "status": info.status,
            "last_visit": info.last_visit or "First visit"
        }

        if show_hard_copy:
            # Print or show on secondary screen for privacy-conscious members
            display["hard_copy_ready"] = True

        return {
            "status": "recognized",
            "display": display,
            "session": self.pos.swipe_keychain(barcode)
        }

    def add_item_to_account(self, barcode: str, amount: float, item: str):
        return self.pos.add_purchase(barcode, amount, item)
