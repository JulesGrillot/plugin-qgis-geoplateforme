# standard
import json
import logging

# PyQGIS
from qgis.core import QgsBlockingNetworkRequest
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

# project
from geotuileur.api.custom_exceptions import UnavailableOfferingsException
from geotuileur.api.utils import qgs_blocking_get_request
from geotuileur.toolbelt.log_handler import PlgLogger
from geotuileur.toolbelt.preferences import PlgOptionsManager

logger = logging.getLogger(__name__)


class OfferingsRequestManager:
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
        return f"{self.plg_settings.base_url_api_entrepot}/datastores/{datastore}/offerings"

    def get_offerings_id(self, datastore: str, stored_data: str) -> list:
        """
        Get offerings id for a specific stored data on Geotuileur entrepot

        Args:
            datastore id :(str)
            stored data id : (str)

        """
        self.log(
            f"{__name__}.get_offerings_id(datastore:{datastore},stored_data:{stored_data})"
        )

        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req = QNetworkRequest(
            QUrl(f"{self.get_base_url(datastore)}?stored_data={stored_data}")
        )

        # headers
        req_reply = qgs_blocking_get_request(
            self.ntwk_requester_blk, req, UnavailableOfferingsException
        )

        data = json.loads(req_reply.content().data().decode("utf-8"))

        offering_ids = [offering["_id"] for offering in data]

        return offering_ids

    def delete_offering(self, datastore: str, offering_id: str):
        """
        Delete offering

        Args:
            datastore: (str)
            offering_id : (str)
        """
        self.log(
            f"{__name__}.delete_offering(datastore:{datastore},offering_id:{offering_id})"
        )

        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req_get = QNetworkRequest(QUrl(f"{self.get_base_url(datastore)}/{offering_id}"))

        # headers
        req_get.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        # send request
        resp = self.ntwk_requester_blk.deleteResource(req_get)

        # check response
        if resp != QgsBlockingNetworkRequest.NoError:
            raise UnavailableOfferingsException(
                f"Error while fetching processing : {self.ntwk_requester_blk.errorMessage()}"
            )
