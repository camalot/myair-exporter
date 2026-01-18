import datetime

class HealthStatus:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HealthStatus, cls).__new__(cls)
            cls._instance.healthy = False
            cls._instance.last_update = None
            cls._instance.last_error = None
        return cls._instance

    def set_healthy(self, healthy: bool):
        self.healthy = healthy
        self.last_update = datetime.datetime.now(datetime.timezone.utc)

    def set_error(self, error: str):
        self.healthy = False
        self.last_error = error
        self.last_update = datetime.datetime.now(datetime.timezone.utc)
