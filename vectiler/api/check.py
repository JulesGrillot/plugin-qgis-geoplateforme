import logging
from dataclasses import dataclass

from qgis.core import QgsBlockingNetworkRequest

from vectiler.api.client import NetworkRequestsManager
from vectiler.toolbelt import PlgLogger, PlgOptionsManager

logger = logging.getLogger(__name__)


@dataclass
class Check:
    id: str
    name: str


@dataclass
class Execution:
    id: str
    status: str
    check: Check


class CheckRequestManager:
    class UnavailableExecutionException(Exception):
        pass

    def __init__(self):
        """
        Helper for checks request

        """
        self.log = PlgLogger().log
        self.request_manager = NetworkRequestsManager()
        self.ntwk_requester_blk = QgsBlockingNetworkRequest()
        self.plg_settings = PlgOptionsManager.get_plg_settings()

    def get_base_url(self, datastore: str) -> str:
        """
        Get base url for checks for a datastore

        Args:
            datastore: (str) datastore id

        Returns: url for uploads

        """
        return f"{self.plg_settings.base_url_api_entrepot}/datastores/{datastore}/checks"
