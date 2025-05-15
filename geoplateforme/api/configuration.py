# standard
import json
import logging
import math
import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Self

# PyQGIS
from qgis.PyQt.QtCore import QByteArray, QUrl

# project
from geoplateforme.api.custom_exceptions import (
    AddTagException,
    ConfigurationCreationException,
    OfferingCreationException,
    ReadConfigurationException,
    UnavailableConfigurationException,
)
from geoplateforme.toolbelt.log_handler import PlgLogger
from geoplateforme.toolbelt.network_manager import NetworkRequestsManager
from geoplateforme.toolbelt.preferences import PlgOptionsManager

logger = logging.getLogger(__name__)


class ConfigurationField(Enum):
    NAME = "name"
    LAYER_NAME = "layer_name"
    TYPE = "type"
    STATUS = "status"
    ATTRIBUTION = "attributions"
    METADATAS = "metadatas"
    TAGS = "tags"
    LAST_EVENT = "last_event"


class ConfigurationStatus(Enum):
    UNPUBLISHED = "UNPUBLISHED"
    PUBLISHED = "PUBLISHED"
    SYNCHRONIZING = "SYNCHRONIZING"


@dataclass
class Configuration:
    _id: str
    datastore_id: str
    is_detailed: bool = False

    # Optional
    _status: Optional[ConfigurationStatus] = None
    type_data: Optional[str] = None
    metadata: Optional[str] = None
    name: Optional[str] = None
    layer_name: Optional[str] = None
    type_infos: Optional[dict] = None
    attribution: Optional[dict] = None
    _tags: Optional[dict] = None
    _last_event: Optional[dict] = None

    @property
    def title(self) -> str:
        if self.type_infos and "title" in self.type_infos:
            return self.type_infos["title"]
        else:
            return ""

    @property
    def status(self) -> ConfigurationStatus:
        """Returns the status of the configuration.

        :return: configuration status
        :rtype: ConfigurationStatus
        """
        if not self._status and not self.is_detailed:
            self.update_from_api()
        return self._status

    @property
    def abstract(self) -> str:
        if self.type_infos and "abstract" in self.type_infos:
            return self.type_infos["abstract"]
        else:
            return ""

    @property
    def url_title(self) -> str:
        if self.type_infos and "title" in self.attribution:
            return self.attribution["title"]
        else:
            return ""

    @property
    def url(self) -> str:
        if self.attribution and "url" in self.attribution:
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

    def get_last_event_date(self) -> str:
        """Returns the configuration last_event date.

        :return: configuration last_event date
        :rtype: str
        """
        result = ""
        if self._last_event and "date" in self._last_event:
            result = self._last_event["date"]
        return result

    @classmethod
    def from_dict(cls, datastore_id: str, val: dict) -> Self:
        """Load object from a dict.

        :param datastore_id: datastore id
        :type datastore_id: str
        :param val: dict value to load
        :type val: dict

        :return: object with attributes filled from dict.
        :rtype: Configuration
        """
        res = cls(
            _id=val["_id"],
            datastore_id=datastore_id,
        )
        if "name" in val:
            res.name = val["name"]
        if "type" in val:
            res.type_data = val["type"]
        if "status" in val:
            res._status = ConfigurationStatus(val["status"])
        if "metadata" in val:
            res.metadata = val["metadata"]
        if "layer_name" in val:
            res.layer_name = val["layer_name"]
        if "type_infos" in val:
            res.type_infos = val["type_infos"]
        if "attribution" in val:
            res.attribution = val["attribution"]
        if "tags" in val:
            res._tags = val["tags"]
        if "last_event" in val:
            res._last_event = val["last_event"]

        return res

    def update_from_api(self):
        """Update the configuration by calling API details."""
        manager = ConfigurationRequestManager()
        data = manager.get_configuration_json(self.datastore_id, self._id)

        if "name" in data:
            self.name = data["name"]
        if "type" in data:
            self.type_data = data["type"]
        if "status" in data:
            self._status = ConfigurationStatus(data["status"])
        if "metadata" in data:
            self.metadata = data["metadata"]
        if "layer_name" in data:
            self.layer_name = data["layer_name"]
        if "type_infos" in data:
            self.type_infos = data["type_infos"]
        if "attribution" in data:
            self.attribution = data["attribution"]
        if "tags" in data:
            self._tags = data["tags"]
        if "last_event" in data:
            self._last_event = data["last_event"]
        self.is_detailed = True


class ConfigurationRequestManager:
    MAX_LIMIT = 50

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

        return Configuration.from_dict(
            datastore, self.get_configuration_json(datastore, configuration)
        )

    def get_configuration_json(self, datastore_id: str, configuration: str) -> dict:
        """Get dict values of configuration

        :param datastore_id: datastore id
        :type datastore_id: str
        :param configuration: configuration id
        :type configuration: str

        :raises ReadStoredDataException: when error occur during requesting the API

        :return: dict values of stored data
        :rtype: dict
        """
        try:
            # send request
            reply = self.request_manager.get_url(
                url=QUrl(f"{self.get_base_url(datastore_id)}/{configuration}"),
                config_id=self.plg_settings.qgis_auth_id,
            )
            return json.loads(reply.data().decode("utf-8"))
        except ConnectionError as err:
            raise ReadConfigurationException(
                f"Error while getting configuration : {err}"
            )

    def get_configuration_list(
        self,
        datastore_id: str,
        with_fields: Optional[List[ConfigurationField]] = None,
        tags: Optional[dict] = None,
    ) -> List[Configuration]:
        """Get list of configuration

        :param datastore_id: datastore id
        :type datastore_id: str
        :param with_fields: list of field to be add to the response
        :type with_fields: List[ConfigurationField], optional
        :param tags: list of tags to filter data
        :type tags: dict, optional

        :raises ReadConfigurationException: when error occur during requesting the API

        :return: list of available configuration
        :rtype: List[Configuration]
        """
        self.log(f"{__name__}.get_configuration_list(datastore:{datastore_id})")

        nb_value = self._get_nb_available_configuration(datastore_id, tags)
        nb_request = math.ceil(nb_value / self.MAX_LIMIT)
        result = []
        for page in range(0, nb_request):
            result += self._get_configuration_list(
                datastore_id, page + 1, self.MAX_LIMIT, with_fields, tags
            )
        return result

    def _get_configuration_list(
        self,
        datastore_id: str,
        page: int = 1,
        limit: int = MAX_LIMIT,
        with_fields: Optional[List[ConfigurationField]] = None,
        tags: Optional[dict] = None,
    ) -> List[Configuration]:
        """Get list of configuration

        :param datastore_id: datastore id
        :type datastore_id: str
        :param page: page number (start at 1)
        :type page: int
        :param limit: nb response per pages
        :type limit: int
        :param with_fields: list of field to be add to the response
        :type with_fields: List[ConfigurationField], optional
        :param tags: list of tags to filter data
        :type tags: dict, optional

        :raises ReadConfigurationException: when error occur during requesting the API

        :return: list of available configuration
        :rtype: List[Configuration]
        """

        # request additionnal fields
        add_fields = ""
        if with_fields:
            for field in with_fields:
                add_fields += f"&fields={field.value}"
        # Add filter on tags
        tags_url = ""
        if tags:
            for key, value in dict.items(tags):
                tags_url += f"&tags[{key}]={value}"

        try:
            reply = self.request_manager.get_url(
                url=QUrl(
                    f"{self.get_base_url(datastore_id)}?page={page}&limit={limit}{add_fields}{tags_url}"
                ),
                config_id=self.plg_settings.qgis_auth_id,
            )
        except ConnectionError as err:
            raise ReadConfigurationException(
                f"Error while fetching configuration : {err}"
            )

        data = json.loads(reply.data())
        return [
            Configuration.from_dict(datastore_id, stored_data) for stored_data in data
        ]

    def _get_nb_available_configuration(
        self, datastore_id: str, tags: Optional[dict] = None
    ) -> int:
        """Get number of available configuration

        :param datastore_id: datastore id
        :type datastore_id: str
        :param tags: list of tags to filter data
        :type tags: dict, optional

        :raises ReadConfigurationException: when error occur during requesting the API

        :return: number of available configuration
        :rtype: int
        """
        # For now read with maximum limit possible
        tags_url = ""
        if tags:
            for key, value in dict.items(tags):
                tags_url += f"&tags[{key}]={value}"
        try:
            req_reply = self.request_manager.get_url(
                url=QUrl(f"{self.get_base_url(datastore_id)}?limit=1{tags_url}"),
                config_id=self.plg_settings.qgis_auth_id,
                return_req_reply=True,
            )
        except ConnectionError as err:
            raise ReadConfigurationException(
                f"Error while fetching configuration : {err}"
            )

        # check response
        content_range = req_reply.rawHeader(b"Content-Range").data().decode("utf-8")
        match = re.match(
            r"(?P<min>\d+)\s?-\s?(?P<max>\d+)?\s?\/?\s?(?P<nb_val>\d+|\*)?",
            content_range,
        )
        if match:
            nb_val = int(match.group("nb_val"))
        else:
            raise ReadConfigurationException(
                f"Invalid Content-Range {content_range} not min-max/nb_val as expected"
            )
        return nb_val

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
