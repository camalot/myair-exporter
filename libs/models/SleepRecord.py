# {
#     "startDate": "2025-08-01",
#     "totalUsage": 0,
#     "sleepScore": 0,
#     "usageScore": 0,
#     "ahiScore": 0,
#     "maskScore": 0,
#     "leakScore": 0,
#     "ahi": 0.0,
#     "maskPairCount": 0,
#     "leakPercentile": 0.0,
#     "sleepRecordPatientId": "00uylx14a9T8huxmW297",
#     "__typename": "SleepRecord"
#   }

from dataclasses import dataclass, asdict, field
from typing import Optional
import typing

from libs import utils


@dataclass
class SleepRecord:
    startDate: str
    totalUsage: int
    sleepScore: int
    usageScore: int
    ahiScore: int
    maskScore: int
    leakScore: int
    ahi: float
    maskPairCount: int
    leakPercentile: float
    sleepRecordPatientId: str
    maskCode: Optional[str] = None
    typename: str = field(default="SleepRecord", init=False)

    def to_dict(self):
        """Convert the dataclass to a dictionary for MongoDB insertion."""
        return asdict(self)

    @staticmethod
    def from_map(data: typing.Mapping[str, typing.Any]) -> 'SleepRecord':
        """Create a SleepRecord instance from a mapping."""
        return SleepRecord.from_dict(utils.map_to_dict(data))

    @staticmethod
    def from_dict(data: dict):
        """Create a SleepRecord instance from a dictionary."""
        return SleepRecord(
            startDate=data.get("startDate", ""),
            totalUsage=data.get("totalUsage", 0),
            sleepScore=data.get("sleepScore", 0),
            usageScore=data.get("usageScore", 0),
            ahiScore=data.get("ahiScore", 0),
            maskScore=data.get("maskScore", 0),
            leakScore=data.get("leakScore", 0),
            ahi=data.get("ahi", 0.0),
            maskPairCount=data.get("maskPairCount", 0),
            leakPercentile=data.get("leakPercentile", 0.0),
            sleepRecordPatientId=data.get("sleepRecordPatientId", ""),
            maskCode=data.get("maskCode", None),
        )
