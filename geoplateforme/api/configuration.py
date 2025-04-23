# standard
import json
import logging
from dataclasses import dataclass

# PyQGIS
from qgis.PyQt.QtCore import QByteArray, QUrl

# project
from geoplateforme.api.custom_exceptions import (
    AddTagException,
    ConfigurationCreationException,
    OfferingCreationException,
    UnavailableConfigurationException,
)
from geoplateforme.toolbelt.log_handler import PlgLogger
from geoplateforme.toolbelt.network_manager import NetworkRequestsManager
from geoplateforme.toolbelt.preferences import PlgOptionsManager

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
    def __init__(self):
        """
        Helper for configuration request

        """
        self.log = PlgLogger().log
        self.request_manager = NetworkRequestsManager()
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
    ) -> str:
        """
        Create configuration on Geoplateforme entrepot

        Args:
            datastore: (str) datastore id
            configuration

        Returns: Upload if creation succeeded, raise UploadCreationException otherwise

        """
        self.log(
            f"{__name__}.create_configuration(datastore:{datastore}, stored_data: {stored_data}, "
            f"top_level: {top_level}, bottom_level: {bottom_level}, configuration: {configuration})"
        )

        configuration.type_infos["used_data"] = [
            {
                "stored_data": stored_data,
                "top_level": str(top_level),
                "bottom_level": str(bottom_level),
            }
        ]

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
        try:
            # send request
            reply = self.request_manager.post_url(
                url=QUrl(self.get_base_url(datastore)),
                config_id=self.plg_settings.qgis_auth_id,
                data=data,
                headers={b"Content-Type": bytes("application/json", "utf8")},
            )
        except ConnectionError as err:
            raise ConfigurationCreationException(
                f"Error while creating configuration : {err}"
            )
        data = json.loads(reply.data())
        return data["_id"]

    def get_configurations_id(self, datastore: str, stored_data: str) -> list:
        """
        get  configuration id list from stored data

        Args:
            datastore: (str) stored_data : (str)
        """
        self.log(
            f"{__name__}.get_configurations_id(datastore:{datastore}, stored_data: {stored_data})"
        )
        try:
            # send request
            reply = self.request_manager.get_url(
                url=QUrl(f"{self.get_base_url(datastore)}?stored_data={stored_data}"),
                config_id=self.plg_settings.qgis_auth_id,
            )
        except ConnectionError as err:
            raise UnavailableConfigurationException(
                f"Error while getting configuration : {err}"
            )
        data = json.loads(reply.data().decode("utf-8"))
        configuration_ids = [configuration["_id"] for configuration in data]

        return configuration_ids

    def get_configuration(self, datastore: str, configuration: str) -> Configuration:
        """
        get configuration informations

        Args :
            datastore : (str) , configuration : (str)
        """
        self.log(
            f"{__name__}.get_configuration(datastore:{datastore}, configuration: {configuration})"
        )

        try:
            # send request
            reply = self.request_manager.get_url(
                url=QUrl(f"{self.get_base_url(datastore)}/{configuration}"),
                config_id=self.plg_settings.qgis_auth_id,
            )
        except ConnectionError as err:
            raise UnavailableConfigurationException(
                f"Error while getting configuration : {err}"
            )
        data = json.loads(reply.data().decode("utf-8"))
        return self._create_configuration_from_json(data)

    def _create_configuration_from_json(self, data: dict) -> Configuration:
        """
        Get config by id

        Args:
            datastore: (str) datastore id
            stored_data: (str) stored dat id

        Returns: stored data, raise ReadStoredDataException otherwise
        """

        result = Configuration(
            type_data=data["type"],
            metadata=data["metadata"],
            name=data["name"],
            layer_name=data["layer_name"],
            type_infos=data["type_infos"],
            attribution=data["attribution"],
        )

        return result

    def delete_configuration(self, datastore: str, configuration_ids: str):
        """
        Delete a configuration

        Args:
            configuration_id: (str) datastore_id : (str)
        """
        self.log(
            f"{__name__}.delete_configuration(datastore:{datastore}, configuration_ids: {configuration_ids})"
        )

        try:
            # send request
            self.request_manager.delete_url(
                url=QUrl(f"{self.get_base_url(datastore)}/{configuration_ids}"),
                config_id=self.plg_settings.qgis_auth_id,
                headers={b"Content-Type": bytes("application/json", "utf8")},
            )

        except ConnectionError as err:
            raise UnavailableConfigurationException(
                f"Error while getting configuration : {err}"
            )

    def create_offering(
        self, visibility: str, endpoint: str, datastore: str, configuration_id: str
    ):
        """
        Create offering on Geoplateforme entrepot

        Args:
            configuration_id: (str) datastore_id :(str)
            visibility :(str) endpoint : (str)

        """
        self.log(
            f"{__name__}.create_offering(visibility:{visibility}, endpoint: {endpoint}, datastore: {datastore}, configuration_id: {configuration_id})"
        )

        # encode data
        data = QByteArray()
        data_map = {
            "visibility": visibility,
            "endpoint": endpoint,
        }

        data.append(json.dumps(data_map))

        try:
            # send request
            reply = self.request_manager.post_url(
                url=QUrl(
                    f"{self.get_base_url(datastore)}/{configuration_id}/offerings"
                ),
                config_id=self.plg_settings.qgis_auth_id,
                data=data,
                headers={b"Content-Type": bytes("application/json", "utf8")},
            )

        except ConnectionError as err:
            raise OfferingCreationException(f"Error while creating publication : {err}")

        data = json.loads(reply.data())
        return data["urls"]

    def add_tags(self, datastore_id: str, configuration_id: str, tags: dict) -> None:
        """Add tags to stored data

        :param datastore_id: datastore id
        :type datastore_id: str
        :param configuration_id: configuration id
        :type configuration_id: str
        :param tags: dictionary of tags
        :type tags: dict

        :raises AddTagException: when error occur during requesting the API
        """
        self.log(
            f"{__name__}.add_tags(datastore_id:{datastore_id},configuration_id:{configuration_id}, tags:{tags})"
        )

        try:
            # encode data
            data = QByteArray()
            data.append(json.dumps(tags))
            self.request_manager.post_url(
                url=QUrl(f"{self.get_base_url(datastore_id)}/{configuration_id}/tags"),
                config_id=self.plg_settings.qgis_auth_id,
                data=data,
                headers={b"Content-Type": bytes("application/json", "utf8")},
            )
        except ConnectionError as err:
            raise AddTagException(f"Error while adding tag to configuration : {err}")
