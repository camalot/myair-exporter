import inspect
import os
import sys
import traceback
import typing

from libs import settings, utils
from libs.colors import Colors
from libs.enums import loglevel
from libs.mongodb.MongoClientSingleton import MongoClientSingleton


class BaseDatabase:
    def __init__(self) -> None:
        # get the file name without the extension and without the directory
        self._module = os.path.basename(__file__)[:-3]
        self._class = self.__class__.__name__
        self.settings = settings.Settings()
        self.client = None
        self.connection = None
        self.database_name = self.settings.db_name
        self.db_url = self.settings.db_url

    def open(self) -> None:
        if not self.db_url:
            raise ValueError("MONGODB_URL is not set")
        if self.client is not None and self.connection is not None:
            return
        self.client = MongoClientSingleton.get_client(self.db_url)
        self.connection = self.client[self.database_name]

    def close(self) -> None:
        _method = inspect.stack()[0][3]
        try:
            if self.client:
                self.client.close()
            self.client = None
            self.connection = None
        except Exception as ex:
            self.log(
                level=loglevel.LogLevel.ERROR,
                method=f"{self._module}.{self._class}.{_method}",
                message=f"Failed to close connection: {ex}",
                stackTrace=traceback.format_exc(),
            )

    def log(
        self,
        level: loglevel.LogLevel,
        method: str,
        message: str,
        stackTrace: typing.Optional[str] = None,
        outIO: typing.Optional[typing.IO] = None,
        colorOverride: typing.Optional[str] = None,
    ) -> None:
        _method = inspect.stack()[0][3]
        if colorOverride is None:
            color = Colors.get_color(level)
        else:
            color = colorOverride

        m_level = Colors.colorize(color, f"[{level.name}]", bold=True)
        m_method = Colors.colorize(Colors.HEADER, f"[{method}]", bold=True)
        m_message = f"{Colors.colorize(color, message)}"

        str_out = f"{m_level} {m_method} {m_message}"
        if outIO is None:
            stdoe = sys.stdout if level < loglevel.LogLevel.ERROR else sys.stderr
        else:
            stdoe = outIO

        print(str_out, file=stdoe)
        if stackTrace:
            print(Colors.colorize(color, stackTrace), file=stdoe)
        try:
            if level >= loglevel.LogLevel.INFO:
                self.insert_log(level=level, method=method, message=message, stack=stackTrace)
        except Exception as ex:
            self.log(
                level=loglevel.LogLevel.PRINT,
                method=f"{self._module}.{self._class}.{_method}",
                message=f"Unable to log to database: {ex}",
                stackTrace=traceback.format_exc(),
                outIO=sys.stderr,
                colorOverride=Colors.FAIL,
            )

    def insert_log(
        self, level: loglevel.LogLevel, method: str, message: str, stack: typing.Optional[str] = None
    ) -> None:
        _method = inspect.stack()[0][3]
        try:
            if self.connection is None or self.client is None:
                self.open()
            payload = {
                "timestamp": utils.get_timestamp(),
                "level": level.name,
                "method": method,
                "message": message,
                "stack_trace": stack if stack else "",
            }
            self.connection.logs.insert_one(payload)  # type: ignore
        except Exception as ex:
            self.log(
                level=loglevel.LogLevel.PRINT,
                method=f"{self._module}.{self._class}.{_method}",
                message=f"Failed to insert log: {ex}",
                stackTrace=traceback.format_exc(),
                outIO=sys.stderr,
                colorOverride=Colors.FAIL,
            )
