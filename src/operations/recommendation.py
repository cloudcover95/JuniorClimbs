# path: src/operations/recommendation.py

class MaintenanceRecommender:
    """
    Example recommendation layer.
    Public OSS version includes basic priority scoring and event awareness.
    In-house systems can upgrade to BitNet 3.0 / manifold-powered predictive models.
    """

    def __init__(self, maintenance_system, events_calendar):
        self.maintenance = maintenance_system
        self.events = events_calendar

    def suggest_next_actions(self, date=None):
        overdue = self.maintenance.get_overdue()
        suggestions = []
        for log in overdue:
            priority = "high" if log.due_date else "medium"
            conflict = False
            if self.events:
                daily = self.events.get_daily_schedule(date) if date else []
                busy_slots = [e for e in daily if e.get("title", "").lower() in ["yoga", "crossfit", "class"]]
                if busy_slots and log.action.lower() in ["replace", "heavy repair", "inspection"]:
                    conflict = True
                    priority = "medium"  # deprioritize during peak times

            suggestions.append({
                "equipment_id": log.equipment_id,
                "action": log.action,
                "priority": priority,
                "avoid_peak_classes": conflict,
                "suggested_by": "rule_based"
            })
        return suggestions

class FinanceRecommender:
    def __init__(self, ledger):
        self.ledger = ledger

    def suggest_offers(self, member_id: str):
        return [{"type": "discount", "percent": 10, "reason": "example", "suggested_by": "rule_based"}]
