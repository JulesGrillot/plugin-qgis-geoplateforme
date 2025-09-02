# standard

# PyQGIS

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterString,
)
from qgis.PyQt.QtCore import QCoreApplication

# Plugin
from geoplateforme.api.custom_exceptions import DeleteUserKeyAccessesException
from geoplateforme.api.key_access import KeyAccessRequestManager
from geoplateforme.processing.utils import get_short_string, get_user_manual_url


class DeleteUserKeyAccessesAlgorithm(QgsProcessingAlgorithm):
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
        return DeleteUserKeyAccessesAlgorithm()

    def name(self):
        return "delete_user_key_accesses"

    def displayName(self):
        return self.tr("Suppression des accès associés à une clé utilisateur")

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
        key_id = self.parameterAsString(parameters, self.KEY_ID, context)

        try:
            feedback.pushInfo(
                self.tr("Suppression des accès associés à une clé utilisateur")
            )
            manager = KeyAccessRequestManager()
            manager.delete_user_key_accesses(
                user_key_id=key_id,
            )
            return {}

        except DeleteUserKeyAccessesException as exc:
            raise QgsProcessingException(
                self.tr(
                    "Erreur lors de la suppression des accès associés à une clé utilisateur : {}"
                ).format(exc)
            ) from exc
