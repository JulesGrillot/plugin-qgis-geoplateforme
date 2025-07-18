# standard

from qgis.core import (
    QgsApplication,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingParameterString,
)
from qgis.PyQt.QtCore import QCoreApplication

# Plugin
from geoplateforme.api.configuration import ConfigurationRequestManager
from geoplateforme.api.custom_exceptions import (
    ReadConfigurationException,
    UpdateConfigurationException,
)
from geoplateforme.processing.annexes.delete_annexe import DeleteAnnexeAlgorithm
from geoplateforme.processing.utils import get_short_string, get_user_manual_url

# PyQGIS


class DeleteConfigurationStyleAlgorithm(QgsProcessingAlgorithm):
    DATASTORE_ID = "DATASTORE_ID"
    CONFIGURATION_ID = "CONFIGURATION_ID"
    STYLE_NAME = "STYLE_NAME"

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def createInstance(self):
        return DeleteConfigurationStyleAlgorithm()

    def name(self):
        return "delete_configuration_style"

    def displayName(self):
        return self.tr("Suppression d'un style pour une configuration")

    def group(self):
        return self.tr("Styles")

    def groupId(self):
        return "styles"

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
                name=self.CONFIGURATION_ID,
                description=self.tr("Identifiant de la configuration"),
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.STYLE_NAME,
                self.tr("Nom du style"),
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        datastore_id = self.parameterAsString(parameters, self.DATASTORE_ID, context)
        config_id = self.parameterAsString(parameters, self.CONFIGURATION_ID, context)
        style_name = self.parameterAsString(parameters, self.STYLE_NAME, context)

        # Get configuration
        feedback.pushInfo(self.tr("Récupération de la configuration"))
        config_manager = ConfigurationRequestManager()
        try:
            config = config_manager.get_configuration(
                datastore=datastore_id, configuration=config_id
            )
        except ReadConfigurationException as exc:
            raise QgsProcessingException(
                f"Erreur lors de la lecture de la configuration : {exc}"
            ) from exc

        # Define new extra for configuration
        feedback.pushInfo(self.tr("Récupération styles à supprimer"))

        if config.extra:
            config_extra = config.extra
        else:
            config_extra = {}
        config_styles = []
        if "styles" in config_extra:
            config_styles = config_extra["styles"]

        annexes_to_delete = []
        new_config_styles = []
        for style in config_styles:
            if style["name"] != style_name:
                new_config_styles.append(style)
            else:
                for layer in style["layers"]:
                    annexes_to_delete.append(layer["annexe_id"])

        # Update configuration
        feedback.pushInfo(self.tr("Mise à jour de la configuration"))
        config_extra["styles"] = new_config_styles

        try:
            config_manager.update_extra_and_name(
                datastore_id=datastore_id,
                configuration_id=config_id,
                extra=config_extra,
            )
        except UpdateConfigurationException as exc:
            raise QgsProcessingException(
                f"Erreur lors de la mise à jour de la configuration : {exc}"
            ) from exc

        feedback.pushInfo(self.tr("Suppression des annexes associées"))
        for annexe_id in annexes_to_delete:
            self._delete_annexe(
                datastore_id=datastore_id,
                annexe_id=annexe_id,
                context=context,
                feedback=feedback,
            )

        return {}

    def _delete_annexe(
        self,
        datastore_id: str,
        annexe_id: str,
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ) -> None:
        """Delete annexe

        :param datastore_id: datastore id
        :type datastore_id: str
        :param annexe_id: annexe id
        :type annexe_id: str
        :param context: context
        :type context: QgsProcessingContext
        :param feedback: feedbakc
        :type feedback: QgsProcessingFeedback
        :raises QgsProcessingException: error when annexe creation fail
        :return: created annexe id
        :rtype: str
        """
        algo_str = f"geoplateforme:{DeleteAnnexeAlgorithm().name()}"
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)
        params = {
            DeleteAnnexeAlgorithm.DATASTORE_ID: datastore_id,
            DeleteAnnexeAlgorithm.ANNEXE_ID: annexe_id,
        }
        _, successful = alg.run(params, context, feedback)
        if not successful:
            raise QgsProcessingException(
                self.tr("Erreur lors de la création de l'annexe")
            )
