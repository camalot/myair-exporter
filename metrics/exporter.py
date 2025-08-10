import inspect
import os
import traceback

from libs.enums.loglevel import LogLevel
from libs.logger import Log
from libs.settings import Settings
from metrics.config import MyAirMetricsConfig
from metrics.myair import MyAirMetrics
from prometheus_client import start_http_server


class MetricsExporter:
    def __init__(self):
        _method = inspect.stack()[0][3]
        self._class = self.__class__.__name__
        self._module = os.path.basename(__file__)[:-3]
        self.settings = Settings()
        log_level = LogLevel[self.settings.log_level.upper()]
        if not log_level:
            log_level = LogLevel.DEBUG
        self.log = Log(log_level)

        self.log.debug(f"{self._module}.{self._class}.{_method}", "Exporter initialized")

    async def run(self):
        _method = inspect.stack()[1][3]
        try:
            config = MyAirMetricsConfig("metrics/config.yml")
            app_metrics = MyAirMetrics(config)
            start_http_server(config.metrics["port"])
            self.log.info(
                f"{self._module}.{self._class}.{_method}",
                f"Exporter Starting Listen => :{config.metrics['port']}/metrics",
            )
            await app_metrics.run_metrics_loop()
        except Exception as ex:
            self.log.error(f"{self._module}.{self._class}.{_method}", str(ex), traceback.format_exc())
