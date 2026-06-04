# path: src/operations/recommendation.py

class MaintenanceRecommender:
    """
    Example recommendation layer.
    In public OSS this is rule-based.
    In-house systems can replace with BitNet 3.0 / manifold-powered models
    for predictive maintenance scheduling while keeping the same interface.
    """

    def __init__(self, maintenance_system):
        self.maintenance = maintenance_system

    def suggest_next_actions(self):
        overdue = self.maintenance.get_overdue()
        return [
            {
                "equipment_id": log.equipment_id,
                "action": log.action,
                "priority": "high" if log.due_date else "medium",
                "suggested_by": "rule_based"
            }
            for log in overdue
        ]

class FinanceRecommender:
    """
    Example offer timing layer.
    Public OSS version is simple.
    In-house can use LowRankAdapter + manifold member behavior models
    for personalized discount timing.
    """

    def __init__(self, ledger):
        self.ledger = ledger

    def suggest_offers(self, member_id: str):
        return [{"type": "discount", "percent": 10, "reason": "example", "suggested_by": "rule_based"}]
