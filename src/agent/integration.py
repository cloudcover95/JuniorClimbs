# path: src/agent/integration.py

from typing import Dict, Any

class JuniorClimbsAgentInterface:
    """
    Clean interface so JuniorAGI / on-suite agents can interact with the gym system.
    Agents can check safety, book classes, manage member accounts, apply offers, etc.
    """

    def __init__(self, pos, events, safety, ledger, data_store):
        self.pos = pos
        self.events = events
        self.safety = safety
        self.ledger = ledger
        self.data_store = data_store

    def get_member_status(self, member_id: str) -> dict:
        return self.data_store.get_member(member_id)

    def check_safety_at_location(self, location: Dict) -> List[str]:
        return self.safety.check_point_safety(location)

    def book_class_for_member(self, member_id: str, event_id: str):
        return self.events.book_class(event_id, member_id)

    def apply_discount(self, member_id: str, percent: float, reason: str):
        return self.ledger.inject_discount(member_id, percent, reason)

    def get_daily_schedule(self, date):
        return self.events.get_daily_schedule(date)
