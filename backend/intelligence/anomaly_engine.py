def detect_anomaly(current_value, stats) -> bool:
    """Simple anomaly detection based on relative deviation from rolling average.

    Returns True when deviation > 30%.
    """
    if not stats:
        return False

    try:
        cur = float(current_value)
    except Exception:
        return False

    avg = stats.get("avg")
    if not avg:
        return False

    deviation = abs(cur - avg) / avg
    return deviation > 0.3
