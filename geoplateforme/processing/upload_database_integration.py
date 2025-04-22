import json
from time import sleep

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingParameterFile,
)
from qgis.PyQt.QtCore import QCoreApplication

from geoplateforme.api.custom_exceptions import (
    AddTagException,
    CreateProcessingException,
    LaunchExecutionException,
    ReadStoredDataException,
    UnavailableProcessingException,
)
from geoplateforme.api.processing import ProcessingRequestManager
from geoplateforme.api.stored_data import StoredDataRequestManager, StoredDataStatus
from geoplateforme.toolbelt import PlgOptionsManager


class UploadDatabaseIntegrationProcessingFeedback(QgsProcessingFeedback):
    """
    Implementation of QgsProcessingFeedback to store information from processing:
        - created_vector_db_id (str) : created vector db stored data id
    """

    created_vector_db_id: str = ""


class UploadDatabaseIntegrationAlgorithm(QgsProcessingAlgorithm):
    INPUT_JSON = "INPUT_JSON"

    DATASTORE = "datastore"
    UPLOAD = "upload"
    STORED_DATA_NAME = "stored_data_name"

    PROCESSING_EXEC_ID = "PROCESSING_EXEC_ID"
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
        return UploadDatabaseIntegrationAlgorithm()

    def name(self):
        return "upload_database_integration"

    def displayName(self):
        return self.tr("Integrate upload in database")

    def group(self):
        return self.tr("")

    def groupId(self):
        return ""

    def helpUrl(self):
        return ""

    def shortHelpString(self):
        return self.tr(
            "Integration of geoplateforme platform upload in database.\n"
            "Input parameters are defined in a .json file.\n"
            "Available parameters:\n"
            "{\n"
            f'    "{self.STORED_DATA_NAME}": wanted stored data name (str),\n'
            f'    "{self.DATASTORE}": datastore id (str),\n'
            f'    "{self.UPLOAD}": upload id (str),\n'
            "}\n"
            f"Returns created stored data id in {self.CREATED_STORED_DATA_ID} results"
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

            stored_data_name = data[self.STORED_DATA_NAME]
            datastore = data[self.DATASTORE]
            upload = data[self.UPLOAD]
            try:
                stored_data_manager = StoredDataRequestManager()
                processing_manager = ProcessingRequestManager()

                # Get processing for database integration
                # TODO : for now we use processing name, how can we get processing otherwise ?
                processing = processing_manager.get_processing(
                    datastore, "Intégration de données vecteur livrées en base"
                )

                # Create execution
                data_map = {
                    "processing": processing._id,
                    "inputs": {"upload": [upload]},
                    "output": {"stored_data": {"name": stored_data_name}},
                    "parameters": {},
                }
                res = processing_manager.create_processing_execution(
                    datastore_id=datastore, input_map=data_map
                )
                stored_data_val = res["output"]["stored_data"]
                exec_id = res["_id"]

                # Get created stored_data id
                stored_data_id = stored_data_val["_id"]

                # Update feedback if vector db id attribute present
                if hasattr(feedback, "created_vector_db_id"):
                    feedback.created_vector_db_id = stored_data_id

                # Update stored data tags
                tags = {
                    "upload_id": upload,
                    "proc_int_id": exec_id,
                }
                stored_data_manager.add_tags(
                    datastore_id=datastore,
                    stored_data_id=stored_data_val["_id"],
                    tags=tags,
                )

                # Launch execution
                processing_manager.launch_execution(
                    datastore_id=datastore, exec_id=exec_id
                )

                # Wait for database integration
                self._wait_database_integration(datastore, stored_data_id)

            except UnavailableProcessingException as exc:
                raise QgsProcessingException(
                    f"Can't retrieve processing for database integration : {exc}"
                )
            except CreateProcessingException as exc:
                raise QgsProcessingException(
                    f"Can't create processing execution for database integration : {exc}"
                )
            except LaunchExecutionException as exc:
                raise QgsProcessingException(
                    f"Can't launch execution for database integration : {exc}"
                )
            except AddTagException as exc:
                raise QgsProcessingException(
                    f"Can't add tags to stored data for database integration : {exc}"
                )

        return {
            self.CREATED_STORED_DATA_ID: stored_data_id,
            self.PROCESSING_EXEC_ID: exec_id,
        }

    def _wait_database_integration(
        self, datastore: str, vector_db_stored_data_id: str
    ) -> None:
        """
        Wait until database integration is done (GENERATED status) or throw exception if status is UNSTABLE

        Args:
            datastore: (str) datastore id
            vector_db_stored_data_id: (str) vector db stored data id
        """
        try:
            manager = StoredDataRequestManager()
            stored_data = manager.get_stored_data(
                datastore_id=datastore, stored_data_id=vector_db_stored_data_id
            )
            status = stored_data.status
            while (
                status != StoredDataStatus.GENERATED
                and status != StoredDataStatus.UNSTABLE
            ):
                stored_data = manager.get_stored_data(
                    datastore_id=datastore, stored_data_id=vector_db_stored_data_id
                )
                status = stored_data.status
                sleep(PlgOptionsManager.get_plg_settings().status_check_sleep)

            if status == StoredDataStatus.UNSTABLE:
                raise QgsProcessingException(
                    self.tr(
                        "Database integration failed. Check report in dashboard for more details."
                    )
                )

        except ReadStoredDataException as exc:
            raise QgsProcessingException(f"Stored data read failed : {exc}")
