# mask_info: {
#   "maskManufacturerName": "Resmed",
#   "maskCode": "mirage-quattro-full-face",
#   "maskType": "Full face",
#   "localizedName": "Mirage Quattro",
#   "imagePath": "/v1/masks/mirage_quattro/mirage_quattro_full_face_mask_plus_headgear.jpg",
#   "maskPatientId": "00uylx14a9T8huxmW297",
#   "__typename": "Mask"
# }

from dataclasses import dataclass, asdict, field
import datetime
from typing import Optional
import typing

from libs import utils


@dataclass
class Mask:
    maskManufacturerName: str
    maskCode: str
    maskType: str
    localizedName: str
    imagePath: str
    maskPatientId: str
    typename: str = field(default="Mask", init=False)

    def to_dict(self):
        """Convert the dataclass to a dictionary for MongoDB insertion."""
        return asdict(self)

    @staticmethod
    def from_map(data: typing.Mapping[str, typing.Any]) -> 'Mask':
        """Create a Mask instance from a mapping."""
        return Mask.from_dict(utils.map_to_dict(data))

    @staticmethod
    def from_dict(data: dict) -> 'Mask':
        """Create a Mask instance from a dictionary."""
        image_path = data.get("imagePath", "")
        if image_path and not image_path.startswith("https://"):
            image_path = f'https://static.myair-prd.dht.live/{image_path}'
        data["imagePath"] = image_path
        return Mask(
            maskManufacturerName=data.get("maskManufacturerName", ""),
            maskCode=data.get("maskCode", ""),
            maskType=data.get("maskType", ""),
            localizedName=data.get("localizedName", ""),
            imagePath=data.get("imagePath", ""),
            maskPatientId=data.get("maskPatientId", ""),
        )
