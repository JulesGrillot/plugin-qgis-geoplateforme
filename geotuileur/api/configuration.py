# standard
import json
import logging
from dataclasses import dataclass

# PyQGIS
from qgis.core import QgsBlockingNetworkRequest
from qgis.PyQt.QtCore import QByteArray, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

# project
from geotuileur.toolbelt.log_handler import PlgLogger
from geotuileur.toolbelt.preferences import PlgOptionsManager

logger = logging.getLogger(__name__)


@dataclass
class Configuration:

    type_data: str
    metadata: str
    name: str
    layer_name: str
    type_infos: dict
    attribution: dict

    @property
    def title(self) -> str:
        if "title" in self.type_infos:
            return self.type_infos["title"]
        else:
            return ""

    @property
    def abstract(self) -> str:
        if "abstract" in self.type_infos:
            return self.type_infos["abstract"]
        else:
            return ""

    @property
    def url_title(self) -> str:
        if "title" in self.attribution:
            return self.attribution["title"]
        else:
            return ""

    @property
    def url(self) -> str:
        if "url" in self.attribution:
            return self.attribution["url"]
        else:
            return ""

    @title.setter
    def title(self, val: str) -> None:
        self.type_infos["title"] = val

    @abstract.setter
    def abstract(self, val: str) -> None:
        self.type_infos["abstract"] = val

    @url_title.setter
    def url_title(self, val: str) -> None:
        self.attribution["title"] = val

    @url.setter
    def url(self, val: str) -> None:
        self.attribution["url"] = val


class ConfigurationRequestManager:
    class UnavailableConfigurationException(Exception):
        pass

    class ConfigurationCreationException(Exception):
        pass

    def __init__(self):
        """
        Helper for configuration request

        """
        self.log = PlgLogger().log
        self.ntwk_requester_blk = QgsBlockingNetworkRequest()
        self.plg_settings = PlgOptionsManager.get_plg_settings()

    def get_base_url(self, datastore: str) -> str:
        """
        Get base url for configuration for a datastore

        Args:
            datastore: (str) datastore id

        Returns: url for configuration

        """
        return f"{self.plg_settings.base_url_api_entrepot}/datastores/{datastore}/configurations"

    def create_configuration(
        self,
        datastore: str,
        stored_data: str,
        top_level: int,
        bottom_level: int,
        configuration: Configuration,
    ) -> Configuration:
        """
        Create configuration on Geotuileur entrepot

        Args:
            datastore: (str) datastore id
            configuration

        Returns: Upload if creation succeeded, raise UploadCreationException otherwise

        """
        configuration.type_infos["used_data"] = [
            {
                "stored_data": stored_data,
                "top_level": str(top_level),
                "bottom_level": str(bottom_level),
            }
        ]

        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req_post = QNetworkRequest(QUrl(self.get_base_url(datastore)))
        # headers
        req_post.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        # encode data
        data = QByteArray()
        data_map = {
            "type": configuration.type_data,
            "metadata": configuration.metadata,
            "name": configuration.name,
            "layer_name": configuration.layer_name,
            "type_infos": configuration.type_infos,
            "attribution": configuration.attribution,
        }
        data.append(json.dumps(data_map))
        self.log(message=f" creation data map CONFIG: {data}", log_level=4)

        # send request
        resp = self.ntwk_requester_blk.post(req_post, data=data)

        # check response
        if resp != QgsBlockingNetworkRequest.NoError:
            raise self.ConfigurationCreationException(
                f"Error while creating configuration : "
                f"{self.ntwk_requester_blk.errorMessage()}"
            )
        # check response type
        req_reply = self.ntwk_requester_blk.reply()
        if (
            not req_reply.rawHeader(b"Content-Type")
            == "application/json; charset=utf-8"
        ):
            raise self.ConfigurationCreationException(
                "Response mime-type is '{}' not 'application/json; charset=utf-8' as required.".format(
                    req_reply.rawHeader(b"Content-type")
                )
            )

        data = json.loads(req_reply.content().data().decode("utf-8"))
        print(data.keys())

        return data["_id"]
