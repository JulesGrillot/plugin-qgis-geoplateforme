#! python3  # noqa: E265

"""
    Processing provider module.
"""

# PyQGIS
from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon

# project
from geotuileur.__about__ import DIR_PLUGIN_ROOT, __title__, __version__
from geotuileur.processing.check_layer import CheckLayerAlgorithm
from geotuileur.processing.tile_creation import TileCreationAlgorithm
from geotuileur.processing.upload_creation import UploadCreationAlgorithm
from geotuileur.processing.upload_database_integration import (
    UploadDatabaseIntegrationAlgorithm,
)
from geotuileur.processing.upload_publication import UploadPublicationAlgorithm

# ############################################################################
# ########## Classes ###############
# ##################################


class GeotuileurProvider(QgsProcessingProvider):
    """
    Processing provider class.
    """

    def loadAlgorithms(self):
        """Loads all algorithms belonging to this provider."""
        self.addAlgorithm(CheckLayerAlgorithm())
        self.addAlgorithm(UploadCreationAlgorithm())
        self.addAlgorithm(UploadDatabaseIntegrationAlgorithm())
        self.addAlgorithm(TileCreationAlgorithm())
        self.addAlgorithm(UploadPublicationAlgorithm())

    def id(self) -> str:
        """Unique provider id, used for identifying it. This string should be unique, \
        short, character only string, eg "qgis" or "gdal". \
        This string should not be localised.

        :return: provider ID
        :rtype: str
        """
        return "geotuileur"

    def name(self) -> str:
        """Returns the provider name, which is used to describe the provider
        within the GUI. This string should be short (e.g. "Lastools") and localised.

        :return: provider name
        :rtype: str
        """
        return __title__

    def longName(self) -> str:
        """Longer version of the provider name, which can include
        extra details such as version numbers. E.g. "Lastools LIDAR tools". This string should be localised. The default
        implementation returns the same string as name().

        :return: provider long name
        :rtype: str
        """
        return self.tr("Geotuileur - Tools")

    def icon(self) -> QIcon:
        """QIcon used for your provider inside the Processing toolbox menu.

        :return: provider icon
        :rtype: QIcon
        """
        return QIcon(str(DIR_PLUGIN_ROOT / "resources/images/default_icon.png"))

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def versionInfo(self) -> str:
        """Version information for the provider, or an empty string if this is not \
        applicable (e.g. for inbuilt Processing providers). For plugin based providers, \
        this should return the plugin’s version identifier.

        :return: version
        :rtype: str
        """
        return __version__
