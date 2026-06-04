# path: src/operations/maintenance.py

import csv
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Optional
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

@dataclass
class MaintenanceLog:
    timestamp: float
    equipment_id: str
    action: str
    performed_by: str
    notes: str
    due_date: Optional[str] = None
    status: str = "open"  # open, in_progress, completed

class MaintenanceSystem:
    """
    Portable CSV/Excel forward/backwards compatible system for maintenance logs,
    schedules, reports, and actionables.
    Works with or without pandas for maximum compatibility.
    """

    def __init__(self, data_store):
        self.data_store = data_store
        self.logs: List[MaintenanceLog] = []

    def add_log(self, equipment_id: str, action: str, performed_by: str, notes: str,
                due_date: Optional[str] = None, status: str = "open") -> MaintenanceLog:
        log = MaintenanceLog(
            timestamp=time.time(),
            equipment_id=equipment_id,
            action=action,
            performed_by=performed_by,
            notes=notes,
            due_date=due_date,
            status=status
        )
        self.logs.append(log)
        self.data_store.append_maintenance_log(asdict(log))
        return log

    def export_to_csv(self, filepath: str):
        if not self.logs:
            return False
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=asdict(self.logs[0]).keys())
            writer.writeheader()
            for log in self.logs:
                writer.writerow(asdict(log))
        return True

    def import_from_csv(self, filepath: str):
        imported = []
        with open(filepath, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                log = MaintenanceLog(**{k: v for k, v in row.items() if k in MaintenanceLog.__annotations__})
                self.logs.append(log)
                imported.append(log)
        return imported

    def export_to_excel(self, filepath: str):
        if not HAS_PANDAS or not self.logs:
            return False
        df = pd.DataFrame([asdict(log) for log in self.logs])
        df.to_excel(filepath, index=False)
        return True

    def import_from_excel(self, filepath: str):
        if not HAS_PANDAS:
            return []
        df = pd.read_excel(filepath)
        imported = []
        for _, row in df.iterrows():
            log = MaintenanceLog(**{k: v for k, v in row.items() if k in MaintenanceLog.__annotations__})
            self.logs.append(log)
            imported.append(log)
        return imported

    def get_overdue(self) -> List[MaintenanceLog]:
        now = time.time()
        return [log for log in self.logs if log.due_date and log.status != "completed"]
