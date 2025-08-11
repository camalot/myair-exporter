import inspect
import os
import traceback
import typing

from libs.enums import loglevel
from libs.models.SleepRecord import SleepRecord
from libs.mongodb.Database import Database


class MyAirSleepRecordsDatabase(Database):
    def __init__(self) -> None:
        super().__init__()
        # get the file name without the extension and without the directory
        self._module = os.path.basename(__file__)[:-3]
        self._class = self.__class__.__name__
        self.collection_name = "myair_sleep_records"
        pass

    def getLastReportDate(self, patientId: str) -> str | None:
        """Get the last report date for a patient."""
        _method = inspect.stack()[0][3]
        try:
            if self.connection is None or self.client is None:
                self.open()
            if self.collection_name not in self.connection.list_collection_names():  # type: ignore
                return None

            record = self.connection[self.collection_name].find_one(  # type: ignore
                {"sleepRecordPatientId": patientId}
            )  # type: ignore
            if record:
                return SleepRecord.from_dict(record).startDate
            return None
        except Exception as ex:
            self.log(
                level=loglevel.LogLevel.ERROR,
                method=f"{self._module}.{self._class}.{_method}",
                message=f"{ex}",
                stackTrace=traceback.format_exc(),
            )
            return None

    def list(self) -> list[SleepRecord]:
        """Get all sleep records."""
        _method = inspect.stack()[0][3]
        try:
            if self.connection is None or self.client is None:
                self.open()
            if self.collection_name not in self.connection.list_collection_names():  # type: ignore
                return []
            # get the sleep records from the collection and return them as a list of models.SleepRecord
            records = self.connection[self.collection_name].find({})  # type: ignore
            return [SleepRecord.from_dict(record) for record in records]
        except Exception as ex:
            self.log(
                level=loglevel.LogLevel.ERROR,
                method=f"{self._module}.{self._class}.{_method}",
                message=f"{ex}",
                stackTrace=traceback.format_exc(),
            )
            return []

    def get(self, startDate: str, patientId: str) -> SleepRecord | None:
        """Get a sleep record by its ID."""
        _method = inspect.stack()[0][3]
        try:
            if self.connection is None or self.client is None:
                self.open()
            if self.connection is None or self.client is None:
                raise ValueError("Database connection is not open")

            record = self.connection[self.collection_name].find_one(
                {"startDate": startDate, "sleepRecordPatientId": patientId}
            )  # type: ignore
            if record:
                return SleepRecord.from_dict(record)
            return None
        except Exception as ex:
            self.log(
                level=loglevel.LogLevel.ERROR,
                method=f"{self._module}.{self._class}.{_method}",
                message=f"{ex}",
                stackTrace=traceback.format_exc(),
            )
            return None

    def insert_many(self, records: typing.List[SleepRecord]) -> None:
        """Insert multiple sleep records into the database."""
        _method = inspect.stack()[0][3]
        try:
            if self.connection is None or self.client is None:
                self.open()
            if self.connection is None or self.client is None:
                raise ValueError("Database connection is not open")

            # payloads = [record.to_dict() for record in records]
            if records:
                for record in records:
                    self.insert(record)
        except Exception as ex:
            self.log(
                level=loglevel.LogLevel.ERROR,
                method=f"{self._module}.{self._class}.{_method}",
                message=f"{ex}",
                stackTrace=traceback.format_exc(),
            )

    def insert(self, record: SleepRecord) -> None:
        """Insert a single sleep record into the database."""
        _method = inspect.stack()[0][3]
        try:
            if self.connection is None or self.client is None:
                self.open()
            if self.connection is None or self.client is None:
                raise ValueError("Database connection is not open")

            # do not update the maskCode if it is already set
            existing_record = self.connection[self.collection_name].find_one(
                {"startDate": record.startDate, "sleepRecordPatientId": record.sleepRecordPatientId}
            )  # type: ignore

            if existing_record:
                if existing_record.get("maskCode") is not None:
                    # if the maskCode is already set, do not update it
                    record.maskCode = existing_record["maskCode"]

            self.connection[self.collection_name].update_one(
                {"startDate": record.startDate, "sleepRecordPatientId": record.sleepRecordPatientId},
                {"$set": record.to_dict()},
                upsert=True,
            )
        except Exception as ex:
            self.log(
                level=loglevel.LogLevel.ERROR,
                method=f"{self._module}.{self._class}.{_method}",
                message=f"{ex}",
                stackTrace=traceback.format_exc(),
            )
