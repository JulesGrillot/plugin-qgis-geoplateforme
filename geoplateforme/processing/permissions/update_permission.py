# standard

# PyQGIS

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterDateTime,
    QgsProcessingParameterString,
)
from qgis.PyQt.QtCore import QCoreApplication

# Plugin
from geoplateforme.api.permissions import PermissionRequestManager
from geoplateforme.processing.utils import get_short_string, get_user_manual_url


class UpdatePermissionAlgorithm(QgsProcessingAlgorithm):
    DATASTORE_ID = "DATASTORE_ID"
    PERMISSION_ID = "PERMISSION_ID"
    LICENCE = "LICENCE"
    OFFERINGS = "OFFERINGS"
    END_DATE = "END_DATE"

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def createInstance(self):
        return UpdatePermissionAlgorithm()

    def name(self):
        return "update_permission"

    def displayName(self):
        return self.tr("Mise à jour d'une permission")

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

        self.addParameter(
            QgsProcessingParameterString(
                name=self.LICENCE,
                description=self.tr("Nom de la permission"),
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                name=self.OFFERINGS,
                description=self.tr(
                    "Identifiants des offres. Valeurs séparées par des virgules (,)"
                ),
            )
        )
        self.addParameter(
            QgsProcessingParameterDateTime(
                name=self.END_DATE,
                description=self.tr("Date de fin de la permission"),
                optional=True,
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        permission_id = self.parameterAsString(parameters, self.PERMISSION_ID, context)
        datastore_id = self.parameterAsString(parameters, self.DATASTORE_ID, context)
        license_ = self.parameterAsString(parameters, self.LICENCE, context)

        offerring_str = self.parameterAsString(parameters, self.OFFERINGS, context)
        offerings = offerring_str.split(",")

        end_date = self.parameterAsDateTime(parameters, self.END_DATE, context)
        if not end_date.isNull():
            end_date = end_date.toUTC().toPyDateTime()
        else:
            end_date = None

        try:
            feedback.pushInfo(self.tr("Modification de la permission"))
            manager = PermissionRequestManager()
            manager.update_permission(
                permission_id=permission_id,
                datastore_id=datastore_id,
                licence=license_,
                offerings=offerings,
                end_date=end_date,
            )
            return {}

        except UpdatePermissionAlgorithm as exc:
            raise QgsProcessingException(
                self.tr("Erreur lors de la modification de la permission : {}").format(
                    exc
                )
            ) from exc

        return {}
