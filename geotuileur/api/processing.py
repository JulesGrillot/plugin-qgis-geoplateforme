import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from qgis.core import QgsBlockingNetworkRequest
from qgis.PyQt.QtCore import QByteArray, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

from geotuileur.api.utils import send_qgs_blocking_request
from geotuileur.toolbelt import PlgLogger, PlgOptionsManager


class ExecutionStatus(Enum):
    CREATED = "CREATED"
    WAITING = "WAITING"
    PROGRESS = "PROGRESS"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    ABORTED = "ABORTED"


@dataclass
class Execution:
    id: str
    status: str
    name: str
    creation: datetime = None
    launch: datetime = None
    start: datetime = None
    finish: datetime = None


@dataclass
class Processing:
    name: str
    id: str


class ProcessingRequestManager:
    class UnavailableProcessingException(Exception):
        pass

    class UnavailableExecutionException(Exception):
        pass

    class UnavailableStoredDataException(Exception):
        pass

    class CreateProcessingException(Exception):
        pass

    class LaunchExecutionException(Exception):
        pass

    def __init__(self):
        """
        Helper for processing request

        """
        self.log = PlgLogger().log
        self.ntwk_requester_blk = QgsBlockingNetworkRequest()
        self.plg_settings = PlgOptionsManager.get_plg_settings()

    def get_base_url(self, datastore: str) -> str:
        """
        Get base url for processings for a datastore

        Args:
            datastore: (str) datastore id

        Returns: url for processings

        """
        return f"{self.plg_settings.base_url_api_entrepot}/datastores/{datastore}/processings"

    def get_processing(self, datastore: str, name: str) -> Processing:
        """
        Get processing from name.

        Raises UnavailableProcessingException if processing not available or error in request

        Args:
            datastore: (str) datastore id
            name: (str) wanted processing name

        Returns: Processing

        """
        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req = QNetworkRequest(QUrl(f"{self.get_base_url(datastore)}"))

        req_reply = send_qgs_blocking_request(
            self.ntwk_requester_blk, req, self.UnavailableProcessingException
        )
        processing_list = json.loads(req_reply.content().data().decode("utf-8"))
        for processing in processing_list:
            if processing["name"] == name:
                return Processing(name=processing["name"], id=processing["_id"])

        raise self.UnavailableProcessingException("Processing not available in server")

    def create_processing_execution(self, datastore: str, input_map: dict) -> dict:
        """
        Create a processing execution from an input map

        Args:
            datastore: (str) datastore id
            input_map: (dict) input map containing processing id

        Returns: (dict) result map containing created execution in _id

        """
        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req_post = QNetworkRequest(QUrl(f"{self.get_base_url(datastore)}/executions"))

        # headers
        req_post.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        # encode data
        data = QByteArray()
        data.append(json.dumps(input_map))

        # send request
        resp = self.ntwk_requester_blk.post(req_post, data=data, forceRefresh=True)

        # check response
        if resp != QgsBlockingNetworkRequest.NoError:
            raise self.CreateProcessingException(
                f"Error while creating processing execution : {self.ntwk_requester_blk.errorMessage()}"
            )

        # check response
        req_reply = self.ntwk_requester_blk.reply()
        if (
            not req_reply.rawHeader(b"Content-Type")
            == "application/json; charset=utf-8"
        ):
            raise self.CreateProcessingException(
                "Response mime-type is '{}' not 'application/json; charset=utf-8' as required.".format(
                    req_reply.rawHeader(b"Content-type")
                )
            )
        res = json.loads(req_reply.content().data().decode("utf-8"))
        return res

    def launch_execution(self, datastore: str, exec_id: str) -> None:
        """
        Launch execution

        Args:
            datastore: (str) datastore id
            exec_id: (str) execution id (see create_processing_execution)
        """
        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req_post = QNetworkRequest(
            QUrl(f"{self.get_base_url(datastore)}/executions/{exec_id}/launch")
        )

        # headers
        req_post.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        # send request
        resp = self.ntwk_requester_blk.post(
            req_post, data=QByteArray(), forceRefresh=True
        )

        # check response
        if resp != QgsBlockingNetworkRequest.NoError:
            raise self.LaunchExecutionException(
                f"Error while launching execution : {self.ntwk_requester_blk.errorMessage()}"
            )

    def get_execution(self, datastore: str, exec_id: str) -> Execution:
        """
        Get execution.

        Args:
            datastore: (str) datastore id
            exec_id: (str) execution id

        Returns: Execution execution if execution available, raise UnavailableExecutionException otherwise
        """
        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req = QNetworkRequest(
            QUrl(f"{self.get_base_url(datastore)}/executions/{exec_id}")
        )

        req_reply = send_qgs_blocking_request(
            self.ntwk_requester_blk, req, self.UnavailableExecutionException
        )
        data = json.loads(req_reply.content().data().decode("utf-8"))

        execution = self._execution_from_json(data)
        return execution

    def get_stored_data_executions(
        self, datastore: str, stored_data: str
    ) -> [Execution]:
        """
        Get stored data execution.

        Args:
            datastore: (str) datastore id
            stored_data: (str) stored data id

        Returns: [Execution] list of execution if stored data available, raise UnavailableExecutionException otherwise
        """
        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req = QNetworkRequest(
            QUrl(
                f"{self.get_base_url(datastore)}/executions/?output_stored_data={stored_data}"
            )
        )

        req_reply = send_qgs_blocking_request(
            self.ntwk_requester_blk, req, self.UnavailableExecutionException
        )
        data = json.loads(req_reply.content().data().decode("utf-8"))
        execution_list = [self._execution_from_json(execution) for execution in data]
        return execution_list

    @staticmethod
    def _execution_from_json(data) -> Execution:
        execution = Execution(
            id=data["_id"], status=data["status"], name=data["processing"]["name"]
        )

        if "creation" in data:
            execution.creation = data["creation"]
        if "launch" in data:
            execution.launch = data["launch"]
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

        req_reply = send_qgs_blocking_request(
            self.ntwk_requester_blk,
            req,
            self.UnavailableExecutionException,
            expected_type="plain/text; charset=utf-8",
        )
        data = req_reply.content().data().decode("utf-8")
        return data
