#! python3  # noqa: E265

"""
    Perform network request.
"""

# ############################################################################
# ########## Imports ###############
# ##################################

# Standard library
import logging

# PyQGIS
from qgis.core import QgsApplication, QgsAuthMethodConfig, QgsBlockingNetworkRequest
from qgis.PyQt.Qt import QByteArray, QUrl
from qgis.PyQt.QtCore import QByteArray, QCoreApplication
from qgis.PyQt.QtNetwork import QNetworkRequest

# project
from vectiler.toolbelt.log_handler import PlgLogger
from vectiler.toolbelt.preferences import PlgOptionsManager

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)

# ############################################################################
# ########## Classes ###############
# ##################################


class NetworkRequestsManager:
    """Helper on network operations.

    :param tr: method to translate
    :type tr: func
    """

    def __init__(self):
        """Initialization."""
        self.log = PlgLogger().log
        self.ntwk_requester_blk = QgsBlockingNetworkRequest()
        self.plg_settings = PlgOptionsManager.get_plg_settings()

    def test_url(self, url: str, method: str = "head") -> bool:
        """Test if URL is reachable. First, try a HEAD then a GET.

        :param url: URL to test.
        :type url: str
        :param method: _description_, defaults to "head"
        :type method: str, optional

        :return: True if URL is reachable.
        :rtype: bool
        """
        try:
            req = QNetworkRequest(QUrl(url))
            self.ntwk_requester_blk.head(req)
            return True
        except Exception:
            if method == "head":
                return self.test_url(url=url, method="get")
            return False

    def get_user_info(self) -> QByteArray:
        """Get user info as json.

        :raises TypeError: if response mime-type is not valid

        :return: user info in bytes or error string in case of request error
        :rtype: QByteArray
        """
        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        req_get = QNetworkRequest(QUrl(f"{self.plg_settings.url_api_entrepot}api/v1/users/me"))
        resp = self.ntwk_requester_blk.get(req_get, forceRefresh=True)

        # check response
        if resp != QgsBlockingNetworkRequest.NoError:
            self.log(
                f"Error while getting user informations: {self.ntwk_requester_blk.errorMessage()}",
                log_level=2,
                push=True,
            )
            return self.ntwk_requester_blk.errorMessage()
        # check response type
        req_reply = self.ntwk_requester_blk.reply()
        if not req_reply.rawHeader(b"Content-Type") == "application/json; charset=utf-8":
            raise TypeError(
                "Response mime-type is '{}' not 'application/json; charset=utf-8' as required.".format(
                    req_reply.rawHeader(b"Content-type")
                )
            )
        return req_reply.content()

    def get_api_token(self) -> QByteArray:
        """Get API token.

        :raises TypeError: if response mime-type is not valid

        :return: token in bytes
        :rtype: QByteArray
        """
        # request URL
        qreq = QNetworkRequest(QUrl(self.plg_settings.url_authentication_token))

        # auth
        self.ntwk_requester_blk.setAuthCfg(self.plg_settings.qgis_auth_id)
        auth_manager = QgsApplication.authManager()
        conf = QgsAuthMethodConfig()
        auth_manager.loadAuthenticationConfig(
            self.plg_settings.qgis_auth_id, conf, True
        )
        if conf.id():
            username = conf.config("username", "")
            password = conf.config("password", "")

        # headers
        qreq.setHeader(
            QNetworkRequest.ContentTypeHeader, "application/x-www-form-urlencoded"
        )

        # encode data
        data = QByteArray()
        data.append(
            f"grant_type=password&"
            f"client_id={self.plg_settings.auth_client_id}&"
            f"username={username}&"
            f"password={password}"
        )

        # send request
        resp = self.ntwk_requester_blk.post(qreq, data=data, forceRefresh=True)

        # check response
        if resp != QgsBlockingNetworkRequest.NoError:
            self.log(
                f"Error while getting token: {self.ntwk_requester_blk.errorMessage()}",
                log_level=2,
                push=True,
            )
            return self.ntwk_requester_blk.errorMessage()

        # debug log
        self.log(
            message=f"Token request to {self.plg_settings.url_authentication_token} succeeded.",
            log_level=3,
            push=0,
        )

        # check response type
        req_reply = self.ntwk_requester_blk.reply()
        if not req_reply.rawHeader(b"Content-Type") == "application/json":
            raise TypeError(
                "Response mime-type is '{}' not 'application/json' as required.".format(
                    req_reply.rawHeader(b"Content-type")
                )
            )
        self.log("Token received", log_level=4)
        return req_reply.content()

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)
