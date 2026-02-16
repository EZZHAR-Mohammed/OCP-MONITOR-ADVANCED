class SensorData:
    def __init__(self, name, value, timestamp):
        self.name = name
        self.value = value
        self.timestamp = timestamp

    def to_dict(self):
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp,
        }
