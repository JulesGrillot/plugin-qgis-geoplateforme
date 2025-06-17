# standard

# PyQGIS

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterString,
)
from qgis.PyQt.QtCore import QCoreApplication

# Plugin
from geoplateforme.api.custom_exceptions import CreateUserKeyException
from geoplateforme.api.user_key import UserKeyRequestManager
from geoplateforme.processing.utils import get_short_string, get_user_manual_url


class CreateAccessesAlgorithm(QgsProcessingAlgorithm):
    KEY_ID = "KEY_ID"
    PERMISSION_ID = "PERMISSION_ID"
    OFFERING_IDS = "OFFERING_IDS"

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def createInstance(self):
        return CreateAccessesAlgorithm()

    def name(self):
        return "create_accesses"

    def displayName(self):
        return self.tr("Création d'acces à une ou des offres d'une permission")

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

        self.addParameter(
            QgsProcessingParameterString(
                name=self.PERMISSION_ID,
                description=self.tr("Identifiant de la permission"),
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                name=self.OFFERING_IDS,
                description=self.tr(
                    "Identifiants des offres. Valeurs séparées par des ,"
                ),
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        key_id = self.parameterAsString(parameters, self.KEY_ID, context)
        permission_id = self.parameterAsString(parameters, self.PERMISSION_ID, context)
        offering_ids_str = self.parameterAsString(
            parameters, self.OFFERING_IDS, context
        )
        offering_ids = offering_ids_str.split(",")

        try:
            feedback.pushInfo(self.tr("Création de l'accès"))
            manager = UserKeyRequestManager()
            manager.create_accesses(
                user_key_id=key_id,
                permission_id=permission_id,
                offering_ids=offering_ids,
            )
            return {}

        except CreateUserKeyException as exc:
            raise QgsProcessingException(
                self.tr("Erreur lors de la création de la clé : {}").format(exc)
            ) from exc
