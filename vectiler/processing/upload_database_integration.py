from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterString,
)
from qgis.PyQt.QtCore import QCoreApplication

from vectiler.api.processing import ProcessingRequestManager
from vectiler.api.stored_data import StoredDataRequestManager


class UploadDatabaseIntegrationAlgorithm(QgsProcessingAlgorithm):
    DATASTORE = "DATASTORE"
    UPLOAD = "UPLOAD"
    STORED_DATA_NAME = "STORED_DATA_NAME"
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
        return ""

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterString(
                name=self.STORED_DATA_NAME,
                description=self.tr("Stored data name"),
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                name=self.DATASTORE,
                description=self.tr("Upload datastore"),
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                name=self.UPLOAD,
                description=self.tr("Upload id"),
                optional=False,
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        stored_data_name = self.parameterAsString(
            parameters, self.STORED_DATA_NAME, context
        )
        datastore = self.parameterAsString(parameters, self.DATASTORE, context)
        upload = self.parameterAsString(parameters, self.UPLOAD, context)
        stored_data_id = ""
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
            processing_manager.launch_execution(datastore=datastore, exec_id=exec_id)

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
