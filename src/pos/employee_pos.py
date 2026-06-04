# path: src/pos/employee_pos.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict

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
    def __init__(self, data_store, ledger):
        self.data_store = data_store
        self.ledger = ledger
        self.active_sessions: Dict[str, MemberSession] = {}

    def swipe_keychain(self, barcode: str) -> dict:
        member = self.data_store.get_member_by_keychain(barcode)
        if not member or member.get("status") != "active":
            return {"status": "denied", "reason": "inactive or invalid"}

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
            "balance": session.balance,
            "ui_message": f"Welcome {member['name']} — Swipe confirmed"
        }

    def add_purchase(self, barcode: str, amount: float, item: str, category: str = "merch"):
        if barcode not in self.active_sessions:
            return {"success": False, "reason": "No active session"}

        session = self.active_sessions[barcode]
        session.balance -= amount

        # Record in second brain controlled ledger (Web3-style hash chain)
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
            "new_balance": session.balance,
            "tx_hash": entry.tx_hash,
            "message": f"{item} added. New balance: ${session.balance:.2f}"
        }

    def inject_member_discount(self, barcode: str, percent: float, reason: str):
        """Employee or second brain triggered targeted discount."""
        if barcode not in self.active_sessions:
            return {"success": False}
        session = self.active_sessions[barcode]
        discount_amount = session.balance * (percent / 100)
        session.balance += discount_amount  # positive because it's a credit

        entry = self.ledger.inject_discount(session.member_id, discount_amount, reason)
        self.data_store.update_balance(session.member_id, session.balance)

        return {
            "success": True,
            "new_balance": session.balance,
            "tx_hash": entry.tx_hash
        }
