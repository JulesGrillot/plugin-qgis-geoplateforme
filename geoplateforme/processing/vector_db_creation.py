from typing import List, Tuple

from qgis.core import (
    Qgis,
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingParameterCrs,
    QgsProcessingParameterFile,
    QgsProcessingParameterMatrix,
    QgsProcessingParameterMultipleLayers,
    QgsProcessingParameterString,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QCoreApplication

from geoplateforme.processing.upload_database_integration import (
    UploadDatabaseIntegrationAlgorithm,
)
from geoplateforme.processing.upload_from_layers import GpfUploadFromLayersAlgorithm
from geoplateforme.processing.utils import (
    get_short_string,
    get_user_manual_url,
    tags_from_qgs_parameter_matrix_string,
    tags_to_qgs_parameter_matrix_string,
)


class VectorDatabaseCreationProcessingFeedback(QgsProcessingFeedback):
    """
    Implementation of QgsProcessingFeedback to store information from processing:
        - created_upload_id (str) : created upload id
        - created_vector_db_id (str) : created vector db stored data id
    """

    created_upload_id: str = ""
    created_vector_db_id: str = ""


class VectorDatabaseCreationAlgorithm(QgsProcessingAlgorithm):
    DATASTORE = "DATASTORE"
    NAME = "NAME"
    LAYERS = "LAYERS"
    FILES = "FILES"
    SRS = "SRS"
    TAGS = "TAGS"

    PROCESSING_EXEC_ID = "PROCESSING_EXEC_ID"
    CREATED_UPLOAD_ID = "CREATED_UPLOAD_ID"
    CREATED_STORED_DATA_ID = "CREATED_STORED_DATA_ID"

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def createInstance(self):
        return VectorDatabaseCreationAlgorithm()

    def name(self):
        return "vector_db_creation"

    def displayName(self):
        return self.tr(
            "Création d'une base de données vectorielle depuis des couches vectorielles"
        )

    def group(self):
        return self.tr("")

    def groupId(self):
        return ""

    def helpUrl(self):
        return get_user_manual_url(self.name())

    def shortHelpString(self):
        return get_short_string(self.name(), self.displayName())

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterString(
                name=self.DATASTORE,
                description=self.tr("Identifiant de l'entrepôt"),
            )
        )

        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                name=self.LAYERS,
                description=self.tr("Couches vectorielles à livrer"),
                layerType=Qgis.ProcessingSourceType.VectorAnyGeometry,
            )
        )

        self.addParameter(
            QgsProcessingParameterFile(
                name=self.FILES,
                description=self.tr(
                    "Fichiers additionnels à importer (séparés par ; pour fichiers multiples)"
                ),
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.NAME,
                description=self.tr("Nom de la livraison"),
            )
        )

        self.addParameter(
            QgsProcessingParameterCrs(self.SRS, self.tr("Système de coordonnées"))
        )

        self.addParameter(
            QgsProcessingParameterMatrix(
                name=self.TAGS,
                description=self.tr("Tags"),
                headers=[self.tr("Tag"), self.tr("Valeur")],
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        name = self.parameterAsString(parameters, self.NAME, context)
        datastore = self.parameterAsString(parameters, self.DATASTORE, context)

        layers = self.parameterAsLayerList(parameters, self.LAYERS, context)
        files = self.parameterAsString(parameters, self.FILES, context)
        tag_data = self.parameterAsMatrix(parameters, self.TAGS, context)
        tags = tags_from_qgs_parameter_matrix_string(tag_data)
        srs: QgsCoordinateReferenceSystem = self.parameterAsCrs(
            parameters, self.SRS, context
        )

        # Create upload
        upload_id = self._create_upload(
            datastore,
            layers,
            files,
            name,
            srs,
            tags,
            context,
            feedback,
        )

        # Run database integration
        vector_db_stored_data_id, exec_id = self._database_integration(
            name,
            datastore,
            upload_id,
            tags,
            context,
            feedback,
        )

        return {
            self.CREATED_UPLOAD_ID: upload_id,
            self.CREATED_STORED_DATA_ID: vector_db_stored_data_id,
            self.PROCESSING_EXEC_ID: exec_id,
        }

    def _create_upload(
        self,
        datastore: str,
        layers: List[QgsVectorLayer],
        files: List[str],
        name: str,
        srs: QgsCoordinateReferenceSystem,
        tags: dict[str, str],
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ) -> str:
        """Create upload for a list of files and layers

        :param datastore: datastore id
        :type datastore: str
        :param layers: QgsVectorLayer to be integrated
        :type layers: List[QgsVectorLayer]
        :param files: full file path list
        :type files: List[str]
        :param name: upload name
        :type name: str
        :param srs: srs
        :type srs: dict[str, str]
        :param tags: tags
        :type tags: dict[str, str]
        :param context: context of processing
        :type context: QgsProcessingContext
        :param feedback: feedback for processing
        :type feedback: QgsProcessingFeedback
        :raises QgsProcessingException: propagate error in case of upload creation exception
        :return: id of created upload
        :rtype: str
        """
        algo_str = f"geoplateforme:{GpfUploadFromLayersAlgorithm().name()}"
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)
        params = {
            GpfUploadFromLayersAlgorithm.DATASTORE: datastore,
            GpfUploadFromLayersAlgorithm.NAME: name,
            GpfUploadFromLayersAlgorithm.DESCRIPTION: name,
            GpfUploadFromLayersAlgorithm.LAYERS: layers,
            GpfUploadFromLayersAlgorithm.FILES: files,
            GpfUploadFromLayersAlgorithm.SRS: srs,
            GpfUploadFromLayersAlgorithm.TAGS: tags_to_qgs_parameter_matrix_string(
                tags
            ),
            GpfUploadFromLayersAlgorithm.WAIT_FOR_CLOSE: True,
        }

        results, successful = alg.run(params, context, feedback)
        if successful:
            created_upload_id = results[GpfUploadFromLayersAlgorithm.CREATED_UPLOAD_ID]
        else:
            raise QgsProcessingException(self.tr("Upload creation failed"))
        return created_upload_id

    def _database_integration(
        self,
        name: str,
        datastore: str,
        upload_id: str,
        tags: dict[str, str],
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ) -> Tuple[str, str]:
        """Launch database integration for an upload

        :param name: stored data name
        :type name: str
        :param datastore: datastore id
        :type datastore: str
        :param upload_id: upload id
        :type upload_id: str
        :param tags: tags
        :type tags: dict[str, str]
        :param context: context of processing
        :type context: QgsProcessingContext
        :param feedback: feedback for processing
        :type feedback: QgsProcessingFeedback
        :raises QgsProcessingException: an error occured when creating the database
        :return: created stored data id, processing execution id used for creation
        :rtype: Tuple[str, str]
        """

        algo_str = f"geoplateforme:{UploadDatabaseIntegrationAlgorithm().name()}"
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)
        params = {
            UploadDatabaseIntegrationAlgorithm.DATASTORE: datastore,
            UploadDatabaseIntegrationAlgorithm.UPLOAD: upload_id,
            UploadDatabaseIntegrationAlgorithm.STORED_DATA_NAME: name,
            UploadDatabaseIntegrationAlgorithm.TAGS: tags_to_qgs_parameter_matrix_string(
                tags
            ),
            UploadDatabaseIntegrationAlgorithm.WAIT_FOR_INTEGRATION: True,
        }
        results, successful = alg.run(params, context, feedback)
        if successful:
            vector_db_stored_data_id = results[
                UploadDatabaseIntegrationAlgorithm.CREATED_STORED_DATA_ID
            ]
            exec_id = results[UploadDatabaseIntegrationAlgorithm.PROCESSING_EXEC_ID]
        else:
            raise QgsProcessingException(self.tr("Upload database integration failed"))
        return vector_db_stored_data_id, exec_id
