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
from qgis.PyQt.QtCore import QByteArray, QCoreApplication, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

# project
from geoplateforme.toolbelt.log_handler import PlgLogger
from geoplateforme.toolbelt.preferences import PlgOptionsManager

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

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)
