# standard

# PyQGIS

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterString,
)
from qgis.PyQt.QtCore import QCoreApplication

# Plugin
from geoplateforme.api.custom_exceptions import DeleteUserKeyException
from geoplateforme.api.user_key import UserKeyRequestManager
from geoplateforme.processing.utils import get_short_string, get_user_manual_url


class DeleteUserKeyAlgorithm(QgsProcessingAlgorithm):
    KEY_ID = "KEY_ID"

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def createInstance(self):
        return DeleteUserKeyAlgorithm()

    def name(self):
        return "delete_key"

    def displayName(self):
        return self.tr("Suppression d'une clé utilisateur")

    def group(self):
        return self.tr("Clés")

    def groupId(self):
        return "user_key"

    def helpUrl(self):
        return get_user_manual_url(self.name())

    def shortHelpString(self):
        return get_short_string(self.name(), self.displayName())

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterString(
                name=self.KEY_ID,
                description=self.tr("Identifiant de la clé"),
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        user_key_id = self.parameterAsString(parameters, self.KEY_ID, context)
        try:
            feedback.pushInfo(self.tr("Suppression de la clé"))
            manager = UserKeyRequestManager()
            manager.delete(user_key_id)

        except DeleteUserKeyException as exc:
            raise QgsProcessingException(
                self.tr("Erreur lors de la suppression de la clé : {}").format(exc)
            ) from exc

        return {}
