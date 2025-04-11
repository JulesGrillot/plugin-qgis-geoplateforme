import json
import tempfile

from qgis.core import (
    QgsApplication,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingParameterFile,
)
from qgis.PyQt.QtCore import QCoreApplication

from geoplateforme.processing.upload_creation import UploadCreationAlgorithm
from geoplateforme.processing.upload_database_integration import (
    UploadDatabaseIntegrationAlgorithm,
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
    INPUT_JSON = "INPUT_JSON"

    DATASTORE = "datastore"
    NAME = "name"
    FILES = "files"
    SRS = "srs"

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
        return self.tr("Create vector database")

    def group(self):
        return self.tr("")

    def groupId(self):
        return ""

    def helpUrl(self):
        return ""

    def shortHelpString(self):
        return self.tr(
            "Create vector db stored data in geotuileur platform.\n"
            "Input parameters are defined in a .json file.\n"
            "Available parameters:\n"
            "{\n"
            f'    "{self.DATASTORE}": datastore id (str),\n'
            f'    "{self.NAME}": wanted stored data name (str),\n'
            f'    "{self.FILES}": upload full file path list [str],\n'
            f'    "{self.SRS}": upload SRS (str) must be in IGNF or EPSG repository,\n'
            "}\n"
            f"Returns :"
            f"   - created upload id in {self.CREATED_UPLOAD_ID} results "
            f"   - created stored data id in {self.CREATED_STORED_DATA_ID} results"
        )

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                name=self.INPUT_JSON,
                description=self.tr("Input .json file"),
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        filename = self.parameterAsFile(parameters, self.INPUT_JSON, context)

        with open(filename, "r") as file:
            data = json.load(file)

            name = data[self.NAME]
            files = data[self.FILES]
            srs = data[self.SRS]
            datastore = data[self.DATASTORE]

            # Create upload
            upload_id = self._create_upload(
                datastore, files, name, srs, context, feedback
            )

            # Run database integration
            vector_db_stored_data_id = self._database_integration(
                name, datastore, upload_id, context, feedback
            )

        return {
            self.CREATED_UPLOAD_ID: upload_id,
            self.CREATED_STORED_DATA_ID: vector_db_stored_data_id,
        }

    def _create_upload(
        self,
        datastore: str,
        files: [str],
        name: str,
        srs: str,
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ) -> str:
        """

        Args:
            datastore : (str) datastore id
            files: [str] full file path list
            name: (str) upload name
            srs: (str) upload srs
            context: QgsProcessingContext
            feedback: QgsProcessingFeedback

        Returns: (str) created upload id

        """
        algo_str = f"geotuileur:{UploadCreationAlgorithm().name()}"
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)
        data = {
            UploadCreationAlgorithm.DATASTORE: datastore,
            UploadCreationAlgorithm.NAME: name,
            UploadCreationAlgorithm.DESCRIPTION: name,
            UploadCreationAlgorithm.SRS: srs,
            UploadCreationAlgorithm.FILES: files,
        }
        filename = tempfile.NamedTemporaryFile(suffix=".json").name
        with open(filename, "w") as file:
            json.dump(data, file)
        params = {UploadCreationAlgorithm.INPUT_JSON: filename}
        results, successful = alg.run(params, context, feedback)
        if successful:
            created_upload_id = results[UploadCreationAlgorithm.CREATED_UPLOAD_ID]
        else:
            raise QgsProcessingException(self.tr("Upload creation failed"))
        return created_upload_id

    def _database_integration(
        self,
        name: str,
        datastore: str,
        upload_id: str,
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ) -> str:
        """
        Launch database integration for an upload

        Args:
            name: (str) stored data name
            datastore : (str) datastore id
            upload_id:  (str) upload id
            context: QgsProcessingContext
            feedback: QgsProcessingFeedback

        Returns: (str) created vector db stored data id

        """
        algo_str = f"geotuileur:{UploadDatabaseIntegrationAlgorithm().name()}"
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)
        data = {
            UploadDatabaseIntegrationAlgorithm.DATASTORE: datastore,
            UploadDatabaseIntegrationAlgorithm.UPLOAD: upload_id,
            UploadDatabaseIntegrationAlgorithm.STORED_DATA_NAME: name,
        }
        filename = tempfile.NamedTemporaryFile(suffix=".json").name
        with open(filename, "w") as file:
            json.dump(data, file)
        params = {UploadDatabaseIntegrationAlgorithm.INPUT_JSON: filename}
        results, successful = alg.run(params, context, feedback)
        if successful:
            vector_db_stored_data_id = results[
                UploadDatabaseIntegrationAlgorithm.CREATED_STORED_DATA_ID
            ]
        else:
            raise QgsProcessingException(self.tr("Upload database integration failed"))
        return vector_db_stored_data_id
