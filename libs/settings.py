import glob
import inspect
import json
import os
import sys
import traceback
import typing

import urllib.parse

from libs import utils
from libs.enums.loglevel import LogLevel


class Settings:
    APP_VERSION = "1.0.0-snapshot"

    def __init__(self):
        self._module = os.path.basename(__file__)[:-3]
        self._class = self.__class__.__name__

        self.name = None
        self.version = None
        self.log_level = utils.dict_get(os.environ, 'MAE_LOG_LEVEL', default_value='DEBUG')

        # build db_url from environment variables:
        # MAE_MONGODB_USERNAME
        # MAE_MONGODB_PASSWORD
        # MAE_MONGODB_HOST
        # MAE_MONGODB_PORT
        # MAE_MONGODB_AUTHSOURCE
        # if MAE_MONGODB_URL is set, use that instead

        self.db_url = utils.dict_get(
            os.environ,
            "MAE_MONGODB_URL",
            default_value="mongodb://{username}:{password}@{host}:{port}/{authsource}".format(
                username=urllib.parse.quote_plus(utils.dict_get(os.environ, "MAE_MONGODB_USERNAME")),
                password=urllib.parse.quote_plus(utils.dict_get(os.environ, "MAE_MONGODB_PASSWORD")),
                host=utils.dict_get(os.environ, "MAE_MONGODB_HOST", default_value="localhost"),
                port=utils.dict_get(os.environ, "MAE_MONGODB_PORT", default_value="27017"),
                authsource=utils.dict_get(os.environ, "MAE_MONGODB_AUTHSOURCE", default_value="admin"),
            ),
        )
        self.db_name = utils.dict_get(os.environ, "MAE_MONGODB_DATABASE", default_value="myair", required=True)

        self.myair = {
            "username": utils.dict_get(os.environ, "MAE_MYAIR_USERNAME", required=True),
            "password": utils.dict_get(os.environ, "MAE_MYAIR_PASSWORD", required=True),
            "device_token": utils.dict_get(os.environ, "MAE_MYAIR_DEVICE_TOKEN", default_value=None),
            "region": utils.dict_get(os.environ, "MAE_MYAIR_REGION", default_value="NA", required=True),
            # parse MAE_MYAIR_RECORDS_DAYS as an integer, default to 90 days
            "records_days": int(
                utils.dict_get(os.environ, "MAE_MYAIR_RECORDS_DAYS", default_value='90', required=True) or 90
            ),
        }

        # print(json.dumps(self.to_dict(), indent=2))

    def to_dict(self):
        return self.__dict__

    def get(self, name, default_value=None) -> typing.Any:
        return utils.dict_get(self.to_dict(), name, default_value)
