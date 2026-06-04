# path: src/admin/marketing.py

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Campaign:
    id: str
    name: str
    start_date: datetime
    end_date: datetime
    target_tiers: List[str]
    discount_percent: float
    channels: List[str]  # email, sms, in-app, social

class MarketingCampaigns:
    """
    Admin tools for communication, marketing deployment, and campaign scheduling.
    """

    def __init__(self, data_store, ledger):
        self.data_store = data_store
        self.ledger = ledger

    def create_campaign(self, name: str, start: datetime, end: datetime, tiers: List[str], discount: float, channels: List[str]):
        campaign = Campaign(
            id=f"CAMP{int(datetime.now().timestamp())}",
            name=name,
            start_date=start,
            end_date=end,
            target_tiers=tiers,
            discount_percent=discount,
            channels=channels
        )
        self.data_store.save_campaign(campaign)
        # Second brain can auto-inject matching discounts into ledger
        return campaign

    def schedule_class_series(self, title: str, instructor: str, start_date: datetime, weeks: int, days: List[int], time: str):
        """Create recurring classes (e.g. daily yoga or crossfit)."""
        created = []
        for week in range(weeks):
            for day in days:
                event_date = start_date + timedelta(weeks=week, days=day)
                # Would call EventsCalendar.create_class(...)
                created.append({"title": title, "date": event_date})
        return created
