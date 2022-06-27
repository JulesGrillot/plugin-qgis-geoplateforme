import json

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterFile,
)
from qgis.PyQt.QtCore import QCoreApplication

from vectiler.api.processing import ProcessingRequestManager
from vectiler.api.stored_data import StoredDataRequestManager


class TileCreationAlgorithm(QgsProcessingAlgorithm):
    INPUT_JSON = "INPUT_JSON"

    DATASTORE = "datastore"
    VECTOR_DB_STORED_DATA_ID = "vector_db_stored_data_id"
    STORED_DATA_NAME = "stored_data_name"
    TIPPECANOE_OPTIONS = "tippecanoe_options"
    TMS = "tms"
    BOTTOM_LEVEL = "bottom_level"
    TOP_LEVEL = "top_level"
    ATTRIBUTES = "attributes"
    COMPOSITION = "composition"

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
        return self.tr(
            "Tile creation in geotuileur platform.\n"
            "Input parameters are defined in a .json file.\n"
            "Available parameters:\n"
            "{\n"
            f'    "{self.STORED_DATA_NAME}": wanted stored data name (str),\n'
            f'    "{self.DATASTORE}": datastore id (str),\n'
            f'    "{self.VECTOR_DB_STORED_DATA_ID}": vector db stored data is used for tile creation (str),\n'
            f'    "{self.TIPPECANOE_OPTIONS}": tippecanoe option for tile creation (str),\n'
            f'    "{self.TMS}": tile matrix set (str),\n'
            f'    "{self.BOTTOM_LEVEL}": tile bottom level (int), value between 1 and 21,\n'
            f'    "{self.TOP_LEVEL}": tile top level (int), value between 1 and 21,\n'
            f'    "{self.COMPOSITION}": table composition ([]): define attributes and levels for each table,\n'
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
            print(data)

            stored_data_name = data[self.STORED_DATA_NAME]
            datastore = data[self.DATASTORE]
            tippecanoe_options = data[self.TIPPECANOE_OPTIONS]
            vector_db_stored_data_id = data[self.VECTOR_DB_STORED_DATA_ID]

            tms = data[self.TMS]
            bottom_level = data[self.BOTTOM_LEVEL]
            top_level = data[self.TOP_LEVEL]
            attributes = data[self.ATTRIBUTES]
            try:
                stored_data_manager = StoredDataRequestManager()
                processing_manager = ProcessingRequestManager()

                vector_db_stored_data = stored_data_manager.get_stored_data(
                    datastore, vector_db_stored_data_id
                )

                # Get processing for tile creation
                # TODO : for now we use processing name, how can we get processing otherwise ?
                processing = processing_manager.get_processing(
                    datastore, "Création d'une pyramide vecteur"
                )
                # Execution parameters
                exec_params = {
                    "tms": tms,
                    "bottom_level": str(bottom_level),
                    "top_level": str(top_level),
                    "tippecanoe_options": tippecanoe_options,
                }

                # Define attributes parameters : for now common attributes for all table and same bottom and top level
                if attributes:
                    compositions = []
                    for table in vector_db_stored_data.get_tables():
                        compositions.append(
                            {
                                "table": table,
                                "bottom_level": str(bottom_level),
                                "top_level": str(top_level),
                                "attributes": attributes,
                            }
                        )
                    exec_params["composition"] = compositions

                # Create execution
                data_map = {
                    "processing": processing.id,
                    "inputs": {"stored_data": [vector_db_stored_data_id]},
                    "output": {"stored_data": {"name": stored_data_name}},
                    "parameters": exec_params,
                }
                res = processing_manager.create_processing_execution(
                    datastore=datastore, input_map=data_map
                )
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
                    "proc_pyr_creat_id": exec_id,
                }
                stored_data_manager.add_tags(
                    datastore=datastore, stored_data=stored_data_val["_id"], tags=tags
                )

                # Add tag to vector db
                vector_db_tag = {
                    "pyramid_id": stored_data_id,
                }
                stored_data_manager.add_tags(
                    datastore=datastore,
                    stored_data=vector_db_stored_data.id,
                    tags=vector_db_tag,
                )

                # Launch execution
                processing_manager.launch_execution(
                    datastore=datastore, exec_id=exec_id
                )

            except StoredDataRequestManager.UnavailableStoredData as exc:
                raise QgsProcessingException(
                    f"Can't retrieve vector db datastore for tile creation : {exc}"
                )
            except ProcessingRequestManager.UnavailableProcessingException as exc:
                raise QgsProcessingException(
                    f"Can't retrieve processing for tile creation : {exc}"
                )
            except ProcessingRequestManager.CreateProcessingException as exc:
                raise QgsProcessingException(
                    f"Can't create processing execution for tile creation : {exc}"
                )
            except ProcessingRequestManager.LaunchExecutionException as exc:
                raise QgsProcessingException(
                    f"Can't launch execution for tile creation : {exc}"
                )
            except StoredDataRequestManager.AddTagException as exc:
                raise QgsProcessingException(
                    f"Can't add tags to stored data for tile creation : {exc}"
                )

        return {self.CREATED_STORED_DATA_ID: stored_data_id}
