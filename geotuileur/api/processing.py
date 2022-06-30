import json
from dataclasses import dataclass

from qgis.core import QgsBlockingNetworkRequest
from qgis.PyQt.QtCore import QByteArray, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

from geotuileur.api.execution import Execution
from geotuileur.toolbelt import PlgLogger, PlgOptionsManager


@dataclass
class Processing:
    name: str
    id: str


class ProcessingRequestManager:
    class UnavailableProcessingException(Exception):
        pass

    class UnavailableExecutionException(Exception):
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

        # headers
        req.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        # send request
        resp = self.ntwk_requester_blk.get(req, forceRefresh=True)

        # check response
        if resp != QgsBlockingNetworkRequest.NoError:
            raise self.UnavailableProcessingException(
                f"Error while fetching processing : {self.ntwk_requester_blk.errorMessage()}"
            )

        # check response
        req_reply = self.ntwk_requester_blk.reply()
        if (
            not req_reply.rawHeader(b"Content-Type")
            == "application/json; charset=utf-8"
        ):
            raise self.UnavailableProcessingException(
                "Response mime-type is '{}' not 'application/json; charset=utf-8' as required.".format(
                    req_reply.rawHeader(b"Content-type")
                )
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

        # headers
        req.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        # send request
        resp = self.ntwk_requester_blk.get(req, forceRefresh=True)

        # check response
        if resp != QgsBlockingNetworkRequest.NoError:
            raise self.UnavailableExecutionException(
                f"Error while fetching execution : {self.ntwk_requester_blk.errorMessage()}"
            )

        # check response
        req_reply = self.ntwk_requester_blk.reply()
        if (
            not req_reply.rawHeader(b"Content-Type")
            == "application/json; charset=utf-8"
        ):
            raise self.UnavailableExecutionException(
                "Response mime-type is '{}' not 'application/json; charset=utf-8' as required.".format(
                    req_reply.rawHeader(b"Content-type")
                )
            )

        data = json.loads(req_reply.content().data().decode("utf-8"))

        execution = Execution(
            id=data["_id"], status=data["status"], name=data["processing"]["name"]
        )

        if "start" in data:
            execution.start = data["start"]
        if "finish" in data:
            execution.finish = data["finish"]
        return execution
