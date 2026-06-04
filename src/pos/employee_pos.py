# path: src/pos/employee_pos.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class MemberSession:
    member_id: str
    name: str
    tier: str
    balance: float
    keychain_id: str
    last_swipe: datetime
    status: str = "active"

class EmployeePOS:
    def __init__(self, data_store: Any, ledger: Any):
        self.data_store = data_store
        self.ledger = ledger
        self.active_sessions: Dict[str, MemberSession] = {}

    def swipe_keychain(self, barcode: str) -> dict:
        """Employee-facing swipe confirmation on monitor/UI."""
        member = self.data_store.get_member_by_keychain(barcode)
        if not member or member.get("status") != "active":
            return {"status": "denied", "reason": "inactive or invalid keychain"}

        session = MemberSession(
            member_id=member["id"],
            name=member["name"],
            tier=member["tier"],
            balance=member.get("balance", 0.0),
            keychain_id=barcode,
            last_swipe=datetime.now()
        )
        self.active_sessions[barcode] = session

        return {
            "status": "granted",
            "member_name": member["name"],
            "tier": member["tier"],
            "balance": round(session.balance, 2),
            "ui_message": f"Welcome {member['name']} — Swipe confirmed on monitor"
        }

    def add_purchase(self, barcode: str, amount: float, item: str, category: str = "merch"):
        if barcode not in self.active_sessions:
            return {"success": False, "reason": "No active session"}

        session = self.active_sessions[barcode]
        session.balance -= amount

        entry = self.ledger.record_entry(
            member_id=session.member_id,
            entry_type="purchase",
            amount=-amount,
            item=item,
            metadata={"category": category, "keychain": barcode}
        )

        self.data_store.update_balance(session.member_id, session.balance)

        return {
            "success": True,
            "new_balance": round(session.balance, 2),
            "tx_hash": entry.tx_hash,
            "message": f"{item} added. New balance: ${session.balance:.2f}"
        }

    def get_renewal_status(self, barcode: str):
        member = self.data_store.get_member_by_keychain(barcode)
        if not member:
            return {"status": "unknown"}
        return {
            "status": member.get("status"),
            "renewal_due": member.get("renewal_date"),
            "balance": round(member.get("balance", 0.0), 2),
            "call_for_renew": member.get("renewal_date", "") < "2026-07-01"
        }
