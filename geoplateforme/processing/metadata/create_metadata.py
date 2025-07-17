# standard

# PyQGIS

from pathlib import Path

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingOutputString,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFile,
    QgsProcessingParameterString,
)
from qgis.PyQt.QtCore import QCoreApplication

# Plugin
from geoplateforme.api.custom_exceptions import MetadataFileUploadException
from geoplateforme.api.metadata import MetadataRequestManager, MetadataType
from geoplateforme.processing.utils import get_short_string, get_user_manual_url


class CreateMetadataAlgorithm(QgsProcessingAlgorithm):
    DATASTORE_ID = "DATASTORE_ID"
    FILE_PATH = "FILE_PATH"
    OPEN_DATA = "OPEN_DATA"
    METADATA_TYPE = "TYPE"

    METADATA_TYPE_ENUM = ["ISOAP", "INSPIRE"]

    CREATED_METADATA_ID = "CREATED_METADATA_ID"

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def createInstance(self):
        return CreateMetadataAlgorithm()

    def name(self):
        return "create_metadata"

    def displayName(self):
        return self.tr("Création d'une annexe dans l'entrepôt")

    def group(self):
        return self.tr("Metadata")

    def groupId(self):
        return "metadata"

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
            QgsProcessingParameterFile(
                self.FILE_PATH,
                self.tr("Fichier de métadonnées"),
                fileFilter="Fichier de métadonnées (*.xml)",
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.OPEN_DATA,
                description=self.tr("Métadonnée open data ?"),
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                name=self.METADATA_TYPE,
                description=self.tr("Type de métadonnée"),
                options=self.METADATA_TYPE_ENUM,
            )
        )

        self.addOutput(
            QgsProcessingOutputString(
                name=self.CREATED_METADATA_ID,
                description=self.tr("Identifiant de l'annexe créée."),
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        datastore = self.parameterAsString(parameters, self.DATASTORE_ID, context)
        metadata_type = self.parameterAsString(parameters, self.METADATA_TYPE, context)
        open_data = self.parameterAsBool(parameters, self.OPEN_DATA, context)
        file_path = self.parameterAsFile(parameters, self.FILE_PATH, context)

        try:
            manager = MetadataRequestManager()
            metadata = manager.create_metadata(
                datastore_id=datastore,
                file_path=Path(file_path),
                open_data=open_data,
                metadata_type=MetadataType(metadata_type),
            )

        except MetadataFileUploadException as exc:
            raise QgsProcessingException(
                f"Erreur lors de la création d'une métadonnée : {exc}"
            )

        return {
            self.CREATED_METADATA_ID: metadata._id,
        }
