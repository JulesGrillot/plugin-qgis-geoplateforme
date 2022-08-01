# standard
import json
import os
import tempfile
from functools import partial

# PyQGIS
from qgis.core import (
    QgsApplication,
    QgsProcessingAlgorithm,
    QgsProcessingAlgRunnerTask,
    QgsProcessingContext,
    QgsProcessingFeedback,
)
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QByteArray, QTimer
from qgis.PyQt.QtGui import QMovie, QPixmap
from qgis.PyQt.QtWidgets import QHeaderView, QMessageBox, QWizardPage

from geotuileur.__about__ import DIR_PLUGIN_ROOT
from geotuileur.api.processing import ProcessingRequestManager
from geotuileur.api.stored_data import StoredDataRequestManager
from geotuileur.api.upload import UploadRequestManager
from geotuileur.gui.mdl_execution_list import ExecutionListModel
from geotuileur.gui.tile_creation.qwp_tile_generation_edition import (
    TileGenerationEditionPageWizard,
)
from geotuileur.gui.tile_creation.qwp_tile_generation_fields_selection import (
    TileGenerationFieldsSelectionPageWizard,
)
from geotuileur.gui.tile_creation.qwp_tile_generation_generalization import (
    TileGenerationGeneralizationPageWizard,
)
from geotuileur.processing import GeotuileurProvider
from geotuileur.processing.tile_creation import TileCreationAlgorithm


class TileGenerationStatusPageWizard(QWizardPage):
    STATUS_CHECK_INTERVAL = 500

    def __init__(
        self,
        qwp_tile_generation_edition: TileGenerationEditionPageWizard,
        qwp_tile_generation_fields_selection: TileGenerationFieldsSelectionPageWizard,
        qwp_tile_generation_generalization: TileGenerationGeneralizationPageWizard,
        parent=None,
    ):

        """
        QWizardPage to create tile vector

        Args:
            parent: parent QObject
        """

        super().__init__(parent)
        self.qwp_tile_generation_edition = qwp_tile_generation_edition
        self.qwp_tile_generation_fields_selection = qwp_tile_generation_fields_selection
        self.qwp_tile_generation_generalization = qwp_tile_generation_generalization

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "qwp_tile_generation_status.ui"),
            self,
        )

        # Task and feedback for tile creation
        self.create_tile_task_id = None
        self.create_tile_feedback = QgsProcessingFeedback()

        # Processing results
        self.created_stored_data_id = ""

        # Timer for processing execution check after tile creation
        self.loading_movie = QMovie(
            str(DIR_PLUGIN_ROOT / "resources" / "images" / "loading.gif"),
            QByteArray(),
            self,
        )
        self.create_tile_check_timer = QTimer(self)
        self.create_tile_check_timer.timeout.connect(self.check_create_tile_status)

        # Model for executions display
        self.mdl_execution_list = ExecutionListModel(self)
        self.tableview_execution_list.setModel(self.mdl_execution_list)

        self.tableview_execution_list.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )

    def initializePage(self) -> None:
        """
        Initialize page before show.

        """
        self.created_stored_data_id = ""
        self.mdl_execution_list.set_execution_list([])
        self.create_tile()

    def validatePage(self) -> bool:
        """
        Validate current page and stop timer used to check status

        Returns: True

        """
        self.create_tile_check_timer.stop()
        return True

    def create_tile(self) -> None:
        """
        Run TileCreationAlgorithm with parameters defined from previous QWizardPage

        """
        algo_str = f"{GeotuileurProvider().id()}:{TileCreationAlgorithm().name()}"
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)

        datastore_id = (
            self.qwp_tile_generation_edition.cbx_datastore.current_datastore_id()
        )
        vector_db_stored_id = (
            self.qwp_tile_generation_edition.cbx_stored_data.current_stored_data_id()
        )

        data = {
            TileCreationAlgorithm.DATASTORE: datastore_id,
            TileCreationAlgorithm.VECTOR_DB_STORED_DATA_ID: vector_db_stored_id,
            TileCreationAlgorithm.STORED_DATA_NAME: self.qwp_tile_generation_edition.lne_flux.text(),
            TileCreationAlgorithm.TIPPECANOE_OPTIONS: self.qwp_tile_generation_generalization.get_tippecanoe_value(),
            TileCreationAlgorithm.TMS: "PM",
            TileCreationAlgorithm.BOTTOM_LEVEL: str(
                self.qwp_tile_generation_edition.get_bottom_level()
            ),
            TileCreationAlgorithm.TOP_LEVEL: str(
                self.qwp_tile_generation_edition.get_top_level()
            ),
            TileCreationAlgorithm.COMPOSITION: [],
        }

        selected_attributes = (
            self.qwp_tile_generation_fields_selection.get_selected_attributes()
        )

        # Define composition for each table. For now using zoom levels from tile vector
        for table, attributes in selected_attributes.items():
            data[TileCreationAlgorithm.COMPOSITION].append(
                {
                    TileCreationAlgorithm.TABLE: table,
                    TileCreationAlgorithm.ATTRIBUTES: ",".join(attributes),
                    TileCreationAlgorithm.BOTTOM_LEVEL: str(
                        self.qwp_tile_generation_edition.get_bottom_level()
                    ),
                    TileCreationAlgorithm.TOP_LEVEL: str(
                        self.qwp_tile_generation_edition.get_top_level()
                    ),
                }
            )

        filename = tempfile.NamedTemporaryFile(suffix=".json").name
        with open(filename, "w") as file:
            json.dump(data, file)
            params = {TileCreationAlgorithm.INPUT_JSON: filename}

            self.lbl_step_text.setText(self.tr("Génération en cours"))
            self.lbl_step_icon.setMovie(self.loading_movie)
            self.loading_movie.start()

            self.create_tile_task_id = self._run_alg(
                alg, params, self.create_tile_feedback, self.create_tile_finished
            )

    def create_tile_finished(self, context, successful, results):
        """
        Callback executed when TileCreationAlgorithm is finished

        Args:
            context:  algorithm context
            successful: algorithm success
            results: algorithm results
        """
        if successful:
            self.created_stored_data_id = results[
                TileCreationAlgorithm.CREATED_STORED_DATA_ID
            ]
            # Run timer for tile creation check
            self.create_tile_check_timer.start(self.STATUS_CHECK_INTERVAL)
        else:
            msgBox = QMessageBox(
                QMessageBox.Warning,
                self.tr("Tile creation failed"),
                self.tr("Check details for more informations"),
            )
            msgBox.setDetailedText(self.create_tile_feedback.textLog())
            msgBox.exec()

    def check_create_tile_status(self):
        """
        Check tile creation status

        """
        if self.created_stored_data_id:
            try:
                upload_manager = UploadRequestManager()
                processing_manager = ProcessingRequestManager()
                stored_data_manager = StoredDataRequestManager()
                datastore_id = (
                    self.qwp_tile_generation_edition.cbx_datastore.current_datastore_id()
                )

                stored_data = stored_data_manager.get_stored_data(
                    datastore=datastore_id, stored_data=self.created_stored_data_id
                )

                execution_list = []
                if stored_data.tags and "upload_id" in stored_data.tags.keys():
                    execution_list = upload_manager.get_upload_checks_execution(
                        datastore=datastore_id, upload=stored_data.tags["upload_id"]
                    )

                # Stop timer if stored_data generated
                if stored_data.status == "GENERATED":
                    self.create_tile_check_timer.stop()
                    self.loading_movie.stop()
                    self.lbl_step_text.setText(self.tr("Votre donnée est prête"))
                    pixmap = QPixmap(
                        str(
                            DIR_PLUGIN_ROOT
                            / "resources"
                            / "images"
                            / "icons"
                            / "Done.svg"
                        )
                    )
                    self.lbl_step_icon.setMovie(QMovie())
                    self.lbl_step_icon.setPixmap(pixmap)
                if (
                    stored_data.tags is not None
                    and "proc_pyr_creat_id" in stored_data.tags.keys()
                ):
                    execution_list.append(
                        processing_manager.get_execution(
                            datastore=datastore_id,
                            exec_id=stored_data.tags["proc_pyr_creat_id"],
                        )
                    )
                self.mdl_execution_list.set_execution_list(execution_list)
            except StoredDataRequestManager.UnavailableStoredData as exc:
                msgBox = QMessageBox(
                    QMessageBox.Warning,
                    self.tr("Stored data check status failed"),
                    self.tr("Check details for more informations"),
                )
                msgBox.setDetailedText(str(exc))
                msgBox.exec()
            except ProcessingRequestManager.UnavailableProcessingException as exc:
                msgBox = QMessageBox(
                    QMessageBox.Warning,
                    self.tr("Stored data check status failed"),
                    self.tr("Check details for more informations"),
                )
                msgBox.setDetailedText(str(exc))
                msgBox.exec()
            except UploadRequestManager.UnavailableUploadException as exc:
                msgBox = QMessageBox(
                    QMessageBox.Warning,
                    self.tr("Stored data check status failed"),
                    self.tr("Check details for more informations"),
                )
                msgBox.setDetailedText(str(exc))
                msgBox.exec()

    def _run_alg(
        self,
        alg: QgsProcessingAlgorithm,
        params: {},
        feedback: QgsProcessingFeedback,
        executed_callback,
    ) -> int:
        """
        Run a QgsProcessingAlgorithm and connect execution callback and cancel task for button

        Args:
            alg: QgsProcessingAlgorithm to run
            params: QgsProcessingAlgorithm params
            feedback: QgsProcessingFeedback
            executed_callback: executed callback after algorithm execution
            btn: (optional) button to connect for QgsTask cancel

        Returns: created QgsTask

        """
        context = QgsProcessingContext()
        task = QgsProcessingAlgRunnerTask(alg, params, context, feedback)
        task.executed.connect(partial(executed_callback, context))
        return QgsApplication.taskManager().addTask(task)
