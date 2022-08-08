import json
import logging
from dataclasses import dataclass
from enum import Enum

from qgis.core import QgsBlockingNetworkRequest
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

from geotuileur.api.client import NetworkRequestsManager
from geotuileur.api.utils import qgs_blocking_get_request
from geotuileur.toolbelt import PlgLogger, PlgOptionsManager

logger = logging.getLogger(__name__)


@dataclass
class CheckExecution:
    id: str
    status: str
    name: str
    creation: str
    start: str = ""
    finish: str = ""


class CheckExecutionStatus(Enum):
    WAITING = "WAITING"
    PROGRESS = "PROGRESS"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


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
        return (
            f"{self.plg_settings.base_url_api_entrepot}/datastores/{datastore}/checks"
        )

    def get_execution(self, datastore: str, exec_id: str) -> CheckExecution:
        """
        Get execution.

        Args:
            datastore: (str) datastore id
            exec_id: (str) execution id

        Returns: CheckExecution execution if execution available, raise UnavailableExecutionException otherwise
        """
        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req = QNetworkRequest(
            QUrl(f"{self.get_base_url(datastore)}/executions/{exec_id}")
        )

        req_reply = qgs_blocking_get_request(
            self.ntwk_requester_blk, req, self.UnavailableExecutionException
        )
        data = json.loads(req_reply.content().data().decode("utf-8"))
        execution = CheckExecution(
            id=data["_id"],
            status=data["status"],
            name=data["check"]["name"],
            creation=data["creation"],
        )

        if "start" in data:
            execution.start = data["start"]
        if "finish" in data:
            execution.finish = data["finish"]

        return execution

    def get_execution_logs(self, datastore: str, exec_id: str) -> str:
        """
        Get execution logs.

        Args:
            datastore: (str) datastore id
            exec_id: (str) execution id

        Returns: (str) Execution logs if execution available, raise UnavailableExecutionException otherwise
        """
        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req = QNetworkRequest(
            QUrl(f"{self.get_base_url(datastore)}/executions/{exec_id}/logs")
        )

        req_reply = qgs_blocking_get_request(
            self.ntwk_requester_blk,
            req,
            self.UnavailableExecutionException,
            expected_type="plain/text; charset=utf-8",
        )
        data = req_reply.content().data().decode("utf-8")
        return data
