# standard
import json
import logging

# PyQGIS
from qgis.core import QgsBlockingNetworkRequest
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

# project
from geotuileur.toolbelt.log_handler import PlgLogger
from geotuileur.toolbelt.preferences import PlgOptionsManager

logger = logging.getLogger(__name__)


class OfferingsRequestManager:
    class UnavailableOfferingsException(Exception):
        pass

    def __init__(self):
        """
        Helper for offering request

        """
        self.log = PlgLogger().log
        self.ntwk_requester_blk = QgsBlockingNetworkRequest()
        self.plg_settings = PlgOptionsManager.get_plg_settings()

    def get_base_url(self, datastore: str) -> str:
        """
        Get base url for offering

        Args:
            datastore: (str) configuration : (str)

        Returns: url for offering
        """
        return f"{self.plg_settings.base_url_api_entrepot}/datastores/{datastore}"

    def get_offerings(self, datastore: str, stored_data: str):
        """
        Create offering on Geotuileur entrepot

        Args:
            configuration_id: (str) datastore_id :(str)
            visibility :(str) endpoint : (str)

        """

        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req_get = QNetworkRequest(
            QUrl(f"{self.get_base_url(datastore)}/offerings?stored_data={stored_data}")
        )

        #'''cf méthode qgs_blocking_get_request'''
        # headers
        req_get.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        # send request
        resp = self.ntwk_requester_blk.get(req_get, forceRefresh=True)

        # check response
        if resp != QgsBlockingNetworkRequest.NoError:
            raise self.UnavailableOfferingsException(
                f"Error while fetching processing : {self.ntwk_requester_blk.errorMessage()}"
            )

        # check response
        req_reply = self.ntwk_requester_blk.reply()
        if (
            not req_reply.rawHeader(b"Content-Type")
            == "application/json; charset=utf-8"
        ):
            raise self.UnavailableOfferingsException(
                "Response mime-type is '{}' not 'application/json; charset=utf-8' as required.".format(
                    req_reply.rawHeader(b"Content-type")
                )
            )

        # encode data

        data = json.loads(req_reply.content().data().decode("utf-8"))

        offering_id = []
        for i in range(0, len(data)):
            offering_id = data[i]["_id"]
        return offering_id
