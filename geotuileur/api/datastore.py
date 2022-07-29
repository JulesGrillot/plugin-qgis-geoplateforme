# standard
import json
import logging

from numpy import empty

# PyQGIS
from qgis.core import QgsBlockingNetworkRequest
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

# project
from geotuileur.toolbelt.log_handler import PlgLogger
from geotuileur.toolbelt.preferences import PlgOptionsManager

logger = logging.getLogger(__name__)


class DatastoreRequestManager:
    class UnavailableEndpointException(Exception):
        pass

    def __init__(self):
        """
        Helper for Endpoint request

        """
        self.log = PlgLogger().log
        self.ntwk_requester_blk = QgsBlockingNetworkRequest()
        self.plg_settings = PlgOptionsManager.get_plg_settings()

    def get_base_url(self, datastore: str) -> str:
        """
        Get base url for endpoint

        Args:
            datastore: (str)

        Returns: url for Endpoint

        """
        return f"{self.plg_settings.base_url_api_entrepot}/datastores/{datastore}"

    def get_endpoint(self, datastore: str, data_type: str) -> str:
        """
        Get the endpoint for publication

        Args:
            datastores: (str), data_type: (str)


        """
        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req_get = QNetworkRequest(QUrl(self.get_base_url(datastore)))

        # headers
        req_get.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        # send request
        resp = self.ntwk_requester_blk.get(req_get)

        # check response
        if resp != QgsBlockingNetworkRequest.NoError:
            raise self.UnavailableEndpointException(
                f"Error while endpoint publication : "
                f"{self.ntwk_requester_blk.errorMessage()}"
            )
        # check response type
        req_reply = self.ntwk_requester_blk.reply()
        if (
            not req_reply.rawHeader(b"Content-Type")
            == "application/json; charset=utf-8"
        ):
            raise self.UnavailableEndpointException(
                "Response mime-type is '{}' not 'application/json; charset=utf-8' as required.".format(
                    req_reply.rawHeader(b"Content-type")
                )
            )

        data = json.loads(req_reply.content().data().decode("utf-8"))
        for i in range(0, len(data["endpoints"])):
            if data["endpoints"][i]["endpoint"]["type"] == data_type:
                data = data["endpoints"][i]["endpoint"]["_id"]

        if len(data) == 0:
            raise self.UnavailableEndpointException(
                f"Error while endpoint publication is empty : " f"{data}"
            )
        return data
