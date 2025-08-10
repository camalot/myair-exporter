import inspect
import os
import traceback

from libs.enums import loglevel
from libs.mongodb.Database import Database


class MyAirLogsDatabase(Database):
    def __init__(self) -> None:
        super().__init__()
        # get the file name without the extension and without the directory
        self._module = os.path.basename(__file__)[:-3]
        self._class = self.__class__.__name__
        self.collection_name = "myair_logs"
        pass

    def get_logs(self) -> list:
        """Get all logs."""
        _method = inspect.stack()[0][3]
        try:
            if self.connection is None or self.client is None:
                self.open()
            return list(self.connection.logs.find({}))  # type: ignore
        except Exception as ex:
            self.log(
                level=loglevel.LogLevel.ERROR,
                method=f"{self._module}.{self._class}.{_method}",
                message=f"{ex}",
                stackTrace=traceback.format_exc(),
            )
            return []
