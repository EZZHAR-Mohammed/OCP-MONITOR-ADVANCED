from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class NormalizedData:
    source: str               # opcua, mqtt, rest (future)
    node_id: str
    name: str
    category: str             # system, sensor, machine, unknown
    value: Any
    unit: Optional[str]
    timestamp: int            # UNIX timestamp


@dataclass
class SensorData:
    name: str
    value: Any
    timestamp: float

    def to_dict(self):
        return {"name": self.name, "value": self.value, "timestamp": self.timestamp}
