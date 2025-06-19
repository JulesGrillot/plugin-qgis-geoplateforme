# standard

# PyQGIS

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterString,
)
from qgis.PyQt.QtCore import QCoreApplication

# Plugin
from geoplateforme.api.custom_exceptions import UpdateUserKeyException
from geoplateforme.api.user_key import UserKeyRequestManager
from geoplateforme.processing.utils import get_short_string, get_user_manual_url


class UpdateKeyAlgorithm(QgsProcessingAlgorithm):
    KEY_ID = "KEY_ID"
    NAME = "NAME"
    WHITELIST = "WHITELIST"
    BLACKLIST = "BLACKLIST"
    USER_AGENT = "USER_AGENT"
    REFERER = "REFERER"

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def createInstance(self):
        return UpdateKeyAlgorithm()

    def name(self):
        return "update_key"

    def displayName(self):
        return self.tr("Mise à jour d'une clé")

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
                name=self.NAME,
                description=self.tr("Nom de la clé"),
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                name=self.WHITELIST,
                description=self.tr("Adresses IP authorisées. Valeurs séparées par ,"),
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                name=self.BLACKLIST,
                description=self.tr(
                    "Adresses IP non authorisées. Valeurs séparées par ,"
                ),
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                name=self.USER_AGENT,
                description=self.tr("User-agent"),
                optional=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.REFERER,
                description=self.tr("Referer"),
                optional=True,
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        user_key_id = self.parameterAsString(parameters, self.KEY_ID, context)
        name = self.parameterAsString(parameters, self.NAME, context)
        whitelist_str = self.parameterAsString(parameters, self.WHITELIST, context)
        if whitelist_str:
            whitelist = whitelist_str.split(",")
        else:
            whitelist = []

        blacklist_str = self.parameterAsString(parameters, self.BLACKLIST, context)
        if blacklist_str:
            blacklist = blacklist_str.split(",")
        else:
            blacklist = []

        user_agent = self.parameterAsString(parameters, self.USER_AGENT, context)
        referer = self.parameterAsString(parameters, self.REFERER, context)

        try:
            feedback.pushInfo(self.tr("Modification de la clé"))
            manager = UserKeyRequestManager()
            manager.update_user_key(
                user_key_id=user_key_id,
                name=name,
                whitelist=whitelist,
                blacklist=blacklist,
                user_agent=user_agent if user_agent else None,
                referer=referer if referer else None,
            )
            return {}

        except UpdateUserKeyException as exc:
            raise QgsProcessingException(
                self.tr("Erreur lors de la modification de la clé : {}").format(exc)
            ) from exc

        return {}
