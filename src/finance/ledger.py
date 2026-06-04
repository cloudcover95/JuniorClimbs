# path: src/finance/ledger.py

import time
import hashlib
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

@dataclass
class LedgerEntry:
    timestamp: float
    member_id: str
    entry_type: str  # 'purchase', 'discount', 'renewal', 'adjustment'
    amount: float
    item: str
    metadata: Dict
    tx_hash: str  # Web3-style immutable commit hash

class FinanceLedger:
    """
    Sovereign business second brain controlled ledger.
    Supports on-chain style immutable commits (hash chain) for taxes, balance sheets, audits.
    Can be later anchored to real Web3 (e.g. via web3node).
    """

    def __init__(self, data_store):
        self.data_store = data_store
        self.chain: List[LedgerEntry] = []

    def _create_tx_hash(self, previous_hash: str, entry: dict) -> str:
        data = previous_hash + str(entry)
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def record_entry(self, member_id: str, entry_type: str, amount: float, item: str, metadata: Optional[Dict] = None) -> LedgerEntry:
        previous_hash = self.chain[-1].tx_hash if self.chain else "genesis"
        entry_dict = {
            "timestamp": time.time(),
            "member_id": member_id,
            "entry_type": entry_type,
            "amount": amount,
            "item": item,
            "metadata": metadata or {}
        }
        tx_hash = self._create_tx_hash(previous_hash, entry_dict)

        entry = LedgerEntry(
            timestamp=entry_dict["timestamp"],
            member_id=member_id,
            entry_type=entry_type,
            amount=amount,
            item=item,
            metadata=metadata or {},
            tx_hash=tx_hash
        )
        self.chain.append(entry)

        # Persist to second brain (JuniorMemSys / Parquet)
        self.data_store.append_ledger_entry(asdict(entry))
        return entry

    def get_member_balance(self, member_id: str) -> float:
        balance = 0.0
        for entry in self.chain:
            if entry.member_id == member_id:
                if entry.entry_type in ["purchase", "adjustment"]:
                    balance += entry.amount
                elif entry.entry_type == "discount":
                    balance += entry.amount  # negative amount for discount
        return balance

    def inject_discount(self, member_id: str, percent: float, reason: str):
        """Second brain or admin can inject targeted or global discounts."""
        amount = -abs(percent)  # negative = credit
        return self.record_entry(member_id, "discount", amount, reason, {"injected_by": "second_brain"})

    def get_audit_trail(self, member_id: Optional[str] = None) -> List[dict]:
        if member_id:
            return [asdict(e) for e in self.chain if e.member_id == member_id]
        return [asdict(e) for e in self.chain]
