# standard
import logging

# PyQGIS
from qgis.core import QgsBlockingNetworkRequest, QgsProcessingFeedback
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

# project
from geotuileur.toolbelt.log_handler import PlgLogger
from geotuileur.toolbelt.preferences import PlgOptionsManager

logger = logging.getLogger(__name__)


class DepublicationRequestManager:
    class UnavailableDepublicationException(Exception):
        pass

    def __init__(self):
        """
        Helper for offering request

        """
        self.log = PlgLogger().log
        self.ntwk_requester_blk = QgsBlockingNetworkRequest()
        self.plg_settings = PlgOptionsManager.get_plg_settings()

    def get_base_url(self, datastore: str, offering_id: str) -> str:
        """
        Get base url for delete publication

        Args:
            datastore: (str) offering_id : (str)

        Returns: url for offering
        """
        return f"{self.plg_settings.base_url_api_entrepot}/datastores/{datastore}/offerings/{offering_id}"

    def delete_publication(self, datastore: str, offering_id: str):
        """
        Delete a publication

        Args:
            offering_id: (str) datastore_id : (str)
        """

        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req_get = QNetworkRequest(QUrl(self.get_base_url(datastore, offering_id)))

        # headers
        req_get.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        feedback = QgsProcessingFeedback()

        # send request
        resp = self.ntwk_requester_blk.deleteResource(req_get, feedback)

        # check response
        if resp != QgsBlockingNetworkRequest.NoError:
            raise self.UnavailableDepublicationException(
                f"Error while fetching processing : {self.ntwk_requester_blk.errorMessage()}"
            )

        # check response
        req_reply = self.ntwk_requester_blk.reply()
        if (
            not req_reply.rawHeader(b"Content-Type")
            == "application/json; charset=utf-8"
        ):
            raise self.UnavailableDepublicationException(
                "Response mime-type is '{}' not 'application/json; charset=utf-8' as required.".format(
                    req_reply.rawHeader(b"Content-type")
                )
            )
