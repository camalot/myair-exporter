import inspect
import os
import traceback

from libs.enums import loglevel
from libs.models.Patient import Patient
from libs.mongodb.Database import Database


class MyAirPatientsDatabase(Database):
    def __init__(self) -> None:
        super().__init__()
        # get the file name without the extension and without the directory
        self._module = os.path.basename(__file__)[:-3]
        self._class = self.__class__.__name__
        self.collection_name = "myair_patients"
        pass

    def list(self) -> list:
        """List all patients."""
        _method = inspect.stack()[0][3]
        try:
            if self.connection is None or self.client is None:
                self.open()

            patients = list(self.connection[self.collection_name].find({}))  # type: ignore
            return [Patient.from_dict(patient) for patient in patients]
        except Exception as ex:
            self.log(
                level=loglevel.LogLevel.ERROR,
                method=f"{self._module}.{self._class}.{_method}",
                message=f"{ex}",
                stackTrace=traceback.format_exc(),
            )
            return []

    def insert(self, patient: Patient) -> bool:
        _method = inspect.stack()[0][3]
        try:
            if self.connection is None or self.client is None:
                self.open()
            # only insert if the patient does not already exist
            existing_patient = self.connection[self.collection_name].find_one({"id": patient.id})  # type: ignore
            if existing_patient:
                self.log(
                    level=loglevel.LogLevel.INFO,
                    method=f"{self._module}.{self._class}.{_method}",
                    message=f"Patient {patient.id} already exists, skipping insert.",
                )
                return False
            self.connection[self.collection_name].insert_one(patient.to_dict())  # type: ignore
            return True
        except Exception as ex:
            self.log(
                level=loglevel.LogLevel.ERROR,
                method=f"{self._module}.{self._class}.{_method}",
                message=f"{ex}",
                stackTrace=traceback.format_exc(),
            )
            return False
