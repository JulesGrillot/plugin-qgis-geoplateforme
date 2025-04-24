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

# plugin
from geoplateforme.api.custom_exceptions import (
    AddTagException,
    UnavailableExecutionException,
    UnavailableStoredData,
)
from geoplateforme.api.processing import ProcessingRequestManager
from geoplateforme.api.stored_data import StoredDataRequestManager
from geoplateforme.processing.tile_creation import TileCreationAlgorithm
from geoplateforme.processing.vector_db_creation import VectorDatabaseCreationAlgorithm


class UpdateTileUploadProcessingFeedback(QgsProcessingFeedback):
    """
    Implentation of QgsProcessingFeedback to store information from processing:
        - created_upload_id (str) : created upload id
        - created_vector_db_id (str) : created vector db stored data id
    """

    created_upload_id: str = ""
    created_vector_db_id: str = ""


class UpdateTileUploadAlgorithm(QgsProcessingAlgorithm):
    INPUT_JSON = "INPUT_JSON"

    DATASTORE = "datastore"
    STORED_DATA = "stored_data"
    NAME = "name"
    FILES = "files"
    SRS = "srs"

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
        return UpdateTileUploadAlgorithm()

    def name(self):
        return "update_tile_upload"

    def displayName(self):
        return self.tr("Update tile upload")

    def group(self):
        return self.tr("")

    def groupId(self):
        return ""

    def helpUrl(self):
        return ""

    def shortHelpString(self):
        return self.tr(
            "Update tile upload in geoplateforme platform.\n"
            "Input parameters are defined in a .json file.\n"
            "Available parameters:\n"
            "{\n"
            f'    "{self.DATASTORE}": datastore id (str),\n'
            f'    "{self.STORED_DATA}": stored data id (str),\n'
            f'    "{self.NAME}": wanted stored data name (str),\n'
            f'    "{self.FILES}": upload full file path list [str],\n'
            f'    "{self.SRS}": upload SRS (str) must be in IGNF or EPSG repository,\n'
            "}\n"
            f"Returns created stored data in {self.CREATED_STORED_DATA_ID} results"
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
            initial_stored_data_id = data[self.STORED_DATA]

        # Get pyramid creation parameters
        exec_param = self._get_pyramid_creation_params(
            datastore, initial_stored_data_id
        )

        # Create vector db
        vector_db_stored_data_id = self._database_integration(
            datastore, files, name, srs, context, feedback
        )

        # Create tile
        created_stored_data = self._tile_creation(
            name, datastore, vector_db_stored_data_id, exec_param, context, feedback
        )

        # Add tag with initial_pyramid_id
        self._add_tags(datastore, initial_stored_data_id, created_stored_data)

        return {self.CREATED_STORED_DATA_ID: created_stored_data}

    def _get_pyramid_creation_params(
        self, datastore: str, initial_stored_data_id: str
    ) -> dict:
        """
        Get pyramid creation parameters

        Args:
            datastore: (str) datastore id
            initial_stored_data_id: (str) initial stored data id

        Returns: (dict) execution parameters

        """

        # Read stored data
        try:
            manager = StoredDataRequestManager()
            initial_stored_data = manager.get_stored_data(
                datastore, initial_stored_data_id
            )
        except UnavailableStoredData as exc:
            raise QgsProcessingException(
                self.tr("Stored data read failed : {0}").format(exc)
            )

        # Get pyramid creation execution parameters
        if initial_stored_data.tags and "proc_pyr_creat_id" in initial_stored_data.tags:
            try:
                execution_id = initial_stored_data.tags["proc_pyr_creat_id"]
                proc_manager = ProcessingRequestManager()
                execution = proc_manager.get_execution(datastore, execution_id)
                exec_param = execution.parameters
            except UnavailableExecutionException as exc:
                raise QgsProcessingException(
                    self.tr("Execution read failed : {0}").format(exc)
                )
        else:
            raise QgsProcessingException(
                self.tr('Invalid stored data. Must have a "proc_pyr_creat_id" tag.')
            )
        return exec_param

    def _database_integration(
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
        algo_str = f"geoplateforme:{VectorDatabaseCreationAlgorithm().name()}"
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)
        data = {
            VectorDatabaseCreationAlgorithm.DATASTORE: datastore,
            VectorDatabaseCreationAlgorithm.NAME: name,
            VectorDatabaseCreationAlgorithm.SRS: srs,
            VectorDatabaseCreationAlgorithm.FILES: files,
        }
        filename = tempfile.NamedTemporaryFile(suffix=".json").name
        with open(filename, "w") as file:
            json.dump(data, file)
        params = {VectorDatabaseCreationAlgorithm.INPUT_JSON: filename}
        results, successful = alg.run(params, context, feedback)
        if successful:
            vector_db_stored_data_id = results[
                VectorDatabaseCreationAlgorithm.CREATED_STORED_DATA_ID
            ]
        else:
            raise QgsProcessingException(self.tr("Vector database creation failed"))
        return vector_db_stored_data_id

    def _tile_creation(
        self,
        name: str,
        datastore: str,
        vector_db_stored_data_id: str,
        exec_param: dict,
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ):
        """
        Create tile from a vector db stored data and execution parameters

        Args:
            name: (str) stored data name
            datastore: (str) datastore id
            vector_db_stored_data_id: (str) vector db stored data id for tile generation
            exec_param: (dict) execution parameter from previous stored data
            context: QgsProcessingContext
            feedback: QgsProcessingFeedback

        Returns: (str) created pyramid stored data

        """
        algo_str = f"geoplateforme:{TileCreationAlgorithm().name()}"
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)
        data = {
            TileCreationAlgorithm.DATASTORE: datastore,
            TileCreationAlgorithm.VECTOR_DB_STORED_DATA_ID: vector_db_stored_data_id,
            TileCreationAlgorithm.STORED_DATA_NAME: name,
            TileCreationAlgorithm.BOTTOM_LEVEL: exec_param["bottom_level"],
            TileCreationAlgorithm.TOP_LEVEL: exec_param["top_level"],
            TileCreationAlgorithm.COMPOSITION: exec_param["composition"],
        }
        if "tippecanoe_options" in exec_param:
            data[TileCreationAlgorithm.TIPPECANOE_OPTIONS] = exec_param[
                "tippecanoe_options"
            ]
        filename = tempfile.NamedTemporaryFile(suffix=".json").name
        with open(filename, "w") as file:
            json.dump(data, file)
        params = {TileCreationAlgorithm.INPUT_JSON: filename}
        results, successful = alg.run(params, context, feedback)
        if successful:
            created_stored_data = results[TileCreationAlgorithm.CREATED_STORED_DATA_ID]
        else:
            raise QgsProcessingException(self.tr("Upload tile creation failed"))
        return created_stored_data

    def _add_tags(
        self, datastore: str, initial_stored_data_id: str, created_stored_data: str
    ):
        """
        Add tags to stored data for initial pyramid and update pyramid

        Args:
            datastore: (str) datastore id
            initial_stored_data_id: (str) initial stored data id
            created_stored_data: (str) created stored data id
        """
        try:
            # Update stored data tags
            manager = StoredDataRequestManager()
            manager.add_tags(
                datastore_id=datastore,
                stored_data_id=created_stored_data,
                tags={"initial_pyramid_id": initial_stored_data_id},
            )
            manager.add_tags(
                datastore_id=datastore,
                stored_data_id=initial_stored_data_id,
                tags={"update_pyramid_id": created_stored_data},
            )
        except AddTagException as exc:
            raise QgsProcessingException(
                self.tr("Stored data tag add failed : {0}").format(exc)
            )
