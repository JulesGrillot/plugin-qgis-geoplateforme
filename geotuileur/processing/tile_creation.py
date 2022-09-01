import json
from time import sleep

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingParameterFile,
)
from qgis.PyQt.QtCore import QCoreApplication

# plugin
from geotuileur.api.custom_exceptions import (
    CreateProcessingException,
    LaunchExecutionException,
    UnavailableProcessingException,
)
from geotuileur.api.processing import ProcessingRequestManager
from geotuileur.api.stored_data import StoredDataRequestManager, StoredDataStatus
from geotuileur.toolbelt import PlgOptionsManager


class TileCreationProcessingFeedback(QgsProcessingFeedback):
    """
    Implentation of QgsProcessingFeedback to store information from processing:
        - created_pyramid_id (str) : created pyramid stored data id
    """

    created_pyramid_id: str = ""


class TileCreationAlgorithm(QgsProcessingAlgorithm):
    INPUT_JSON = "INPUT_JSON"

    DATASTORE = "datastore"
    VECTOR_DB_STORED_DATA_ID = "vector_db_stored_data_id"
    STORED_DATA_NAME = "stored_data_name"
    TIPPECANOE_OPTIONS = "tippecanoe_options"
    TMS = "tms"
    BOTTOM_LEVEL = "bottom_level"
    TOP_LEVEL = "top_level"
    COMPOSITION = "composition"
    TABLE = "table"
    ATTRIBUTES = "attributes"
    BBOX = "bbox"

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
            f'    "{self.TMS}": tile matrix set (str) available options are "PM" or "4326",\n'
            f'    "{self.BOTTOM_LEVEL}": tile bottom level (str), value between 1 and 21,\n'
            f'    "{self.TOP_LEVEL}": tile top level (str), value between 1 and 21,\n'
            f'    "{self.COMPOSITION}": table composition ([]): define attributes and levels for each table,\n'
            f'        ["{self.TABLE}": (str) table name,\n'
            f'         "{self.ATTRIBUTES}": (str) attributes list as a string with "," separator,\n'
            f'         "{self.TOP_LEVEL}": tile top level (str), value between 1 and 21,\n'
            f'         "{self.TOP_LEVEL}": tile top level (str), value between 1 and 21,\n'
            f"        ]"
            f'    "{self.BBOX}": bounding box of sample generation ([x_min,y_min,x_max,y_max]): define bounding box, '
            f"if used is_sample tag added to created stored data,\n"
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

            # Check input data before use
            self._check_json_data(data)

            stored_data_name = data[self.STORED_DATA_NAME]
            datastore = data[self.DATASTORE]
            tippecanoe_options = data[self.TIPPECANOE_OPTIONS]
            vector_db_stored_data_id = data[self.VECTOR_DB_STORED_DATA_ID]

            tms = data[self.TMS]
            bottom_level = data[self.BOTTOM_LEVEL]
            top_level = data[self.TOP_LEVEL]
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
                }

                if tippecanoe_options:
                    exec_params["tippecanoe_options"] = tippecanoe_options

                bbox_used = False
                if self.BBOX in data:
                    exec_params[self.BBOX] = data[self.BBOX]
                    bbox_used = True

                if self.COMPOSITION in data:
                    exec_params[self.COMPOSITION] = data[self.COMPOSITION]

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

                # Update feedback if attribute is present
                if hasattr(feedback, "created_pyramid_id"):
                    feedback.created_pyramid_id = stored_data_id

                # Update stored data tags
                tags = {
                    "upload_id": vector_db_stored_data.tags["upload_id"],
                    "proc_int_id": vector_db_stored_data.tags["proc_int_id"],
                    "vectordb_id": vector_db_stored_data.id,
                    "pyramid_id": stored_data_id,
                    "proc_pyr_creat_id": exec_id,
                }

                if bbox_used:
                    tags["is_sample"] = "true"

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

                # Wait for tile creation
                self._wait_tile_creation(datastore, stored_data_id)

                # Delete vector db stored data
                stored_data_manager.delete(datastore, vector_db_stored_data_id)

            except StoredDataRequestManager.UnavailableStoredData as exc:
                raise QgsProcessingException(
                    f"Can't retrieve vector db datastore for tile creation : {exc}"
                )
            except UnavailableProcessingException as exc:
                raise QgsProcessingException(
                    f"Can't retrieve processing for tile creation : {exc}"
                )
            except CreateProcessingException as exc:
                raise QgsProcessingException(
                    f"Can't create processing execution for tile creation : {exc}"
                )
            except LaunchExecutionException as exc:
                raise QgsProcessingException(
                    f"Can't launch execution for tile creation : {exc}"
                )
            except StoredDataRequestManager.AddTagException as exc:
                raise QgsProcessingException(
                    f"Can't add tags to stored data for tile creation : {exc}"
                )
            except StoredDataRequestManager.DeleteStoredDataException as exc:
                raise QgsProcessingException(
                    f"Can't delete vector db stored data after tile creation : {exc}"
                )

        return {self.CREATED_STORED_DATA_ID: stored_data_id}

    def _check_json_data(self, data) -> None:
        """
        Check json data, raises QgsProcessingException in case of errors

        Args:
            data: input json data
        """
        mandatory_keys = [
            self.STORED_DATA_NAME,
            self.DATASTORE,
            self.TIPPECANOE_OPTIONS,
            self.VECTOR_DB_STORED_DATA_ID,
            self.TMS,
            self.BOTTOM_LEVEL,
            self.TOP_LEVEL,
        ]

        missing_keys = [key for key in mandatory_keys if key not in data]

        if missing_keys:
            raise QgsProcessingException(
                f"Missing {', '.join(missing_keys)} keys in input json."
            )

        if self.BBOX in data:
            self._check_bbox_data(data[self.BBOX])

        if self.COMPOSITION in data:
            self._check_composition(data[self.COMPOSITION])

    def _check_bbox_data(self, data) -> None:
        """
        Check bbox data, raises QgsProcessingException in case of errors

        Args:
            data: input bbox data
        """
        if not isinstance(data, list):
            raise QgsProcessingException(
                f"Invalid {self.BBOX} key in input json.  Expected list, not {type(data)}"
            )
        if len(data) != 4:
            raise QgsProcessingException(
                f"Invalid {self.BBOX} key in input json.  Expected 4 values [x_min,x_max,y_min,y_max]"
            )

    def _check_composition(self, data) -> None:
        """
        Check composition data, raises QgsProcessingException in case of errors

        Args:
            data: input composition data
        """
        if not isinstance(data, list):
            raise QgsProcessingException(
                f"Invalid {self.COMPOSITION} key in input json.  Expected list, not {type(data)}"
            )

        mandatory_keys = [self.TABLE, self.ATTRIBUTES]
        for compo in data:
            missing_keys = [key for key in mandatory_keys if key not in compo]

            if missing_keys:
                raise QgsProcessingException(
                    f"Missing {', '.join(missing_keys)} keys for {self.COMPOSITION} item in input json."
                )

    def _wait_tile_creation(self, datastore: str, pyramid_stored_data_id: str) -> None:
        """
        Wait until tile creation is done (GENERATED status) or throw exception if status is UNSTABLE

        Args:
            datastore: (str) datastore id
            pyramid_stored_data_id: (str) pyramid stored data id
        """
        try:
            manager = StoredDataRequestManager()
            stored_data = manager.get_stored_data(
                datastore=datastore, stored_data=pyramid_stored_data_id
            )
            status = StoredDataStatus(stored_data.status)
            while (
                status != StoredDataStatus.GENERATED
                and status != StoredDataStatus.UNSTABLE
            ):
                stored_data = manager.get_stored_data(
                    datastore=datastore, stored_data=pyramid_stored_data_id
                )
                status = StoredDataStatus(stored_data.status)
                sleep(PlgOptionsManager.get_plg_settings().status_check_sleep)

            if status == StoredDataStatus.UNSTABLE:
                raise QgsProcessingException(
                    self.tr(
                        "Tile creation failed. Check report in dashboard for more details."
                    )
                )

        except StoredDataRequestManager.ReadStoredDataException as exc:
            raise QgsProcessingException(f"Stored data read failed : {exc}")
