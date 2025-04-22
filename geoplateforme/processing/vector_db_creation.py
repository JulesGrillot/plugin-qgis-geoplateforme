import json
import tempfile
from typing import Tuple

from qgis.core import (
    QgsApplication,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingParameterFile,
)
from qgis.PyQt.QtCore import QCoreApplication

from geoplateforme.api.custom_exceptions import AddTagException
from geoplateforme.api.stored_data import StoredDataRequestManager
from geoplateforme.api.upload import UploadRequestManager
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
    DATASET_NAME = "dataset_name"

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
            "Create vector db stored data in geoplateforme platform.\n"
            "Input parameters are defined in a .json file.\n"
            "Available parameters:\n"
            "{\n"
            f'    "{self.DATASTORE}": datastore id (str),\n'
            f'    "{self.NAME}": wanted stored data name (str),\n'
            f'    "{self.DATASET_NAME}": dataset name, used for tag definition (str),\n'
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
            dataset_name = data[self.DATASET_NAME]

            # Create upload
            upload_id = self._create_upload(
                datastore, files, name, srs, context, feedback
            )

            # Run database integration
            vector_db_stored_data_id, exec_id = self._database_integration(
                name, datastore, upload_id, context, feedback
            )

            stored_data_tags = {
                "upload_id": upload_id,
                "datasheet_name": dataset_name,
                "proc_int_id": exec_id,
            }
            upload_tags = {
                "vectordb_id": vector_db_stored_data_id,
                "proc_int_id": exec_id,
                "datasheet_name": dataset_name,
            }

            self._add_upload_tag(
                datastore_id=datastore,
                upload_id=upload_id,
                tags=upload_tags,
            )

            self._add_stored_data_tag(
                datastore_id=datastore,
                stored_data_id=vector_db_stored_data_id,
                tags=stored_data_tags,
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
        algo_str = f"geoplateforme:{UploadCreationAlgorithm().name()}"
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

    def _add_upload_tag(
        self, datastore_id: str, upload_id: str, tags: dict[str, str]
    ) -> None:
        try:
            # Update stored data tags
            manager = UploadRequestManager()
            manager.add_tags(
                datastore_id=datastore_id,
                upload_id=upload_id,
                tags=tags,
            )
        except AddTagException as exc:
            raise QgsProcessingException(
                self.tr("Upload tag add failed : {0}").format(exc)
            )

    def _database_integration(
        self,
        name: str,
        datastore: str,
        upload_id: str,
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ) -> Tuple[str, str]:
        """
        Launch database integration for an upload

        Args:
            name: (str) stored data name
            datastore : (str) datastore id
            upload_id:  (str) upload id
            context: QgsProcessingContext
            feedback: QgsProcessingFeedback

        Returns: Tuple(str,str) created vector db stored data id, processing exec id

        """
        algo_str = f"geoplateforme:{UploadDatabaseIntegrationAlgorithm().name()}"
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
            exec_id = results[UploadDatabaseIntegrationAlgorithm.PROCESSING_EXEC_ID]
        else:
            raise QgsProcessingException(self.tr("Upload database integration failed"))
        return vector_db_stored_data_id, exec_id

    def _add_stored_data_tag(
        self, datastore_id: str, stored_data_id: str, tags: dict[str, str]
    ) -> None:
        try:
            # Update stored data tags
            manager = StoredDataRequestManager()
            manager.add_tags(
                datastore_id=datastore_id,
                stored_data_id=stored_data_id,
                tags=tags,
            )
        except AddTagException as exc:
            raise QgsProcessingException(
                self.tr("Stored data tag add failed : {0}").format(exc)
            )
