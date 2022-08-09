# standard
import logging

# PyQGIS
from qgis.core import QgsBlockingNetworkRequest, QgsProcessingFeedback
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

from geotuileur.api.offerings import OfferingsRequestManager

# project
from geotuileur.toolbelt.log_handler import PlgLogger
from geotuileur.toolbelt.preferences import PlgOptionsManager

logger = logging.getLogger(__name__)


class DepublicationRequestManager:
    def __init__(self):
        """
        Helper for offering request

        """
        self.log = PlgLogger().log
        self.ntwk_requester_blk = QgsBlockingNetworkRequest()
        self.plg_settings = PlgOptionsManager.get_plg_settings()

    def get_base_url(self, datastore: str, offering_ids: str) -> str:
        """
        Get base url for delete publication

        Args:
            datastore: (str) offering_ids : (str)

        Returns: url for offering
        """
        return f"{self.plg_settings.base_url_api_entrepot}/datastores/{datastore}/offerings/{offering_ids}"

    def delete_publication(self, datastore: str, offering_ids: str):
        """
        Delete a publication

        Args:
            offering_ids: (str) datastore_id : (str)
        """

        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req_get = QNetworkRequest(QUrl(self.get_base_url(datastore, offering_ids)))

        # headers
        req_get.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        feedback = QgsProcessingFeedback()

        # send request
        resp = self.ntwk_requester_blk.deleteResource(req_get, feedback)

        # check response
        if resp != QgsBlockingNetworkRequest.NoError:
            raise OfferingsRequestManager.UnavailableOfferingsException(
                f"Error while fetching processing : {self.ntwk_requester_blk.errorMessage()}"
            )

        # check response
        req_reply = self.ntwk_requester_blk.reply()
        if (
            not req_reply.rawHeader(b"Content-Type")
            == "application/json; charset=utf-8"
        ):
            raise OfferingsRequestManager.UnavailableOfferingsException(
                "Response mime-type is '{}' not 'application/json; charset=utf-8' as required.".format(
                    req_reply.rawHeader(b"Content-type")
                )
            )
