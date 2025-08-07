import os

from libs import settings
from libs.mongodb.BaseDatabase import BaseDatabase


class Database(BaseDatabase):
    def __init__(self) -> None:
        super().__init__()
        # get the file name without the extension and without the directory
        self._module = os.path.basename(__file__)[:-3]
        self._class = self.__class__.__name__
        self.client = None
        self.connection = None
        pass
