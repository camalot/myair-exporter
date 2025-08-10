import inspect
import os
import traceback
import typing

from libs.enums import loglevel
from libs.models.SleepDevice import SleepDevice
from libs.mongodb.Database import Database


class MyAirDevicesDatabase(Database):
    def __init__(self) -> None:
        super().__init__()
        # get the file name without the extension and without the directory
        self._module = os.path.basename(__file__)[:-3]
        self._class = self.__class__.__name__
        self.collection_name = "myair_devices"
        pass

    def get(self, patientId: str, serialNumber: str) -> typing.Optional[SleepDevice]:
        """Get a device by patientId and serialNumber."""
        _method = inspect.stack()[0][3]
        try:
            if self.connection is None or self.client is None:
                self.open()
            device_data = self.connection[self.collection_name].find_one({"fgDevicePatientId": patientId, "serialNumber": serialNumber})  # type: ignore
            if device_data:
                return SleepDevice.from_dict(device_data)
            return None
        except Exception as ex:
            self.log(
                level=loglevel.LogLevel.ERROR,
                method=f"{self._module}.{self._class}.{_method}",
                message=f"{ex}",
                stackTrace=traceback.format_exc(),
            )
            return None

    def list(self) -> typing.List[SleepDevice]:
        """List all devices."""
        _method = inspect.stack()[0][3]
        try:
            if self.connection is None or self.client is None:
                self.open()

            devices = list(self.connection[self.collection_name].find({}))  # type: ignore
            return [SleepDevice.from_dict(device) for device in devices]
        except Exception as ex:
            self.log(
                level=loglevel.LogLevel.ERROR,
                method=f"{self._module}.{self._class}.{_method}",
                message=f"{ex}",
                stackTrace=traceback.format_exc(),
            )
            return []

    def list_by_patient(self, patientId: str) -> typing.List[SleepDevice]:
        """Get all devices for a specific patient."""
        _method = inspect.stack()[0][3]
        try:
            if self.connection is None or self.client is None:
                self.open()
            return list(self.connection[self.collection_name].find({"fgDevicePatientId": patientId}))  # type: ignore
        except Exception as ex:
            self.log(
                level=loglevel.LogLevel.ERROR,
                method=f"{self._module}.{self._class}.{_method}",
                message=f"{ex}",
                stackTrace=traceback.format_exc(),
            )
            return []

    def insert(self, device: SleepDevice) -> bool:
        """Insert a device into the database."""
        _method = inspect.stack()[0][3]
        try:
            if self.connection is None or self.client is None:
                self.open()
            # only insert if the device does not already exist
            existing_device = self.connection[self.collection_name].find_one(  # type: ignore
                {"fgDevicePatientId": device.fgDevicePatientId, "serialNumber": device.serialNumber}
            )
            if existing_device:
                self.log(
                    level=loglevel.LogLevel.INFO,
                    method=f"{self._module}.{self._class}.{_method}",
                    message=f"Device {device.serialNumber} already exists, skipping insert.",
                )
                return False
            self.connection[self.collection_name].insert_one(device.to_dict())  # type: ignore
            return True
        except Exception as ex:
            self.log(
                level=loglevel.LogLevel.ERROR,
                method=f"{self._module}.{self._class}.{_method}",
                message=f"{ex}",
                stackTrace=traceback.format_exc(),
            )
            return False
