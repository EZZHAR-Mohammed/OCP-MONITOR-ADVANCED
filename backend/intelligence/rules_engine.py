import time
from typing import List
from models.alert_model import Alert

# Seuils configurables (extension possible via JSON / UI)
THRESHOLDS = {
    "Temperature": {"warning": 60.0, "critical": 80.0},
    "Pressure": {"warning": 8.0, "critical": 10.0},
}


def evaluate_rules(normalized_data) -> List[Alert]:
    """Evaluate threshold rules on a NormalizedData object and return a list of Alert(s).

    Returns an empty list when the value is OK or not numeric / not configured.
    """
    alerts: List[Alert] = []

    name = normalized_data.name
    raw_value = normalized_data.value

    # Ensure numeric comparison
    try:
        value = float(raw_value)
    except Exception:
        return alerts

    if name not in THRESHOLDS:
        return alerts

    thresholds = THRESHOLDS[name]

    if value >= thresholds.get("critical", float("inf")):
        severity = "CRITICAL"
        threshold = thresholds.get("critical")
    elif value >= thresholds.get("warning", float("inf")):
        severity = "WARNING"
        threshold = thresholds.get("warning")
    else:
        return alerts

    alerts.append(
        Alert(
            name=name,
            node_id=normalized_data.node_id,
            severity=severity,
            message=f"{name} dépasse le seuil {severity}",
            value=value,
            threshold=threshold,
            timestamp=int(time.time()),
        )
    )

    return alerts
