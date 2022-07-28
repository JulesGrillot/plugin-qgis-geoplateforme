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


class EndpointRequestManager:
    class UnavailableEndpointException(Exception):
        pass

    class EndpointCreationException(Exception):
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
        Get base url for Endpoint

        Args:
            datastore: (str)

        Returns: url for Endpoint

        """
        return f"{self.plg_settings.base_url_api_entrepot}/datastores/{datastore}"

    def create_endpoint(self, datastore: str):
        """
        Create Endpoint on Geotuileur entrepot

        Args:
            datastores: (str)


        """
        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req_get = QNetworkRequest(QUrl(self.get_base_url(datastore)))

        # headers
        req_get.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        # send request
        resp = self.ntwk_requester_blk.get(req_get)

        # check response
        if resp != QgsBlockingNetworkRequest.NoError:
            raise self.EndpointCreationException(
                f"Error while endpoint publication : "
                f"{self.ntwk_requester_blk.errorMessage()}"
            )
        # check response type
        req_reply = self.ntwk_requester_blk.reply()
        if (
            not req_reply.rawHeader(b"Content-Type")
            == "application/json; charset=utf-8"
        ):
            raise self.EndpointCreationException(
                "Response mime-type is '{}' not 'application/json; charset=utf-8' as required.".format(
                    req_reply.rawHeader(b"Content-type")
                )
            )

        data = json.loads(req_reply.content().data().decode("utf-8"))
        data = data["endpoints"][0]["endpoint"]["_id"]
        self.log(
            message=f"result endpoint: {data}",
            log_level=4,
        )

        return data
