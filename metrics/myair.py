import asyncio
import datetime
import inspect
import math
import os
import traceback

import aiohttp
from libs import settings
from libs.enums.loglevel import LogLevel
from libs.logger import Log
from libs.models.Mask import Mask
from libs.models.Patient import Patient
from libs.models.SleepDevice import SleepDevice
from libs.models.SleepRecord import SleepRecord
from libs.mongodb.MyAirDevicesDatabase import MyAirDevicesDatabase
from libs.mongodb.MyAirMasksDatabase import MyAirMasksDatabase
from libs.mongodb.MyAirPatientsDatabase import MyAirPatientsDatabase
from libs.mongodb.MyAirSleepRecordsDatabase import MyAirSleepRecordsDatabase
from libs.resmed.client.myair_client import MyAirConfig
from libs.resmed.client.rest_client import RESTClient
from prometheus_client import Gauge


class MyAirMetrics:
    def __init__(self, config):
        _method = inspect.stack()[0][3]
        self._module = os.path.basename(__file__)[:-3]
        self._class = self.__class__.__name__

        self.namespace = "myair"
        self.polling_interval_seconds = config.metrics["pollingInterval"]
        self.config = config

        self.settings = settings.Settings()
        log_level = LogLevel[self.settings.log_level.upper()]
        if not log_level:
            log_level = LogLevel.DEBUG
        self.log = Log(minimumLogLevel=log_level)

        # self.logs_db = MyAirLogsDatabase()
        self.sleep_records_db = MyAirSleepRecordsDatabase()
        self.masks_db = MyAirMasksDatabase()
        self.patient_db = MyAirPatientsDatabase()
        self.device_db = MyAirDevicesDatabase()

        self.patient = Gauge(
            namespace=self.namespace,
            name="patient",
            documentation="A reference metric for the patient to be used in other metrics",
            labelnames=["id", "name", "ahi"],
        )

        self.device = Gauge(
            namespace=self.namespace,
            name="device",
            documentation="A reference metric for the device to be used in other metrics",
            labelnames=["serialNumber", "manufacturer", "type", "name", "image", "lastReportDate", "patient"],
        )

        self.mask = Gauge(
            namespace=self.namespace,
            name="mask",
            documentation="A reference metric for the mask to be used in other metrics",
            labelnames=["patient", "code", "name", "type", "image"],
        )

        self.score = Gauge(
            namespace=self.namespace,
            name="score",
            documentation="myAir calculates your score by analyzing your nightly therapy data. The higher your score, the better. You get points based on the following four key categories: usage, mask seal, events, and mask on/off. The maximum score you can get is 100 points.",
            labelnames=["patient", "device", "date", "mask"],
        )

        self.usage = Gauge(
            namespace=self.namespace,
            name="usage_seconds",
            documentation="The MyAir usage time in seconds",
            labelnames=["patient", "device", "date", "mask"],
        )

        self.usage_score = Gauge(
            namespace=self.namespace,
            name="usage_score",
            documentation="The point system for usage is calculated in hours and minutes. If you use your therapy for 1 hour you get 10 points, or for 2.3 hours (2 hours, 18 minutes) you get 23 points. The more time you use your therapy, the more points you receive, up to a maximum of 70 points.",
            labelnames=["patient", "device", "date", "mask"],
        )

        self.mask_seal = Gauge(
            namespace=self.namespace,
            name="mask_seal",
            documentation="The better your mask seal, the more points you get. This category can help you know if you need to adjust or change your mask to get a better fit. If your mask seal is poor, it can affect your comfort and the quality of your treatment. Your score reduces as your mask leak increases. You can get up to 20 points for minimal mask leak, 10 to 15 points for moderate leak, and 0 to 10 points for higher leak.",
            labelnames=["patient", "device", "date", "mask"],
        )

        self.mask_seal_score = Gauge(
            namespace=self.namespace,
            name="mask_seal_score",
            documentation="Your score reduces as your mask leak increases. You can get up to 20 points for minimal mask leak, 10 to 15 points for moderate leak, and 0 to 10 points for higher leak.",
            labelnames=["patient", "device", "date", "mask"],
        )

        self.mask_onoff_count = Gauge(
            namespace=self.namespace,
            name="mask_onoff_count",
            documentation="The MyAir mask on/off status. The fewer times you take your mask on and off throughout the night, the more points you get. Everyone has to take their mask on and off one time during treatment. So, for example, if you remove your mask one or two times, you get 5 points. However, if you take your mask on and off several times, it can indicate a problem with mask fit or with your sleep in general.",
            labelnames=["patient", "device", "date", "mask"],
        )

        self.mask_onoff_score = Gauge(
            namespace=self.namespace,
            name="mask_onoff_score",
            documentation="The MyAir mask on/off score. The fewer times you take your mask on and off throughout the night, the more points you get. 1-2: 5 points, 3: 4 points, 4: 3 points, 5: 2 points, 6 or more: 0 points.",
            labelnames=["patient", "device", "date", "mask"],
        )

        self.ahi = Gauge(
            namespace=self.namespace,
            name="ahi",
            documentation="Your CPAP machine notes the number of breathing events you have in each hour. This number can help measure how well your treatment is working. When you have an apnea, air stops flowing to your lungs for 10 seconds or longer -- that is, you actually stop breathing.",
            labelnames=["patient", "device", "date", "mask"],
        )

        self.ahi_score = Gauge(
            namespace=self.namespace,
            name="ahi_score",
            documentation="The fewer breathing events you have each hour, the more points you get. These breathing events are also known as the apnea-hypopnea index (or AHI). myAir measures how many times your breathing partially or fully stops each hour. If you have minimal events, you get 4 to 5 points.",
            labelnames=["patient", "device", "date", "mask"],
        )

        self.total_days_count = Gauge(
            namespace=self.namespace,
            name="total_days_count",
            documentation="Total number of days the user has been using any device.",
            labelnames=["patient", "device", "mask", "lastReportDate"],
        )

        self.total_usage_seconds = Gauge(
            namespace=self.namespace,
            name="total_usage_seconds",
            documentation="Total usage time of any device in seconds.",
            labelnames=["patient"],
        )

        self.log.debug(f"{self._module}.{self._class}.{_method}", "Metrics initialized")

    async def run_metrics_loop(self):
        """Metrics fetching loop"""
        _method = inspect.stack()[0][3]
        while True:
            try:
                self.log.debug(f"{self._module}.{self._class}.{_method}", "Begin metrics fetch")
                await self.fetch()
                self.log.debug(f"{self._module}.{self._class}.{_method}", "End metrics fetch")
                self.log.debug(
                    f"{self._module}.{self._class}.{_method}", f"Sleeping for {self.polling_interval_seconds} seconds"
                )
                await asyncio.sleep(self.polling_interval_seconds)
            except Exception as ex:
                self.log.error(f"{self._module}.{self._class}.{_method}", str(ex), traceback.format_exc())

    def _create_clientsession(self, **kwargs):
        return aiohttp.ClientSession(**kwargs)

    async def fetch(self):
        # _method = inspect.stack ()[0][3]
        for user in self.config.settings.myair['users']:
            client_config: MyAirConfig = MyAirConfig(
                username=user["username"],
                password=user["password"],
                region=user["region"],
                device_token=user["device_token"],
            )
            client: RESTClient = RESTClient(config=client_config, session=self._create_clientsession())

            await client.connect()

            user_device_data = SleepDevice.from_map(await client.get_user_device_data())
            record_days = self.config.settings.myair["records_days"] or 90
            months: int = math.ceil(record_days / 30)
            sleep_records = [SleepRecord.from_map(record) for record in await client.get_sleep_records(months=months)]
            user_info = Patient.from_map(await client.get_user_info())
            mask_info = Mask.from_map(await client.get_mask_info())

            # print(f"user_info: {json.dumps(user_info.to_dict(), indent=2)}")
            # print(f"user_device_data: {json.dumps(user_device_data.to_dict(), indent=2)}")
            # print(f"mask_info: {json.dumps(mask_info.to_dict(), indent=2)}")
            # print(f"sleep_records: {json.dumps([record.to_dict() for record in sleep_records], indent=2)}")

            await client.close()

            self.patient_db.insert(user_info)
            self.device_db.insert(user_device_data)
            self.masks_db.insert(mask_info)

            includeZero = self.config.settings.myair["include_zero_scores"]

            if sleep_records is not None and len(sleep_records) > 0:
                for record in sleep_records:
                    print(f"Processing record: {record.startDate} for patient: {record.sleepRecordPatientId}")

                    entry_mask = mask_info

                    existing_record = self.sleep_records_db.get(record.startDate, record.sleepRecordPatientId)
                    if existing_record and existing_record.maskCode is not None:
                        entry_mask = (
                            self.masks_db.get(record.sleepRecordPatientId, existing_record.maskCode) or mask_info
                        )

                    record.maskCode = entry_mask.maskCode

                    self.sleep_records_db.insert(record)

                    if not includeZero and record.sleepScore == 0:
                        continue

                    self.score.labels(
                        patient=record.sleepRecordPatientId,
                        device=user_device_data.serialNumber,
                        date=record.startDate,
                        mask=record.maskCode,
                    ).set(record.sleepScore)

                    self.usage.labels(
                        patient=record.sleepRecordPatientId,
                        device=user_device_data.serialNumber,
                        date=record.startDate,
                        mask=record.maskCode,
                    ).set(
                        record.totalUsage * 60
                    )  # totalUsage is in minutes, convert to seconds

                    self.usage_score.labels(
                        patient=record.sleepRecordPatientId,
                        device=user_device_data.serialNumber,
                        date=record.startDate,
                        mask=record.maskCode,
                    ).set(record.usageScore)

                    self.mask_seal.labels(
                        patient=record.sleepRecordPatientId,
                        device=user_device_data.serialNumber,
                        date=record.startDate,
                        mask=record.maskCode,
                    ).set(record.leakPercentile)

                    self.mask_seal_score.labels(
                        patient=record.sleepRecordPatientId,
                        device=user_device_data.serialNumber,
                        date=record.startDate,
                        mask=record.maskCode,
                    ).set(record.leakScore)

                    self.mask_onoff_count.labels(
                        patient=record.sleepRecordPatientId,
                        device=user_device_data.serialNumber,
                        date=record.startDate,
                        mask=record.maskCode,
                    ).set(record.maskPairCount)

                    self.mask_onoff_score.labels(
                        patient=record.sleepRecordPatientId,
                        device=user_device_data.serialNumber,
                        date=record.startDate,
                        mask=record.maskCode,
                    ).set(record.maskScore)

                    self.ahi.labels(
                        patient=record.sleepRecordPatientId,
                        device=user_device_data.serialNumber,
                        date=record.startDate,
                        mask=record.maskCode,
                    ).set(record.ahi)

                    self.ahi_score.labels(
                        patient=record.sleepRecordPatientId,
                        device=user_device_data.serialNumber,
                        date=record.startDate,
                        mask=record.maskCode,
                    ).set(record.ahiScore)

            lastReportDate = self.sleep_records_db.getLastReportDate(user_info.id)

            if lastReportDate is None:
                yesterday: datetime.datetime = datetime.datetime.now() - datetime.timedelta(days=1)
                lastReportDate = yesterday.strftime("%Y-%m-%d")

            self.patient.labels(
                id=user_info.id,
                name=f"{user_info.firstName} {user_info.lastName[:1]}",
                ahi=user_info.userEnteredAhi or 0,
            ).set(1)

            devices = self.device_db.list() or []
            for device in devices:
                active = device.serialNumber == user_device_data.serialNumber

                deviceLastReportDate = (
                    datetime.datetime.fromisoformat(device.lastSleepDataReportTime).strftime("%Y-%m-%d")
                    if device.lastSleepDataReportTime
                    else None
                )

                self.device.labels(
                    serialNumber=device.serialNumber,
                    manufacturer=device.fgDeviceManufacturerName,
                    type=device.deviceType,
                    name=device.localizedName,
                    image=device.imagePath,
                    lastReportDate=lastReportDate if active else deviceLastReportDate,
                    patient=device.fgDevicePatientId,
                ).set(1 if active else 0)

            usageSeconds = self.sleep_records_db.getTotalUsageSeconds(patientId=device.fgDevicePatientId)
            self.total_usage_seconds.clear()
            usageSeconds = self.sleep_records_db.getTotalUsageSeconds(patientId=user_device_data.fgDevicePatientId)
            self.total_usage_seconds.clear()
            self.total_usage_seconds.labels(patient=user_device_data.fgDevicePatientId).set(usageSeconds)

            masks = self.masks_db.list() or []
            for mask in masks:
                active = mask.maskCode == mask_info.maskCode
                self.mask.labels(
                    patient=mask.maskPatientId,
                    code=mask.maskCode,
                    name=mask.localizedName,
                    type=mask.maskType,
                    image=mask.imagePath,
                ).set(1 if active else 0)

            totalDays = self.sleep_records_db.getTotalDaysCount(user_info.id, includeZero=includeZero)
            self.total_days_count.clear()
            self.total_days_count.labels(
                patient=user_info.id,
                device=user_device_data.serialNumber,
                mask=mask_info.maskCode,
                lastReportDate=lastReportDate,
            ).set(totalDays)
