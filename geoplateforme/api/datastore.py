# standard
import json
import logging
from dataclasses import dataclass

# PyQGIS
from qgis.PyQt.QtCore import QUrl

# project
from geoplateforme.api.custom_exceptions import (
    UnavailableDatastoreException,
    UnavailableEndpointException,
)
from geoplateforme.toolbelt.log_handler import PlgLogger
from geoplateforme.toolbelt.network_manager import NetworkRequestsManager
from geoplateforme.toolbelt.preferences import PlgOptionsManager

logger = logging.getLogger(__name__)


@dataclass
class Datastore:
    id: str
    name: str
    technical_name: str
    storages: dict

    def get_storage_use_and_quota(self, storage_type: str) -> (int, int):
        """
        Get storage use and quota as tuple

        Args:
            storage_type: (str) storage type ("POSTGRESQL" or "FILESYSTEM" or "S3")

        Returns: (int,int) (use/quota)

        """
        result = (0, 0)
        for data in self.storages["data"]:
            if data["type"] == storage_type:
                result = (data["use"], data["quota"])
                break
        return result

    def get_upload_use_and_quota(self) -> (int, int):
        """
        Get upload use and quota as tuple

        Returns: (int,int) (use/quota)

        """
        result = (0, 0)
        if "uploads" in self.storages:
            result = (
                self.storages["uploads"]["use"],
                self.storages["uploads"]["quota"],
            )
        return result


class DatastoreRequestManager:
    def __init__(self):
        """
        Helper for datastore request

        """
        self.log = PlgLogger().log
        self.request_manager = NetworkRequestsManager()
        self.plg_settings = PlgOptionsManager.get_plg_settings()

    def get_base_url(self, datastore: str) -> str:
        """
        Get base url for endpoint

        Args:
            datastore: (str)

        Returns: url for Endpoint

        """
        return f"{self.plg_settings.base_url_api_entrepot}/datastores/{datastore}"

    def get_datastore(self, datastore: str) -> Datastore:
        """
        Get datastore by id

        Args:
            datastore: (str) datastore id

        Returns: Datastore data, raise UnavailableDatastoreException otherwise
        """
        self.log(f"{__name__}.get_datastore(datastore:{datastore})")

        try:
            reply = self.request_manager.get_url(
                url=QUrl(self.get_base_url(datastore)),
                config_id=self.plg_settings.qgis_auth_id,
            )
        except ConnectionError as err:
            raise UnavailableDatastoreException(
                f"Error while getting datastore : {err}"
            )

        data = json.loads(reply.data())
        result = Datastore(
            id=data["_id"],
            name=data["name"],
            technical_name=data["technical_name"],
            storages=data["storages"],
        )
        return result

    def get_endpoint(self, datastore: str, data_type: str) -> str:
        """
        Get the endpoint for publication

        Args:
            datastore: (str)
            data_type: (str)

        Returns: first available endpoint id for data_type, raise UnavailableEndpointException otherwise
        """
        self.log(
            f"{__name__}.get_endpoint(datastore:{datastore},data_type:{data_type})"
        )

        try:
            reply = self.request_manager.get_url(
                url=QUrl(self.get_base_url(datastore)),
                config_id=self.plg_settings.qgis_auth_id,
            )
        except ConnectionError as err:
            raise UnavailableEndpointException(
                f"Error while getting datastore endpoint : {err}"
            )

        data = json.loads(reply.data())
        for i in range(0, len(data["endpoints"])):
            if data["endpoints"][i]["endpoint"]["type"] == data_type:
                data = data["endpoints"][i]["endpoint"]["_id"]

        if len(data) == 0:
            raise UnavailableEndpointException(
                f"Error while endpoint publication is empty : {data}"
            )
        return data
