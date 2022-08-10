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
        Helper for depublication request

        """
        self.log = PlgLogger().log
        self.ntwk_requester_blk = QgsBlockingNetworkRequest()
        self.plg_settings = PlgOptionsManager.get_plg_settings()

    def get_base_url(self, datastore: str) -> str:
        """
        Get base url for delete publication

        Args:
            datastore: (str)
        Returns: url for offering
        """
        return f"{self.plg_settings.base_url_api_entrepot}/datastores/{datastore}"

    def delete_publication(self, datastore: str, offering_ids: str):
        """
        Delete a publication

        Args:
            offering_ids: (str) datastore_id : (str)
        """

        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req_get = QNetworkRequest(
            QUrl(f"{self.get_base_url(datastore)}/offerings/{offering_ids}")
        )

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

    def delete_configuration(self, datastore: str, configuration_ids: str):
        """
        Delete a configuration

        Args:
            configuration_id: (str) datastore_id : (str)
        """

        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req_get = QNetworkRequest(
            QUrl(f"{self.get_base_url(datastore)}/configurations/{configuration_ids}")
        )

        # headers
        req_get.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        feedback = QgsProcessingFeedback()

        # send request
        resp = self.ntwk_requester_blk.deleteResource(req_get, feedback)

        # check response
        if resp != QgsBlockingNetworkRequest.NoError:
            raise OfferingsRequestManager.UnavailableConfigurationsException(
                f"Error while fetching processing : {self.ntwk_requester_blk.errorMessage()}"
            )
