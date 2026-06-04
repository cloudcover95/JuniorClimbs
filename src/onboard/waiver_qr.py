# path: src/onboard/waiver_qr.py

import time
from typing import Dict

class WaiverOnboard:
    def __init__(self, data_store):
        self.data_store = data_store

    def process_qr_scan(self, qr_payload: Dict) -> dict:
        """Member scans QR code on tablet/kiosk. Auto-onboard."""
        required = ["name", "email", "emergency_contact", "tier"]
        if not all(k in qr_payload for k in required):
            return {"status": "error", "message": "Incomplete waiver data"}

        member_id = f"M{int(time.time())}"
        keychain_id = f"KC{int(time.time())}"

        new_member = {
            "id": member_id,
            "name": qr_payload["name"],
            "email": qr_payload["email"],
            "emergency_contact": qr_payload["emergency_contact"],
            "tier": qr_payload["tier"],
            "keychain_id": keychain_id,
            "status": "active",
            "balance": 0.0,
            "joined_date": time.strftime("%Y-%m-%d"),
            "renewal_date": None
        }

        self.data_store.create_member(new_member)

        return {
            "status": "onboarded",
            "member_id": member_id,
            "keychain_id": keychain_id,
            "message": "Waiver signed and processed. Keychain activated. Welcome!"
        }
