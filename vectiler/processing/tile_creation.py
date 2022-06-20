from PyQt5.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterString,
    QgsProcessingException,
    QgsProcessingParameterNumber,
    QgsProcessingParameterEnum
)

from vectiler.api.processing import ProcessingRequestManager
from vectiler.api.stored_data import StoredDataRequestManager


class TileCreationAlgorithm(QgsProcessingAlgorithm):
    DATASTORE = "DATASTORE"
    VECTOR_DB_STORED_DATA_ID = "VECTOR_DB_STORED_DATA_ID"
    STORED_DATA_NAME = "STORED_DATA_NAME"
    TIPPECANOE_OPTIONS = "TIPPECANOE_OPTIONS"
    TMS = "TMS"
    BOTTOM_LEVEL = "BOTTOM_LEVEL"
    TOP_LEVEL = "TOP_LEVEL"
    ATTRIBUTES = "ATTRIBUTES"

    TMS_ENUM = ["PM", "4326"]

    CREATED_STORED_DATA_ID = "CREATED_STORED_DATA_ID"

    def tr(self, string):
        return QCoreApplication.translate("Ask for tile creation", string)

    def createInstance(self):
        return TileCreationAlgorithm()

    def name(self):
        return "tile_creation"

    def displayName(self):
        return self.tr("Ask for tile creation")

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
                name=self.VECTOR_DB_STORED_DATA_ID,
                description=self.tr("Vector DB stored data id for tile generation"),
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                name=self.TIPPECANOE_OPTIONS,
                description=self.tr("Tippecanoe options"),
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.TMS,
                self.tr("Tile Matrix Set"),
                self.TMS_ENUM,
                defaultValue=0,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.BOTTOM_LEVEL,
                self.tr("Bottom level"),
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=18,
                minValue=5,
                maxValue=18,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.TOP_LEVEL,
                self.tr("Top level"),
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=5,
                minValue=5,
                maxValue=18,
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.ATTRIBUTES,
                self.tr("Attributes"),
                optional=True,
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        stored_data_name = self.parameterAsString(parameters, self.STORED_DATA_NAME, context)
        datastore = self.parameterAsString(parameters, self.DATASTORE, context)
        tippecanoe_options = self.parameterAsString(parameters, self.TIPPECANOE_OPTIONS, context)
        vector_db_stored_data_id = self.parameterAsString(parameters, self.VECTOR_DB_STORED_DATA_ID, context)

        tms = self.TMS_ENUM[self.parameterAsEnum(parameters, self.TMS, context)]
        bottom_level = self.parameterAsString(parameters, self.BOTTOM_LEVEL, context)
        top_level = self.parameterAsString(parameters, self.TOP_LEVEL, context)
        attributes = self.parameterAsString(parameters, self.ATTRIBUTES, context)
        try:
            stored_data_manager = StoredDataRequestManager()
            processing_manager = ProcessingRequestManager()

            vector_db_stored_data = stored_data_manager.get_stored_data(datastore, vector_db_stored_data_id)

            # Get processing for tile creation
            # TODO : for now we use processing name, how can we get processing otherwise ?
            processing = processing_manager.get_processing(datastore,
                                                           "Création d'une pyramide vecteur")
            # Execution parameters
            exec_params = {
                "tms": tms,
                "bottom_level": bottom_level,
                "top_level": top_level,
                "tippecanoe_options": tippecanoe_options
            }

            # Define attributes parameters : for now common attributes for all table and same bottom and top level
            if attributes:
                compositions = []
                for table in vector_db_stored_data.get_tables():
                    compositions.append({
                        "table": table,
                        "bottom_level": bottom_level,
                        "top_level": top_level,
                        "attributes": attributes
                    })
                exec_params["composition"] = compositions

            # Create execution
            data_map = {
                "processing": processing.id,
                "inputs": {
                    "stored_data": [vector_db_stored_data_id]
                },
                "output": {
                    "stored_data": {
                        "name": stored_data_name
                    }
                },
                "parameters": exec_params
            }
            res = processing_manager.create_processing_execution(datastore=datastore, input_map=data_map)
            stored_data_val = res["output"]["stored_data"]
            exec_id = res["_id"]

            # Get created stored_data id
            stored_data_id = stored_data_val["_id"]

            # Update stored data tags
            tags = {
                "upload_id": vector_db_stored_data.tags["upload_id"],
                "proc_int_id": vector_db_stored_data.tags["proc_int_id"],
                "vectordb_id": vector_db_stored_data.id,
                "pyramid_id": stored_data_id,
                "proc_pyr_creat_id": exec_id
            }
            stored_data_manager.add_tags(datastore=datastore, stored_data=stored_data_val["_id"], tags=tags)

            # Add tag to vector db
            vector_db_tag = {
                "pyramid_id": stored_data_id,
            }
            stored_data_manager.add_tags(datastore=datastore, stored_data=vector_db_stored_data.id, tags=vector_db_tag)

            # Launch execution
            processing_manager.launch_execution(datastore=datastore, exec_id=exec_id)

        except StoredDataRequestManager.UnavailableStoredData as exc:
            raise QgsProcessingException(f"Can't retrieve vector db datastore for tile creation : {exc}")
        except ProcessingRequestManager.UnavailableProcessingException as exc:
            raise QgsProcessingException(f"Can't retrieve processing for tile creation : {exc}")
        except ProcessingRequestManager.CreateProcessingException as exc:
            raise QgsProcessingException(f"Can't create processing execution for tile creation : {exc}")
        except ProcessingRequestManager.LaunchExecutionException as exc:
            raise QgsProcessingException(f"Can't launch execution for tile creation : {exc}")
        except StoredDataRequestManager.AddTagException as exc:
            raise QgsProcessingException(f"Can't add tags to stored data for tile creation : {exc}")

        return {self.CREATED_STORED_DATA_ID: stored_data_id}
