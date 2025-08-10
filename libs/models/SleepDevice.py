import typing
from dataclasses import asdict, dataclass, field

import libs.utils as utils


@dataclass
class SleepDevice:
    serialNumber: str
    deviceType: str
    lastSleepDataReportTime: str
    localizedName: str
    imagePath: str
    fgDeviceManufacturerName: str
    fgDevicePatientId: str
    typename: str = field(default="SleepDevice", init=False)

    def to_dict(self):
        """Convert the dataclass to a dictionary for MongoDB insertion."""
        return asdict(self)

    @staticmethod
    def from_map(data: typing.Mapping[str, typing.Any]) -> 'SleepDevice':
        """Create a SleepDevice instance from a mapping."""
        return SleepDevice.from_dict(utils.map_to_dict(data))

    @staticmethod
    def from_dict(data: dict) -> 'SleepDevice':
        """Create a SleepDevice instance from a dictionary."""
        image_path = data.get("imagePath", "")
        if image_path and not image_path.startswith("https://"):
            image_path = f'https://static.myair-prd.dht.live/{image_path}'
        data["imagePath"] = image_path
        return SleepDevice(
            serialNumber=data.get("serialNumber", ""),
            deviceType=data.get("deviceType", ""),
            lastSleepDataReportTime=data.get("lastSleepDataReportTime", ""),
            localizedName=data.get("localizedName", ""),
            imagePath=data.get("imagePath", ""),
            fgDeviceManufacturerName=data.get("fgDeviceManufacturerName", ""),
            fgDevicePatientId=data.get("fgDevicePatientId", ""),
        )
