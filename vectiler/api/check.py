import json
import logging
from dataclasses import dataclass

from PyQt5.QtCore import QUrl
from PyQt5.QtNetwork import QNetworkRequest
from qgis.core import QgsBlockingNetworkRequest

from vectiler.api.client import NetworkRequestsManager
from vectiler.api.execution import Execution
from vectiler.toolbelt import PlgLogger, PlgOptionsManager

logger = logging.getLogger(__name__)


@dataclass
class Check:
    id: str
    name: str


class CheckRequestManager:
    class UnavailableExecutionException(Exception):
        pass

    def __init__(self):
        """
        Helper for checks request

        """
        self.log = PlgLogger().log
        self.request_manager = NetworkRequestsManager()
        self.ntwk_requester_blk = QgsBlockingNetworkRequest()
        self.plg_settings = PlgOptionsManager.get_plg_settings()

    def get_base_url(self, datastore: str) -> str:
        """
        Get base url for checks for a datastore

        Args:
            datastore: (str) datastore id

        Returns: url for uploads

        """
        return f"{self.plg_settings.base_url_api_entrepot}/datastores/{datastore}/checks"

    def get_execution(self, datastore: str, exec_id: str) -> Execution:
        """
        Get execution.

        Args:
            datastore: (str) datastore id
            exec_id: (str) execution id

        Returns: Execution execution if execution available, raise UnavailableExecutionException otherwise
        """
        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req = QNetworkRequest(QUrl(f'{self.get_base_url(datastore)}/executions/{exec_id}'))

        # headers
        req.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        # send request
        resp = self.ntwk_requester_blk.get(req, forceRefresh=True)

        # check response
        if resp != QgsBlockingNetworkRequest.NoError:
            raise self.UnavailableExecutionException(
                f"Error while fetching execution : {self.ntwk_requester_blk.errorMessage()}")

        # check response
        req_reply = self.ntwk_requester_blk.reply()
        if not req_reply.rawHeader(b"Content-Type") == "application/json; charset=utf-8":
            raise self.UnavailableExecutionException(
                "Response mime-type is '{}' not 'application/json; charset=utf-8' as required.".format(
                    req_reply.rawHeader(b"Content-type")
                )
            )

        data = json.loads(req_reply.content().data().decode("utf-8"))
        execution = Execution(id=data["_id"], status=data["status"],
                              name=data["check"]["name"])
        if "start" in data:
            execution.start = data["start"]
        if "finish" in data:
            execution.finish = data["finish"]

        return execution
