# standard
import json
import os
import tempfile
from functools import partial
from typing import List

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
from geoplateforme.api.check import CheckExecution
from geoplateforme.api.custom_exceptions import (
    UnavailableProcessingException,
    UnavailableStoredData,
    UnavailableUploadException,
)
from geoplateforme.api.processing import Execution, ProcessingRequestManager
from geoplateforme.api.stored_data import StoredDataRequestManager
from geoplateforme.api.upload import UploadRequestManager
from geoplateforme.gui.mdl_execution_list import ExecutionListModel
from geoplateforme.gui.update_tile_upload.qwp_update_tile_upload_edition import (
    UpdateTileUploadEditionPageWizard,
)
from geoplateforme.processing import GeoplateformeProvider
from geoplateforme.processing.update_tile_upload import (
    UpdateTileUploadAlgorithm,
    UpdateTileUploadProcessingFeedback,
)
from geoplateforme.toolbelt import PlgLogger, PlgOptionsManager


class UpdateTileUploadRunPageWizard(QWizardPage):
    def __init__(
        self, qwp_upload_edition: UpdateTileUploadEditionPageWizard, parent=None
    ):
        """
        QWizardPage to update tile upload in geoplateforme platform

        Args:
            parent: parent QObject
        """

        super().__init__(parent)
        self.setTitle(self.tr("Checking and integration of your data in progress"))
        self.log = PlgLogger().log
        self.qwp_upload_edition = qwp_upload_edition

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "qwp_update_tile_upload_run.ui"),
            self,
        )

        self.tbw_errors.setVisible(False)

        # Task ID and feedback for update
        self.update_task_id = None
        self.created_upload_id = ""
        self.created_vector_db_stored_data_id = ""
        self.created_pyramid_stored_data_id = ""
        self.update_feedback = UpdateTileUploadProcessingFeedback()

        # Processing results
        self.processing_failed = False

        # Timer for update check
        self.loading_movie = QMovie(
            str(DIR_PLUGIN_ROOT / "resources" / "images" / "loading.gif"),
            QByteArray(),
            self,
        )
        self.update_check_timer = QTimer(self)
        self.update_check_timer.timeout.connect(self.check_update_status)

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
        self.tbw_errors.setVisible(False)
        self.update_task_id = None
        self.created_pyramid_stored_data_id = None

        # Processing results
        self.processing_failed = False

        self.mdl_execution_list.clear_executions()
        self.update()

    def update(self) -> None:
        """
        Run UploadCreationAlgorithm with UploadEditionPageWizard parameters

        """
        self.log("Launch UpdateTileUploadAlgorithm")
        algo_str = (
            f"{GeoplateformeProvider().id()}:{UpdateTileUploadAlgorithm().name()}"
        )
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)

        data = {
            UpdateTileUploadAlgorithm.DATASTORE: self.qwp_upload_edition.cbx_datastore.current_datastore_id(),
            UpdateTileUploadAlgorithm.STORED_DATA: self.qwp_upload_edition.cbx_stored_data.current_stored_data_id(),
            UpdateTileUploadAlgorithm.NAME: self.qwp_upload_edition.wdg_upload_creation.get_name(),
            UpdateTileUploadAlgorithm.SRS: self.qwp_upload_edition.wdg_upload_creation.get_crs(),
            UpdateTileUploadAlgorithm.FILES: self.qwp_upload_edition.wdg_upload_creation.get_filenames(),
        }
        filename = tempfile.NamedTemporaryFile(suffix=".json").name
        with open(filename, "w") as file:
            json.dump(data, file)
            params = {UpdateTileUploadAlgorithm.INPUT_JSON: filename}
            self.lbl_step_icon.setMovie(self.loading_movie)
            self.loading_movie.start()

            self.update_task_id = self._run_alg(
                alg, params, self.update_feedback, self.update_finished
            )

            # Run timer for update check
            self.update_check_timer.start(
                int(PlgOptionsManager.get_plg_settings().status_check_sleep / 1000.0)
            )

    def update_finished(self, context, successful, results):
        """
        Callback executed when UpdateTileUploadAlgorithm is finished

        Args:
            context:  algorithm context
            successful: algorithm success
            results: algorithm results
        """
        if successful:
            self.created_pyramid_stored_data_id = results[
                UpdateTileUploadAlgorithm.CREATED_STORED_DATA_ID
            ]
            self.loading_movie.stop()
            self.setTitle(self.tr("Your data has been stored on the remote storage."))
            pixmap = QPixmap(
                str(DIR_PLUGIN_ROOT / "resources" / "images" / "icons" / "Done.svg")
            )
            self.lbl_step_icon.setMovie(QMovie())
            self.lbl_step_icon.setPixmap(pixmap)

            # Emit completeChanged to update finish button
            self.completeChanged.emit()
        else:
            self._report_processing_error(
                self.tr("Update tile upload"), self.update_feedback.textLog()
            )

    def check_update_status(self):
        """
        Check update status

        """
        self.mdl_execution_list.clear_executions()
        self.mdl_execution_list.set_check_execution_list(self._check_upload_creation())

        execution_list = []
        execution = self._check_vector_stored_data_creation()
        if execution:
            execution_list.append(execution)

        execution = self._check_pyramid_stored_data_creation()
        if execution:
            execution_list.append(execution)

        self.mdl_execution_list.set_execution_list(execution_list)

    def _check_upload_creation(self) -> List[CheckExecution]:
        """
        Check if upload creation check are done and return checks execution.
        Il upload is closed, launch database integration

        Returns: [Execution] upload checks Execution

        """
        execution_list = []
        if self.update_feedback.created_upload_id:
            self.created_upload_id = self.update_feedback.created_upload_id
            try:
                manager = UploadRequestManager()
                datastore_id = (
                    self.qwp_upload_edition.cbx_datastore.current_datastore_id()
                )

                execution_list = manager.get_upload_checks_execution(
                    datastore_id=datastore_id, upload_id=self.created_upload_id
                )

            except UnavailableUploadException as exc:
                self._report_processing_error(self.tr("Upload check status"), str(exc))
        return execution_list

    def _check_vector_stored_data_creation(self) -> Execution:
        """
        Check if stored data creation is done and return processing execution
        If stored data is generated, stop check timer

        Returns: [Execution] database integration processing execution

        """
        execution = None
        if self.update_feedback.created_vector_db_id:
            self.created_vector_db_stored_data_id = (
                self.update_feedback.created_vector_db_id
            )
            try:
                stored_data_manager = StoredDataRequestManager()
                processing_manager = ProcessingRequestManager()
                datastore_id = (
                    self.qwp_upload_edition.cbx_datastore.current_datastore_id()
                )
                stored_data = stored_data_manager.get_stored_data(
                    datastore_id=datastore_id,
                    stored_data_id=self.created_vector_db_stored_data_id,
                )

                if (
                    stored_data.tags is not None
                    and "proc_int_id" in stored_data.tags.keys()
                ):
                    execution = processing_manager.get_execution(
                        datastore_id=datastore_id,
                        exec_id=stored_data.tags["proc_int_id"],
                    )
            except (
                UnavailableProcessingException,
                UnavailableStoredData,
            ) as exc:
                self._report_processing_error(
                    self.tr("Stored data database integration check"), str(exc)
                )
        return execution

    def _check_pyramid_stored_data_creation(self) -> Execution:
        """
        Check if stored data creation is done and return processing execution
        If stored data is generated, stop check timer

        Returns: [Execution] database integration processing execution

        """
        execution = None
        if self.created_pyramid_stored_data_id:
            try:
                stored_data_manager = StoredDataRequestManager()
                processing_manager = ProcessingRequestManager()
                datastore_id = (
                    self.qwp_upload_edition.cbx_datastore.current_datastore_id()
                )
                stored_data = stored_data_manager.get_stored_data(
                    datastore_id=datastore_id,
                    stored_data_id=self.created_pyramid_stored_data_id,
                )

                if (
                    stored_data.tags is not None
                    and "proc_pyr_creat_id" in stored_data.tags.keys()
                ):
                    execution = processing_manager.get_execution(
                        datastore_id=datastore_id,
                        exec_id=stored_data.tags["proc_pyr_creat_id"],
                    )

                if stored_data.status == "GENERATED":
                    self.update_check_timer.stop()
            except (
                UnavailableProcessingException,
                UnavailableStoredData,
            ) as exc:
                self._report_processing_error(
                    self.tr("Stored data pyramid creation check"), str(exc)
                )
        return execution

    def validatePage(self) -> bool:
        """
        Validate current page content : return True

        Returns: True

        """
        result = True

        if not self.created_upload_id and not self.processing_failed:
            result = False
            QMessageBox.warning(
                self,
                self.tr("Upload not finished."),
                self.tr(
                    "Upload not finished. You must wait for data upload before closing this dialog."
                ),
            )
        elif not self.created_vector_db_stored_data_id and not self.processing_failed:
            result = False
            QMessageBox.warning(
                self,
                self.tr("Database integration not finished."),
                self.tr(
                    "Database integration not finished. You must wait for database integration before closing this "
                    "dialog."
                ),
            )
        elif not self.created_pyramid_stored_data_id and not self.processing_failed:
            result = False
            QMessageBox.warning(
                self,
                self.tr("Tile creation not finished."),
                self.tr(
                    "Tile creation not finished. You must wait for tile creation before closing this "
                    "dialog."
                ),
            )
        if result:
            self.update_check_timer.stop()

        return result

    def isComplete(self) -> bool:
        """
        Check if QWizardPage is complete for next/finish button enable.
        Here we check that update tile upload is finish.

        Returns: True if update tile upload is finish. False otherwise

        """
        result = True
        if not self.created_upload_id and not self.processing_failed:
            result = False
        elif not self.created_vector_db_stored_data_id and not self.processing_failed:
            result = False
        elif not self.created_pyramid_stored_data_id and not self.processing_failed:
            result = False

        return result

    def _stop_timer_and_display_error(self, error: str) -> None:
        self.update_check_timer.stop()
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
        params: dict,
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
