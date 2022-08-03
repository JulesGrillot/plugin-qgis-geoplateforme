# standard
import json
import logging

# PyQGIS
from qgis.core import QgsBlockingNetworkRequest
from qgis.PyQt.QtCore import QByteArray, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

# project
from geotuileur.toolbelt.log_handler import PlgLogger
from geotuileur.toolbelt.preferences import PlgOptionsManager

logger = logging.getLogger(__name__)


class OfferingRequestManager:
    class UnavailableOfferingException(Exception):
        pass

    class OfferingCreationException(Exception):
        pass

    def __init__(self):
        """
        Helper for offering request

        """
        self.log = PlgLogger().log
        self.ntwk_requester_blk = QgsBlockingNetworkRequest()
        self.plg_settings = PlgOptionsManager.get_plg_settings()

    def get_base_url(self, datastore: str, configuration_id: str) -> str:
        """
        Get base url for offering

        Args:
            datastore: (str) configuration : (str)

        Returns: url for offering

        """
        return f"{self.plg_settings.base_url_api_entrepot}/datastores/{datastore}/configurations/{configuration_id}/offerings"

    def create_offering(
        self, visibility: str, endpoint: str, datastore: str, configuration_id: str
    ):
        """
        Create offering on Geotuileur entrepot

        Args:
            configuration_id: (str) datastore_id :(str)
            visibility :(str) endpoint : (str)




        """
        self.log(
            message="Offering creation options: "
            f"visibility={visibility}, endpoint={endpoint}, "
            f"datastore={datastore}, configuration_id={configuration_id}",
            log_level=4,
        )

        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req_post = QNetworkRequest(QUrl(self.get_base_url(datastore, configuration_id)))

        # headers
        req_post.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        # encode data
        data = QByteArray()
        data_map = {
            "visibility": visibility,
            "endpoint": endpoint,
        }

        data.append(json.dumps(data_map))

        self.log(message=f" creation data map : {data}", log_level=4)

        # send request
        resp = self.ntwk_requester_blk.post(req_post, data=data)

        # check response
        if resp != QgsBlockingNetworkRequest.NoError:
            raise self.OfferingCreationException(
                f"Error while creating publication : "
                f"{self.ntwk_requester_blk.errorMessage()}"
            )
        # check response type
        req_reply = self.ntwk_requester_blk.reply()
        if (
            not req_reply.rawHeader(b"Content-Type")
            == "application/json; charset=utf-8"
        ):
            raise self.OfferingCreationException(
                "Response mime-type is '{}' not 'application/json; charset=utf-8' as required.".format(
                    req_reply.rawHeader(b"Content-type")
                )
            )

        data = json.loads(req_reply.content().data().decode("utf-8"))
        return data["urls"]
