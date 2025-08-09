# user_device_data: {
#   "serialNumber": "23191427249",
#   "deviceType": "AS10",
#   "lastSleepDataReportTime": "2025-08-07T13:26:36.000+00:00",
#   "localizedName": "AirSense 10 Respond",
#   "imagePath": "v1/flowgens/airsense_10_autoset/airsense_10_autoset.png",
#   "fgDeviceManufacturerName": "Resmed",
#   "fgDevicePatientId": "00uylx14a9T8huxmW297",
#   "__typename": "FgDevice"
# }
from dataclasses import dataclass, asdict, field
from typing import Optional
import libs.utils as utils
import typing


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
