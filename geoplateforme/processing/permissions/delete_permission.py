# standard

# PyQGIS

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterString,
)
from qgis.PyQt.QtCore import QCoreApplication

# Plugin
from geoplateforme.api.custom_exceptions import DeletePermissionException
from geoplateforme.api.permissions import PermissionRequestManager
from geoplateforme.processing.utils import get_short_string, get_user_manual_url


class DeletePermissionAlgorithm(QgsProcessingAlgorithm):
    DATASTORE_ID = "DATASTORE_ID"
    PERMISSION_ID = "PERMISSION_ID"

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def createInstance(self):
        return DeletePermissionAlgorithm()

    def name(self):
        return "delete_permission"

    def displayName(self):
        return self.tr("Suppression d'une permission")

    def group(self):
        return self.tr("Permissions")

    def groupId(self):
        return "permission"

    def helpUrl(self):
        return get_user_manual_url(self.name())

    def shortHelpString(self):
        return get_short_string(self.name(), self.displayName())

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterString(
                name=self.DATASTORE_ID,
                description=self.tr("Identifiant de l'entrepôt"),
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.PERMISSION_ID,
                description=self.tr("Identifiant de la permission"),
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        permission_id = self.parameterAsString(parameters, self.PERMISSION_ID, context)
        datastore_id = self.parameterAsString(parameters, self.DATASTORE_ID, context)
        try:
            feedback.pushInfo(self.tr("Suppression de la permission"))
            manager = PermissionRequestManager()
            manager.delete(datastore_id=datastore_id, permission_id=permission_id)

        except DeletePermissionException as exc:
            raise QgsProcessingException(
                self.tr("Erreur lors de la suppression de la permission : {}").format(
                    exc
                )
            ) from exc

        return {}
