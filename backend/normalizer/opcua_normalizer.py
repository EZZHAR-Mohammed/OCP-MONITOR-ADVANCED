import time
from typing import Any, Dict
from models.data_model import NormalizedData

# Simple mapping table - extendable for project-specific NodeIds
NODE_MAPPING: Dict[str, Dict[str, Any]] = {
    "i=2257": {"name": "StartTime", "category": "system", "unit": None},
    "i=2258": {"name": "CurrentTime", "category": "system", "unit": None},
    "i=2259": {"name": "ServerState", "category": "system", "unit": None},
}


def _format_value(raw_value: Any) -> Any:
    # Datetime -> ISO string
    if hasattr(raw_value, "isoformat"):
        try:
            return raw_value.isoformat()
        except Exception:
            pass

    # If bytes, decode if possible
    if isinstance(raw_value, (bytes, bytearray)):
        try:
            return raw_value.decode("utf-8")
        except Exception:
            return raw_value

    return raw_value


def normalize_opcua_data(node_id: str, raw_value: Any, raw_name: str = None) -> NormalizedData:
    mapping = NODE_MAPPING.get(node_id, None)

    if mapping is None:
        # fallback: try to infer category from name or node id
        if raw_name and any(x in raw_name.lower() for x in ("time", "server", "status")):
            category = "system"
        else:
            category = "sensor"

        name = raw_name if raw_name else node_id
        unit = None
    else:
        name = mapping.get("name")
        category = mapping.get("category", "unknown")
        unit = mapping.get("unit")

    value = _format_value(raw_value)

    return NormalizedData(
        source="opcua",
        node_id=node_id,
        name=name,
        category=category,
        value=value,
        unit=unit,
        timestamp=int(time.time()),
    )
