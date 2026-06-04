# path: src/calendar/events.py

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional

@dataclass
class ClassEvent:
    id: str
    title: str
    instructor: str
    start_time: datetime
    duration_minutes: int
    capacity: int
    current_bookings: int = 0
    tier_required: Optional[str] = None  # e.g. "monthly", "drop-in"

class EventsCalendar:
    """
    Climbing gym calendar + events system.
    Supports daily yoga, crossfit, climbing classes, marketing campaigns, camps.
    """

    def __init__(self, data_store):
        self.data_store = data_store
        self.events: List[ClassEvent] = []

    def create_class(self, title: str, instructor: str, start_time: datetime, duration: int, capacity: int, tier: Optional[str] = None):
        event = ClassEvent(
            id=f"EVT{int(datetime.now().timestamp())}",
            title=title,
            instructor=instructor,
            start_time=start_time,
            duration_minutes=duration,
            capacity=capacity,
            tier_required=tier
        )
        self.events.append(event)
        self.data_store.save_event(event)
        return event

    def get_daily_schedule(self, date: datetime) -> List[dict]:
        day_events = [e for e in self.events if e.start_time.date() == date.date()]
        return [
            {
                "title": e.title,
                "instructor": e.instructor,
                "time": e.start_time.strftime("%H:%M"),
                "duration": f"{e.duration_minutes} min",
                "spots_left": e.capacity - e.current_bookings,
                "tier": e.tier_required or "any"
            }
            for e in day_events
        ]

    def book_class(self, event_id: str, member_id: str):
        for e in self.events:
            if e.id == event_id and e.current_bookings < e.capacity:
                e.current_bookings += 1
                self.data_store.book_event(event_id, member_id)
                return {"success": True, "spots_left": e.capacity - e.current_bookings}
        return {"success": False, "reason": "Class full or not found"}
