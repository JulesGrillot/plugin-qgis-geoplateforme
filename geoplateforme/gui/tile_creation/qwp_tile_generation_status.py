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
from qgis.PyQt.QtCore import QByteArray, QSize, QTimer
from qgis.PyQt.QtGui import QIcon, QMovie, QPixmap
from qgis.PyQt.QtWidgets import QHeaderView, QMessageBox, QWizardPage

# plugin
from geoplateforme.__about__ import DIR_PLUGIN_ROOT
from geoplateforme.api.custom_exceptions import (
    UnavailableProcessingException,
    UnavailableStoredData,
    UnavailableUploadException,
)
from geoplateforme.api.processing import ProcessingRequestManager
from geoplateforme.api.stored_data import StoredDataRequestManager, StoredDataStatus
from geoplateforme.api.upload import UploadRequestManager
from geoplateforme.gui.mdl_execution_list import ExecutionListModel
from geoplateforme.gui.tile_creation.qwp_tile_generation_edition import (
    TileGenerationEditionPageWizard,
)
from geoplateforme.gui.tile_creation.qwp_tile_generation_fields_selection import (
    TileGenerationFieldsSelectionPageWizard,
)
from geoplateforme.gui.tile_creation.qwp_tile_generation_generalization import (
    TileGenerationGeneralizationPageWizard,
)
from geoplateforme.gui.tile_creation.qwp_tile_generation_sample import (
    TileGenerationSamplePageWizard,
)
from geoplateforme.processing import GeoplateformeProvider
from geoplateforme.processing.tile_creation import (
    TileCreationAlgorithm,
    TileCreationProcessingFeedback,
)
from geoplateforme.toolbelt import PlgOptionsManager


class TileGenerationStatusPageWizard(QWizardPage):
    def __init__(
        self,
        qwp_tile_generation_edition: TileGenerationEditionPageWizard,
        qwp_tile_generation_fields_selection: TileGenerationFieldsSelectionPageWizard,
        qwp_tile_generation_generalization: TileGenerationGeneralizationPageWizard,
        qwp_tile_generation_sample: TileGenerationSamplePageWizard,
        parent=None,
    ):
        """
        QWizardPage to create tile vector

        Args:
            parent: parent QObject
        """

        super().__init__(parent)
        self.setTitle(self.tr("Generating in progress"))
        self.qwp_tile_generation_edition = qwp_tile_generation_edition
        self.qwp_tile_generation_fields_selection = qwp_tile_generation_fields_selection
        self.qwp_tile_generation_generalization = qwp_tile_generation_generalization
        self.qwp_tile_generation_sample = qwp_tile_generation_sample

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "qwp_tile_generation_status.ui"),
            self,
        )
        self.tbw_errors.setVisible(False)

        # Task and feedback for tile creation
        self.create_tile_task_id = None
        self.create_tile_feedback = TileCreationProcessingFeedback()

        # Processing results
        self.created_stored_data_id = ""
        self.processing_failed = False

        # Timer for processing execution check after tile creation
        self.loading_movie = QMovie(
            str(DIR_PLUGIN_ROOT / "resources" / "images" / "loading.gif"),
            QByteArray(),
            self,
        )
        self.create_tile_check_timer = QTimer(self)
        self.create_tile_check_timer.timeout.connect(self._check_create_tile_status)

        # Model for executions display
        self.mdl_execution_list = ExecutionListModel(self)
        self.tableview_execution_list.setModel(self.mdl_execution_list)

        self.tableview_execution_list.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )

    def initializePage(self) -> None:
        """
        Initialize page before show.

        """
        self.created_stored_data_id = ""
        self.processing_failed = False
        self.mdl_execution_list.clear_executions()
        self.create_tile()

    def validatePage(self) -> bool:
        """
        Validate current page and stop timer used to check status

        Returns: True

        """

        result = True

        if not self.created_stored_data_id and not self.processing_failed:
            result = False
            QMessageBox.warning(
                self,
                self.tr("Tile creation not launched."),
                self.tr(
                    "Tile creation is not launched. You must wait for launch before closing this dialog."
                ),
            )

        if result:
            self.create_tile_check_timer.stop()

        return result

    def create_tile(self) -> None:
        """
        Run TileCreationAlgorithm with parameters defined from previous QWizardPage

        """
        algo_str = f"{GeoplateformeProvider().id()}:{TileCreationAlgorithm().name()}"
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)

        datastore_id = (
            self.qwp_tile_generation_edition.cbx_datastore.current_datastore_id()
        )
        vector_db_stored_id = (
            self.qwp_tile_generation_edition.cbx_stored_data.current_stored_data_id()
        )
        dataset_name = (
            self.qwp_tile_generation_edition.cbx_dataset.current_dataset_name()
        )

        data = {
            TileCreationAlgorithm.DATASTORE: datastore_id,
            TileCreationAlgorithm.VECTOR_DB_STORED_DATA_ID: vector_db_stored_id,
            TileCreationAlgorithm.DATASET_NAME: dataset_name,
            TileCreationAlgorithm.STORED_DATA_NAME: self.qwp_tile_generation_edition.lne_flux.text(),
            TileCreationAlgorithm.TIPPECANOE_OPTIONS: self.qwp_tile_generation_generalization.get_tippecanoe_value(),
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
                    TileCreationAlgorithm.ATTRIBUTES: attributes,
                    TileCreationAlgorithm.BOTTOM_LEVEL: str(
                        self.qwp_tile_generation_edition.get_bottom_level()
                    ),
                    TileCreationAlgorithm.TOP_LEVEL: str(
                        self.qwp_tile_generation_edition.get_top_level()
                    ),
                }
            )

        # Add bounding box for sample generation if enabled
        if self.qwp_tile_generation_sample.is_sample_enabled():
            qgs_rectangle = self.qwp_tile_generation_sample.get_sample_box()
            data[TileCreationAlgorithm.BBOX] = [
                qgs_rectangle.xMinimum(),
                qgs_rectangle.yMinimum(),
                qgs_rectangle.xMaximum(),
                qgs_rectangle.yMaximum(),
            ]

        filename = tempfile.NamedTemporaryFile(suffix=".json").name
        with open(filename, "w") as file:
            json.dump(data, file)
        params = {TileCreationAlgorithm.INPUT_JSON: filename}

        self.lbl_step_icon.setMovie(self.loading_movie)
        self.loading_movie.start()

        self.create_tile_task_id = self._run_alg(
            alg, params, self.create_tile_feedback, self._create_tile_finished
        )

        # Run timer for tile creation check
        self.create_tile_check_timer.start(
            int(PlgOptionsManager.get_plg_settings().status_check_sleep / 1000.0)
        )

    def _create_tile_finished(self, context, successful, results):
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
        else:
            self._report_processing_error(
                self.tr("Tile creation"), self.create_tile_feedback.textLog()
            )

    def _check_create_tile_status(self):
        """
        Check tile creation status

        """
        self.mdl_execution_list.clear_executions()

        if self.create_tile_feedback.created_pyramid_id:
            self.created_stored_data_id = self.create_tile_feedback.created_pyramid_id
            try:
                upload_manager = UploadRequestManager()
                processing_manager = ProcessingRequestManager()
                stored_data_manager = StoredDataRequestManager()
                datastore_id = self.qwp_tile_generation_edition.cbx_datastore.current_datastore_id()

                stored_data = stored_data_manager.get_stored_data(
                    datastore_id=datastore_id,
                    stored_data_id=self.created_stored_data_id,
                )

                if stored_data.tags and "upload_id" in stored_data.tags.keys():
                    check_execution_list = upload_manager.get_upload_checks_execution(
                        datastore_id=datastore_id,
                        upload_id=stored_data.tags["upload_id"],
                    )
                    self.mdl_execution_list.set_check_execution_list(
                        check_execution_list
                    )

                # Stop timer if stored_data generated
                status = stored_data.status
                if status == StoredDataStatus.GENERATED:
                    self.create_tile_check_timer.stop()
                    self.loading_movie.stop()
                    self.setTitle(self.tr("Your tiles are ready."))
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
                elif status == StoredDataStatus.UNSTABLE:
                    self._stop_timer_and_display_error(
                        self.tr(
                            "Stored data creation failed. Check report in "
                            "dashboard for more details."
                        )
                    )
                if (
                    stored_data.tags is not None
                    and "proc_pyr_creat_id" in stored_data.tags.keys()
                ):
                    execution = processing_manager.get_execution(
                        datastore_id=datastore_id,
                        exec_id=stored_data.tags["proc_pyr_creat_id"],
                    )

                    self.mdl_execution_list.set_execution_list([execution])
            except (
                UnavailableStoredData,
                UnavailableProcessingException,
                UnavailableUploadException,
            ) as exc:
                self._report_processing_error(
                    self.tr("Stored data check status"), str(exc)
                )

    def _stop_timer_and_display_error(self, error: str) -> None:
        self.create_tile_check_timer.stop()
        self.setTitle(error)
        self.loading_movie.stop()
        self.lbl_step_icon.setMovie(QMovie())
        self.lbl_step_icon.setPixmap(
            QIcon(QgsApplication.iconPath("mIconWarning.svg")).pixmap(QSize(32, 32))
        )
        self.completeChanged.emit()

    def _report_processing_error(self, processing: str, error: str) -> None:
        """
        Report processing error by displaying error in text browser

        Args:
            error:
        """
        self.processing_failed = True
        self.tbw_errors.setVisible(True)
        self.tbw_errors.setText(error)
        self._stop_timer_and_display_error(
            self.tr("{0} failed. Check report for more details.").format(processing)
        )

    @staticmethod
    def _run_alg(
        alg: QgsProcessingAlgorithm,
        params: {},
        feedback: QgsProcessingFeedback,
        executed_callback,
    ) -> int:
        """
        Run a QgsProcessingAlgorithm and connect execution callback

        Args:
            alg: QgsProcessingAlgorithm to run
            params: QgsProcessingAlgorithm params
            feedback: QgsProcessingFeedback
            executed_callback: executed callback after algorithm execution

        Returns: created QgsTask id

        """
        context = QgsProcessingContext()
        task = QgsProcessingAlgRunnerTask(alg, params, context, feedback)
        task.executed.connect(partial(executed_callback, context))
        return QgsApplication.taskManager().addTask(task)
