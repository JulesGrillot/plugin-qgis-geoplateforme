# standard
import json
import logging

# PyQGIS
from qgis.core import QgsBlockingNetworkRequest
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

from geotuileur.api.utils import qgs_blocking_get_request

# project
from geotuileur.toolbelt.log_handler import PlgLogger
from geotuileur.toolbelt.preferences import PlgOptionsManager

logger = logging.getLogger(__name__)


class OfferingsRequestManager:
    class UnavailableOfferingsException(Exception):
        pass

    def __init__(self):
        """
        Helper for get offerings request

        """
        self.log = PlgLogger().log
        self.ntwk_requester_blk = QgsBlockingNetworkRequest()
        self.plg_settings = PlgOptionsManager.get_plg_settings()

    def get_base_url(self, datastore: str) -> str:
        """
        Get base url for offerings

        Args:
            datastore: (str)

        Returns: url for offerings
        """
        return f"{self.plg_settings.base_url_api_entrepot}/datastores/{datastore}"

    def get_offerings_id(self, datastore: str, stored_data: str) -> list:
        """
        Get offerings id for a specific stored data on Geotuileur entrepot

        Args:
            datastore id :(str)
            stored data id : (str)

        """

        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req = QNetworkRequest(
            QUrl(f"{self.get_base_url(datastore)}/offerings?stored_data={stored_data}")
        )

        # headers
        req_reply = qgs_blocking_get_request(
            self.ntwk_requester_blk, req, self.UnavailableOfferingsException
        )
        data = json.loads(req_reply.content().data().decode("utf-8"))
        offering_ids = []
        for offering in data:
            offering_ids = offering["_id"]

        return offering_ids
