# path: src/finance/ledger.py

import time
import hashlib
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

@dataclass
class LedgerEntry:
    timestamp: float
    member_id: str
    entry_type: str
    amount: float
    item: str
    metadata: Dict
    tx_hash: str

class FinanceLedger:
    """Second brain controlled immutable ledger with Web3-style hash chaining."""

    def __init__(self, data_store):
        self.data_store = data_store
        self.chain: List[LedgerEntry] = []

    def _create_tx_hash(self, previous_hash: str, entry: dict) -> str:
        data = previous_hash + str(sorted(entry.items()))
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

        entry = LedgerEntry(**entry_dict, tx_hash=tx_hash)
        self.chain.append(entry)
        self.data_store.append_ledger_entry(asdict(entry))
        return entry

    def inject_discount(self, member_id: str, amount: float, reason: str):
        return self.record_entry(member_id, "discount", amount, reason, {"injected_by": "second_brain"})

    def get_audit_trail(self, member_id: Optional[str] = None):
        if member_id:
            return [asdict(e) for e in self.chain if e.member_id == member_id]
        return [asdict(e) for e in self.chain]
