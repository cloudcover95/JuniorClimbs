# path: src/pos/employee_pos.py

import time
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
    def __init__(self, data_store):
        self.data_store = data_store  # JuniorMemSys or local Parquet/SQLite
        self.active_sessions: Dict[str, MemberSession] = {}

    def swipe_keychain(self, barcode: str) -> dict:
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
            "balance": session.balance,
            "ui_message": f"Welcome {member['name']} — Swipe confirmed on {session.last_swipe.strftime('%H:%M')}"
        }

    def add_purchase(self, barcode: str, amount: float, item: str, category: str = "merch"):
        if barcode not in self.active_sessions:
            return {"success": False, "reason": "No active session"}

        session = self.active_sessions[barcode]
        session.balance -= amount

        # Persist to data store
        self.data_store.update_balance(session.member_id, session.balance, item, category)

        return {
            "success": True,
            "new_balance": session.balance,
            "message": f"{item} added. New balance: ${session.balance:.2f}"
        }

    def get_renewal_status(self, barcode: str):
        member = self.data_store.get_member_by_keychain(barcode)
        if not member:
            return {"status": "unknown"}
        return {
            "status": member.get("status"),
            "renewal_due": member.get("renewal_date"),
            "balance": member.get("balance", 0.0)
        }
