import json
import logging
from dataclasses import dataclass
from enum import Enum
from typing import List

import requests
from qgis.core import QgsApplication, QgsBlockingNetworkRequest, QgsSettings
from qgis.PyQt.QtCore import QByteArray, QEventLoop, QFile, QIODevice, QUrl
from qgis.PyQt.QtNetwork import (
    QHttpMultiPart,
    QHttpPart,
    QNetworkAccessManager,
    QNetworkRequest,
)

from geotuileur.api.check import CheckExecution, CheckRequestManager
from geotuileur.api.client import NetworkRequestsManager
from geotuileur.api.utils import qgs_blocking_get_request
from geotuileur.toolbelt import PlgLogger, PlgOptionsManager

logger = logging.getLogger(__name__)


class UploadStatus(Enum):
    CREATED = "CREATED"
    GENERATING = "GENERATING"
    UNSTABLE = "UNSTABLE"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CHECKING = "CHECKING"
    MODIFYING = "MODIFYING"
    DELETED = "DELETED"


@dataclass
class Upload:
    id: str
    datastore_id: str
    name: str
    description: str
    srs: str
    status: str
    size: int = 0
    tags: dict = None


class UploadRequestManager:
    class UnavailableUploadException(Exception):
        pass

    class UploadCreationException(Exception):
        pass

    class UploadClosingException(Exception):
        pass

    class FileUploadException(Exception):
        pass

    class UnavailableUploadFileTreeException(Exception):
        pass

    def __init__(self):
        """
        Helper for upload request

        """
        self.log = PlgLogger().log
        self.request_manager = NetworkRequestsManager()
        self.ntwk_requester_blk = QgsBlockingNetworkRequest()
        self.plg_settings = PlgOptionsManager.get_plg_settings()

    def get_base_url(self, datastore: str) -> str:
        """
        Get base url for uploads for a datastore

        Args:
            datastore: (str) datastore id

        Returns: url for uploads

        """
        return (
            f"{self.plg_settings.base_url_api_entrepot}/datastores/{datastore}/uploads"
        )

    def get_upload_status(self, datastore: str, upload: str) -> str:
        """
        Get upload status.

        Args:
            datastore: (str) datastore id
            upload: (str) upload id

        Returns: (str) Upload status if upload available, raise UnavailableUploadException otherwise

        """
        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req = QNetworkRequest(QUrl(f"{self.get_base_url(datastore)}/{upload}"))

        # headers
        req.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        # send request
        resp = self.ntwk_requester_blk.get(req, forceRefresh=True)

        # check response
        if resp != QgsBlockingNetworkRequest.NoError:
            raise self.UnavailableUploadException(
                f"Error while fetching upload : {self.ntwk_requester_blk.errorMessage()}"
            )

        # check response
        req_reply = self.ntwk_requester_blk.reply()
        if (
            not req_reply.rawHeader(b"Content-Type")
            == "application/json; charset=utf-8"
        ):
            raise self.UnavailableUploadException(
                "Response mime-type is '{}' not 'application/json; charset=utf-8' as required.".format(
                    req_reply.rawHeader(b"Content-type")
                )
            )

        data = json.loads(req_reply.content().data().decode("utf-8"))
        return data["status"]

    def get_upload(self, datastore: str, upload: str) -> Upload:
        """
        Get upload.

        Args:
            datastore: (str) datastore id
            upload: (str) upload id

        Returns: (upload) Upload if available, raise UnavailableUploadException otherwise

        """
        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req = QNetworkRequest(QUrl(f"{self.get_base_url(datastore)}/{upload}"))

        req_reply = qgs_blocking_get_request(
            self.ntwk_requester_blk, req, self.UnavailableUploadException
        )
        data = json.loads(req_reply.content().data().decode("utf-8"))
        return self._upload_from_json(data, datastore)

    @staticmethod
    def _upload_from_json(data, datastore: str) -> Upload:
        upload = Upload(
            id=data["_id"],
            datastore_id=datastore,
            name=data["name"],
            description=data["description"],
            srs=data["srs"],
            status=data["status"],
        )
        if "size" in data:
            upload.size = data["size"]
        if "tags" in data:
            upload.tags = data["tags"]
        return upload

    def get_upload_checks_execution(
        self, datastore: str, upload: str
    ) -> List[CheckExecution]:
        """
        Get upload checks execution.

        Args:
            datastore: (str) datastore id
            upload: (str) upload id

        Returns: [Execution] Upload checks execution list if upload available, raise UnavailableUploadException otherwise
        """
        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req = QNetworkRequest(QUrl(f"{self.get_base_url(datastore)}/{upload}/checks"))

        # headers
        req.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        # send request
        resp = self.ntwk_requester_blk.get(req, forceRefresh=True)

        # check response
        if resp != QgsBlockingNetworkRequest.NoError:
            raise self.UnavailableUploadException(
                f"Error while fetching upload : {self.ntwk_requester_blk.errorMessage()}"
            )

        # check response
        req_reply = self.ntwk_requester_blk.reply()
        if (
            not req_reply.rawHeader(b"Content-Type")
            == "application/json; charset=utf-8"
        ):
            raise self.UnavailableUploadException(
                "Response mime-type is '{}' not 'application/json; charset=utf-8' as required.".format(
                    req_reply.rawHeader(b"Content-type")
                )
            )

        data = json.loads(req_reply.content().data().decode("utf-8"))
        exec_list = []

        try:
            check_manager = CheckRequestManager()
            for key, executions in data.items():
                for execution in executions:
                    exec_list.append(
                        check_manager.get_execution(
                            datastore=datastore, exec_id=execution["_id"]
                        )
                    )
        except CheckRequestManager.UnavailableExecutionException as exc:
            raise self.UnavailableUploadException(
                f"Error while fetching upload check execution : {exc}"
            )
        return exec_list

    def create_upload(
        self,
        datastore: str,
        name: str,
        description: str,
        srs: str,
    ) -> Upload:
        """
        Create upload on Geotuileur entrepot

        Args:
            datastore: (str) datastore id
            name: (str) upload name
            description: (str) upload description
            srs: (QgsCoordinateReferenceSystem) upload srs

        Returns: Upload if creation succeeded, raise UploadCreationException otherwise

        """
        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req_post = QNetworkRequest(QUrl(self.get_base_url(datastore)))
        # headers
        req_post.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        # encode data
        data = QByteArray()
        data_map = {
            "description": description,
            "name": name,
            "type": "VECTOR",
            "srs": srs,
        }
        data.append(json.dumps(data_map))

        # send request
        resp = self.ntwk_requester_blk.post(req_post, data=data)

        # check response
        if resp != QgsBlockingNetworkRequest.NoError:
            raise self.UploadCreationException(
                f"Error while creating upload : "
                f"{self.ntwk_requester_blk.errorMessage()}"
            )
        # check response type
        req_reply = self.ntwk_requester_blk.reply()
        if (
            not req_reply.rawHeader(b"Content-Type")
            == "application/json; charset=utf-8"
        ):
            raise self.UploadCreationException(
                "Response mime-type is '{}' not 'application/json; charset=utf-8' as required.".format(
                    req_reply.rawHeader(b"Content-type")
                )
            )

        data = json.loads(req_reply.content().data().decode("utf-8"))
        return self._upload_from_json(data, datastore)

    @staticmethod
    def get_qgis_proxy_params_str() -> str:
        """Gets the proxy params from QGIS settings.
        Returns None if proxy is not enabled in QGIS. Otherwise,
        returns proxy params in a single string"""
        sett = QgsSettings()
        proxyEnabled = sett.value("proxy/proxyEnabled", "")
        proxyType = sett.value("proxy/proxyType", "")
        proxyHost = sett.value("proxy/proxyHost", "")
        proxyPort = sett.value("proxy/proxyPort", "")
        proxyUser = sett.value("proxy/proxyUser", "")
        proxyPassword = sett.value("proxy/proxyPassword", "")
        if proxyEnabled != "true":
            return ""
        if not proxyHost:
            return ""
        proxyStr = proxyHost + ":" + proxyPort
        if proxyUser:
            proxyStr = proxyUser + ":" + proxyPassword + "@" + proxyStr
        if proxyType == "Socks5Proxy":
            proxyStr = "socks5://" + proxyStr
        else:
            proxyStr = "https://" + proxyStr
        return proxyStr

    def add_file_with_requests(
        self, datastore: str, upload: str, filename: str
    ) -> None:
        """
        Add file to upload by using python package requests

        Args:
            datastore: (str) datastore id
            upload: (str) upload id
            filename: (str) file to import
        """

        # Get api token for requests
        with requests.Session() as session:
            # Add proxy params
            proxy_str = self.get_qgis_proxy_params_str()
            if proxy_str:
                session.proxies = {"http": proxy_str, "https": proxy_str}

            check = self.request_manager.get_api_token()
            data = json.loads(check.data().decode("utf-8"))
            session.headers.update({"Authorization": "Bearer " + data["access_token"]})

            # Open file
            with open(filename, "rb") as file:
                if not file:
                    raise self.FileUploadException(f"Can't open {filename}")

                # Define request param
                files = {"filename": (filename, file)}
                url = f"{self.get_base_url(datastore)}/{upload}/data"
                response = session.post(url, verify=False, timeout=300, files=files)

                # Check response
                if not response.ok:
                    if response.content:
                        error = (
                            f"Error when uploading {filename} to {url}. HTTP error : {response.status_code}.\n"
                            f" Response content : {response.text} "
                        )
                    else:
                        error = f"Error when uploading {filename} to {url}. HTTP error : {response.status_code}."
                    raise self.FileUploadException(error)

    def add_file(self, datastore: str, upload: str, filename: str) -> None:
        """
        Add file to upload by using QNetworkAccessManager and QHttpMultiPart

        Args:
            datastore: (str) datastore id
            upload: (str) upload id
            filename: (str) file to import
        """
        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req_post = QNetworkRequest(
            QUrl(f"{self.get_base_url(datastore)}/{upload}/data")
        )

        # Create multipart
        multipart = QHttpMultiPart(QHttpMultiPart.FormDataType)
        filepart = QHttpPart()

        # headers
        filepart.setHeader(
            QNetworkRequest.ContentDispositionHeader,
            f'form-data; name="filename" filename="{filename}"',
        )

        file = QFile(filename)
        file.setParent(
            multipart
        )  # we cannot delete the file now, so delete it with the multiPart
        file.open(QIODevice.ReadOnly)

        filepart.setBodyDevice(file)
        multipart.append(filepart)

        networkManager = QNetworkAccessManager(self.ntwk_requester_blk)
        QgsApplication.authManager().updateNetworkRequest(
            req_post, self.plg_settings.qgis_auth_id
        )
        reply = networkManager.post(req_post, multipart)
        multipart.setParent(reply)

        # Add event loop to wait for reply execution
        loop = QEventLoop()
        reply.finished.connect(loop.quit)
        loop.exec()

        # check response
        if reply.error() != QgsBlockingNetworkRequest.NoError:
            raise self.FileUploadException(reply.errorString())

    def close_upload(self, datastore: str, upload: str) -> None:
        """
        Close upload on Geotuileur entrepot

        Args:
            datastore: (str) datastore id
            upload: (str) upload id
        """
        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req_post = QNetworkRequest(
            QUrl(f"{self.get_base_url(datastore)}/{upload}/close")
        )

        # headers
        req_post.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        # send request
        resp = self.ntwk_requester_blk.post(req_post, data=QByteArray())

        # check response
        if resp != QgsBlockingNetworkRequest.NoError:
            raise self.UploadClosingException({self.ntwk_requester_blk.errorMessage()})

    def get_upload_file_tree(self, datastore: str, upload: str) -> dict:
        """
        Get upload file tree.

        Args:
            datastore: (str) datastore id
            upload: (str) upload id

        Returns: (dict) Upload file tree if available, raise UnavailableUploadFileTreeException otherwise

        """
        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req = QNetworkRequest(QUrl(f"{self.get_base_url(datastore)}/{upload}/tree"))

        req_reply = qgs_blocking_get_request(
            self.ntwk_requester_blk, req, self.UnavailableUploadFileTreeException
        )
        data = json.loads(req_reply.content().data().decode("utf-8"))
        return data
