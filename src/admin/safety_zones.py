# path: src/admin/safety_zones.py

from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class SafetyZone:
    id: str
    name: str
    zone_type: str  # 'off_limits', 'top_out', 'slab', 'trad', 'overhang'
    coordinates: List[Dict]  # polygon or bounding box from optical/room mapping
    restrictions: List[str]
    active: bool = True

class SafetyZoneManager:
    """
    Admin can mark safety zones on whole-room optical dash.
    Agents and staff see real-time restrictions.
    """

    def __init__(self, data_store):
        self.data_store = data_store
        self.zones: List[SafetyZone] = []

    def create_zone(self, name: str, zone_type: str, coordinates: List[Dict], restrictions: List[str]):
        zone = SafetyZone(
            id=f"ZONE{int(__import__('time').time())}",
            name=name,
            zone_type=zone_type,
            coordinates=coordinates,
            restrictions=restrictions
        )
        self.zones.append(zone)
        self.data_store.save_safety_zone(zone)
        return zone

    def get_active_zones(self) -> List[dict]:
        return [
            {
                "name": z.name,
                "type": z.zone_type,
                "restrictions": z.restrictions
            }
            for z in self.zones if z.active
        ]

    def check_point_safety(self, point: Dict) -> List[str]:
        violations = []
        for zone in self.zones:
            if zone.active and self._point_in_zone(point, zone.coordinates):
                violations.extend(zone.restrictions)
        return violations
