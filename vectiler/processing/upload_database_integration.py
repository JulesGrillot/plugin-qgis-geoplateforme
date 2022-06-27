import json

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterFile,
)
from qgis.PyQt.QtCore import QCoreApplication

from vectiler.api.processing import ProcessingRequestManager
from vectiler.api.stored_data import StoredDataRequestManager


class UploadDatabaseIntegrationAlgorithm(QgsProcessingAlgorithm):
    INPUT_JSON = "INPUT_JSON"

    DATASTORE = "datastore"
    UPLOAD = "upload"
    STORED_DATA_NAME = "stored_data_name"

    CREATED_STORED_DATA_ID = "CREATED_STORED_DATA_ID"

    def tr(self, string):
        return QCoreApplication.translate("Integrate upload in database", string)

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
            "Integration of geotuileur platform upload in database.\n"
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
                    "processing": processing.id,
                    "inputs": {"upload": [upload]},
                    "output": {"stored_data": {"name": stored_data_name}},
                    "parameters": {},
                }
                res = processing_manager.create_processing_execution(
                    datastore=datastore, input_map=data_map
                )
                stored_data_val = res["output"]["stored_data"]
                exec_id = res["_id"]

                # Get created stored_data id
                stored_data_id = stored_data_val["_id"]

                # Update stored data tags
                tags = {"upload_id": upload, "proc_int_id": exec_id}
                stored_data_manager.add_tags(
                    datastore=datastore, stored_data=stored_data_val["_id"], tags=tags
                )

                # Launch execution
                processing_manager.launch_execution(
                    datastore=datastore, exec_id=exec_id
                )

            except ProcessingRequestManager.UnavailableProcessingException as exc:
                raise QgsProcessingException(
                    f"Can't retrieve processing for database integration : {exc}"
                )
            except ProcessingRequestManager.CreateProcessingException as exc:
                raise QgsProcessingException(
                    f"Can't create processing execution for database integration : {exc}"
                )
            except ProcessingRequestManager.LaunchExecutionException as exc:
                raise QgsProcessingException(
                    f"Can't launch execution for database integration : {exc}"
                )
            except StoredDataRequestManager.AddTagException as exc:
                raise QgsProcessingException(
                    f"Can't add tags to stored data for database integration : {exc}"
                )

        return {self.CREATED_STORED_DATA_ID: stored_data_id}
