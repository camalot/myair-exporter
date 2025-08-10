import inspect
import os
import traceback
import typing

from libs.enums import loglevel
from libs.models.Mask import Mask
from libs.mongodb.Database import Database


class MyAirMasksDatabase(Database):
    def __init__(self) -> None:
        super().__init__()
        # get the file name without the extension and without the directory
        self._module = os.path.basename(__file__)[:-3]
        self._class = self.__class__.__name__
        self.collection_name = "myair_masks"
        pass

    def get(self, patientId: str, maskCode: str) -> typing.Optional[Mask]:
        """Get a mask by patientId and maskCode."""
        _method = inspect.stack()[0][3]
        try:
            if self.connection is None or self.client is None:
                self.open()
            mask_data = self.connection[self.collection_name].find_one({"patientId": patientId, "maskCode": maskCode})  # type: ignore
            if mask_data:
                return Mask.from_dict(mask_data)
            return None
        except Exception as ex:
            self.log(
                level=loglevel.LogLevel.ERROR,
                method=f"{self._module}.{self._class}.{_method}",
                message=f"{ex}",
                stackTrace=traceback.format_exc(),
            )
            return None

    def list(self) -> typing.List[Mask]:
        """List all masks."""
        _method = inspect.stack()[0][3]
        try:
            if self.connection is None or self.client is None:
                self.open()
            masks = list(self.connection[self.collection_name].find({}))  # type: ignore
            return [Mask.from_dict(mask) for mask in masks]
        except Exception as ex:
            self.log(
                level=loglevel.LogLevel.ERROR,
                method=f"{self._module}.{self._class}.{_method}",
                message=f"{ex}",
                stackTrace=traceback.format_exc(),
            )
            return []

    def list_by_patient(self, patientId: str) -> typing.List[Mask]:
        """Get all masks for a specific patient."""
        _method = inspect.stack()[0][3]
        try:
            if self.connection is None or self.client is None:
                self.open()
            masks = list(self.connection[self.collection_name].find({"maskPatientId": patientId}))  # type: ignore
            return [Mask.from_dict(mask) for mask in masks]
        except Exception as ex:
            self.log(
                level=loglevel.LogLevel.ERROR,
                method=f"{self._module}.{self._class}.{_method}",
                message=f"{ex}",
                stackTrace=traceback.format_exc(),
            )
            return []

    def insert(self, mask: Mask) -> bool:
        """Insert a new mask."""
        _method = inspect.stack()[0][3]
        try:
            if self.connection is None or self.client is None:
                self.open()

            # do not insert if the mask already exists
            existing_mask = self.connection[self.collection_name].find_one({"maskCode": mask.maskCode, "maskPatientId": mask.maskPatientId})  # type: ignore
            if existing_mask:
                print(f"Mask {mask.maskCode} for patient {mask.maskPatientId} already exists, skipping insert.")
                return False

            self.connection[self.collection_name].insert_one(mask.to_dict())  # type: ignore
            return True
        except Exception as ex:
            self.log(
                level=loglevel.LogLevel.ERROR,
                method=f"{self._module}.{self._class}.{_method}",
                message=f"{ex}",
                stackTrace=traceback.format_exc(),
            )
            return False
