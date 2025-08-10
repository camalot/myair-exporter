import typing
from dataclasses import dataclass, asdict, field

from libs import utils


@dataclass
class Patient:
    id: str
    firstName: str
    lastName: str
    email: str
    dateOfBirth: str
    countryId: str
    timezoneId: str
    gender: str
    userEnteredAhi: float
    typename: str = field(default="Patient", init=False)

    def to_dict(self):
        """Convert the dataclass to a dictionary for MongoDB insertion."""
        return asdict(self)

    @staticmethod
    def from_map(data: typing.Mapping[str, typing.Any]) -> 'Patient':
        """Create a Patient instance from a mapping."""
        return Patient.from_dict(utils.map_to_dict(data))

    @staticmethod
    def from_dict(data: dict) -> 'Patient':
        """Create a Patient instance from a dictionary."""
        return Patient(
            id=data.get("id", ""),
            firstName=data.get("firstName", ""),
            lastName=data.get("lastName", ""),
            email=data.get("email", ""),
            dateOfBirth=data.get("dateOfBirth", ""),
            countryId=data.get("countryId", ""),
            timezoneId=data.get("timezoneId", ""),
            gender=data.get("gender", ""),
            userEnteredAhi=data.get("userEnteredAhi", 0.0),
        )
