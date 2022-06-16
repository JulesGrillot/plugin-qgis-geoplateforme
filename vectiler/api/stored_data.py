import json

from PyQt5.QtCore import QUrl, QByteArray
from PyQt5.QtNetwork import QNetworkRequest
from qgis.core import QgsBlockingNetworkRequest

from vectiler.toolbelt import PlgLogger, PlgOptionsManager


class StoredDataRequestManager:
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

    def add_tags(self, datastore: str, stored_data: str, tags: dict) -> None:
        """
        Add tags to stored data

        Args:
            datastore:  (str) datastore id
            stored_data: (str) stored_data id
            tags: (dict) dictionary of tags
        """
        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req_post = QNetworkRequest(QUrl(f'{self.get_base_url(datastore)}/{stored_data}/tags'))

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
                f"Error while adding tag to stored_data : {self.ntwk_requester_blk.errorMessage()}")
