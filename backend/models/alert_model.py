from dataclasses import dataclass
from typing import Optional


@dataclass
class Alert:
    name: str
    node_id: str
    severity: str      # INFO / WARNING / CRITICAL
    message: str
    value: float
    threshold: Optional[float]
    timestamp: int
