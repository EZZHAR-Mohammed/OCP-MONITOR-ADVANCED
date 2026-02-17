import math
from collections import deque
from typing import Dict, Any

WINDOW_SIZE = 10  # sliding window size


class StatsEngine:
    def __init__(self):
        self.buffers: Dict[str, deque] = {}

    def update(self, data) -> Dict[str, Any]:
        """Update stats with a NormalizedData instance and return stats dict.

        Returns None if value is non-numeric.
        """
        key = data.name
        value = data.value

        # try cast to float
        try:
            val = float(value)
        except Exception:
            return None

        if key not in self.buffers:
            self.buffers[key] = deque(maxlen=WINDOW_SIZE)

        self.buffers[key].append(val)
        values = list(self.buffers[key])

        if len(values) == 0:
            return None

        avg = sum(values) / len(values)
        return {"avg": avg, "min": min(values), "max": max(values), "count": len(values)}
