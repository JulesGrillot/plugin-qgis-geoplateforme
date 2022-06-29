import json
from dataclasses import dataclass
from typing import List

from qgis.core import QgsBlockingNetworkRequest
from qgis.PyQt.QtCore import QByteArray, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

from vectiler.toolbelt import PlgLogger, PlgOptionsManager


@dataclass
class TableRelation:
    name: str
    attributes: {}
    primary_key: str


@dataclass
class StoredData:
    id: str
    name: str
    type: str
    status: str
    tags: dict = None
    type_infos: dict = None

    def get_tables(self) -> List[TableRelation]:
        tables = []
        if self.type_infos:
            tables = [
                TableRelation(
                    relation["name"], relation["attributes"], relation["primary_key"]
                )
                for relation in self.type_infos["relations"]
                if relation["type"] == "TABLE"
            ]
        return tables


class StoredDataRequestManager:
    class ReadStoredDataException(Exception):
        pass

    class UnavailableStoredData(Exception):
        pass

    class AddTagException(Exception):
        pass

    def get_base_url(self, datastore: str) -> str:
        """
        Get base url for stored data for a datastore

        Args:
            datastore: (str) datastore id

        Returns: url for uploads

        """
        return f"{self.plg_settings.base_url_api_entrepot}/datastores/{datastore}/stored_data"

    def __init__(self):
        """
        Helper for stored_data request

        """
        self.log = PlgLogger().log
        self.ntwk_requester_blk = QgsBlockingNetworkRequest()
        self.plg_settings = PlgOptionsManager.get_plg_settings()

    def get_stored_data_list(self, datastore: str) -> List[StoredData]:
        """
        Get list of stored data

        Args:
            datastore: (str) datastore id

        Returns: list of available stored data, raise ReadStoredDataException otherwise
        """
        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req = QNetworkRequest(QUrl(self.get_base_url(datastore)))

        # headers
        req.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        # send request
        resp = self.ntwk_requester_blk.get(req, forceRefresh=True)

        # check response
        if resp != QgsBlockingNetworkRequest.NoError:
            raise self.ReadStoredDataException(
                f"Error while fetching stored data : {self.ntwk_requester_blk.errorMessage()}"
            )

        # check response
        req_reply = self.ntwk_requester_blk.reply()
        if (
            not req_reply.rawHeader(b"Content-Type")
            == "application/json; charset=utf-8"
        ):
            raise self.ReadStoredDataException(
                "Response mime-type is '{}' not 'application/json; charset=utf-8' as required.".format(
                    req_reply.rawHeader(b"Content-type")
                )
            )

        data = json.loads(req_reply.content().data().decode("utf-8"))
        stored_datas_id = [val["_id"] for val in data]

        return [
            self.get_stored_data(datastore, stored_data)
            for stored_data in stored_datas_id
        ]

    def get_stored_data(self, datastore: str, stored_data: str) -> StoredData:
        """
        Get stored data by id

        Args:
            datastore: (str) datastore id
            stored_data: (str) stored dat id

        Returns: stored data, raise ReadStoredDataException otherwise
        """
        data = self.get_stored_data_json(datastore, stored_data)
        result = StoredData(
            id=data["_id"], name=data["name"], type=data["type"], status=data["status"]
        )
        if "tags" in data:
            result.tags = data["tags"]
        if "type_infos" in data:
            result.type_infos = data["type_infos"]
        return result

    def get_stored_data_json(self, datastore: str, stored_data: str) -> dict:
        """
        Get dict values of stored data

        Args:
            datastore: (str) datastore id
            stored_data: (str) stored data id

        Returns: dict values of stored data, raise ReadStoredDataException otherwise
        """
        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req = QNetworkRequest(QUrl(f"{self.get_base_url(datastore)}/{stored_data}"))

        # headers
        req.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        # send request
        resp = self.ntwk_requester_blk.get(req, forceRefresh=True)

        # check response
        if resp != QgsBlockingNetworkRequest.NoError:
            raise self.ReadStoredDataException(
                f"Error while fetching stored data : {self.ntwk_requester_blk.errorMessage()}"
            )

        # check response
        req_reply = self.ntwk_requester_blk.reply()
        if (
            not req_reply.rawHeader(b"Content-Type")
            == "application/json; charset=utf-8"
        ):
            raise self.ReadStoredDataException(
                "Response mime-type is '{}' not 'application/json; charset=utf-8' as required.".format(
                    req_reply.rawHeader(b"Content-type")
                )
            )

        return json.loads(req_reply.content().data().decode("utf-8"))

    def add_tags(self, datastore: str, stored_data: str, tags: dict) -> None:
        """
        Add tags to stored data

        Args:
            datastore:  (str) datastore id
            stored_data: (str) stored_data id
            tags: (dict) dictionary of tags
        """
        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req_post = QNetworkRequest(
            QUrl(f"{self.get_base_url(datastore)}/{stored_data}/tags")
        )

        # headers
        req_post.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        # encode data
        data = QByteArray()
        data.append(json.dumps(tags))

        # send request
        resp = self.ntwk_requester_blk.post(req_post, data=data, forceRefresh=True)

        # check response
        if resp != QgsBlockingNetworkRequest.NoError:
            raise self.AddTagException(
                f"Error while adding tag to stored_data : {self.ntwk_requester_blk.errorMessage()}"
            )
