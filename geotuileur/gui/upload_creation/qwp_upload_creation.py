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

from geotuileur.__about__ import DIR_PLUGIN_ROOT
from geotuileur.api.check import CheckExecution
from geotuileur.api.processing import Execution, ProcessingRequestManager
from geotuileur.api.stored_data import StoredDataRequestManager, StoredDataStatus
from geotuileur.api.upload import UploadRequestManager, UploadStatus
from geotuileur.gui.mdl_execution_list import ExecutionListModel
from geotuileur.gui.upload_creation.qwp_upload_edition import UploadEditionPageWizard
from geotuileur.processing import GeotuileurProvider
from geotuileur.processing.upload_creation import UploadCreationAlgorithm
from geotuileur.processing.upload_database_integration import (
    UploadDatabaseIntegrationAlgorithm,
)
from geotuileur.toolbelt import PlgLogger


class UploadCreationPageWizard(QWizardPage):
    STATUS_CHECK_INTERVAL = 500

    def __init__(self, qwp_upload_edition: UploadEditionPageWizard, parent=None):

        """
        QWizardPage to define create upload to geotuileur platform

        Args:
            parent: parent QObject
        """

        super().__init__(parent)
        self.setTitle(self.tr("Checking and integration of your data in progress"))
        self.log = PlgLogger().log
        self.qwp_upload_edition = qwp_upload_edition

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "qwp_upload_creation.ui"), self
        )

        self.tbw_errors.setVisible(False)

        # Task ID and feedback for upload creation
        self.upload_task_id = None
        self.upload_feedback = QgsProcessingFeedback()

        # Processing results
        self.processing_failed = False
        self.created_upload_id = ""
        self.created_stored_data_id = ""

        # Timer for upload check after upload creation
        self.loading_movie = QMovie(
            str(DIR_PLUGIN_ROOT / "resources" / "images" / "loading.gif"),
            QByteArray(),
            self,
        )
        self.upload_check_timer = QTimer(self)
        self.upload_check_timer.timeout.connect(self.check_upload_status)

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
        self.tbw_errors.setVisible(False)
        self.upload_task_id = None

        # Processing results
        self.processing_failed = False
        self.created_upload_id = ""
        self.created_stored_data_id = ""

        self.mdl_execution_list.clear_executions()
        self.upload()

    def upload(self) -> None:
        """
        Run UploadCreationAlgorithm with UploadEditionPageWizard parameters

        """
        self.log("Launch UploadCreationAlgorithm")
        algo_str = f"{GeotuileurProvider().id()}:{UploadCreationAlgorithm().name()}"
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)

        data = {
            UploadCreationAlgorithm.DATASTORE: self.qwp_upload_edition.cbx_datastore.current_datastore_id(),
            UploadCreationAlgorithm.NAME: self.qwp_upload_edition.wdg_upload_creation.get_name(),
            UploadCreationAlgorithm.DESCRIPTION: self.qwp_upload_edition.wdg_upload_creation.get_name(),
            UploadCreationAlgorithm.SRS: self.qwp_upload_edition.wdg_upload_creation.get_crs(),
            UploadCreationAlgorithm.FILES: self.qwp_upload_edition.wdg_upload_creation.get_filenames(),
        }
        filename = tempfile.NamedTemporaryFile(suffix=".json").name
        with open(filename, "w") as file:
            json.dump(data, file)
            params = {UploadCreationAlgorithm.INPUT_JSON: filename}
            self.lbl_step_icon.setMovie(self.loading_movie)
            self.loading_movie.start()

            self.upload_task_id = self._run_alg(
                alg, params, self.upload_feedback, self.upload_finished
            )

    def upload_finished(self, context, successful, results):
        """
        Callback executed when UploadCreationAlgorithm is finished

        Args:
            context:  algorithm context
            successful: algorithm success
            results: algorithm results
        """
        if successful:
            self.created_upload_id = results[UploadCreationAlgorithm.CREATED_UPLOAD_ID]

            # Run timer for upload check
            self.upload_check_timer.start(self.STATUS_CHECK_INTERVAL)
        else:
            self._report_processing_error(
                self.tr("Upload creation"), self.upload_feedback.textLog()
            )

    def check_upload_status(self):
        """
        Check upload status and run database integration if upload closed

        """
        self.mdl_execution_list.clear_executions()
        self.mdl_execution_list.set_check_execution_list(self._check_upload_creation())

        execution = self._check_stored_data_creation()
        if execution:
            self.mdl_execution_list.set_execution_list([execution])

    def _check_upload_creation(self) -> List[CheckExecution]:
        """
        Check if upload creation check are done and return checks execution.
        Il upload is closed, launch database integration

        Returns: [Execution] upload checks Execution

        """
        execution_list = []
        if self.created_upload_id:
            try:
                manager = UploadRequestManager()
                datastore_id = (
                    self.qwp_upload_edition.cbx_datastore.current_datastore_id()
                )
                upload = manager.get_upload(
                    datastore=datastore_id, upload=self.created_upload_id
                )

                execution_list = manager.get_upload_checks_execution(
                    datastore=datastore_id, upload=self.created_upload_id
                )
                status = UploadStatus[upload.status]
                # Run database integration
                if status == UploadStatus.CLOSED:
                    self.integrate()
                elif status == UploadStatus.UNSTABLE:
                    self._stop_timer_and_display_error(
                        self.tr(
                            "Upload creation failed. Check report in dashboard for "
                            "more details."
                        )
                    )

            except UploadRequestManager.UnavailableUploadException as exc:
                self._report_processing_error(self.tr("Upload check status"), str(exc))
        return execution_list

    def _check_stored_data_creation(self) -> Execution:
        """
        Check if stored data creation is done and return processing execution
        If stored data is generated, stop check timer

        Returns: [Execution] database integration processing execution

        """
        execution = None
        if self.created_stored_data_id:
            try:
                stored_data_manager = StoredDataRequestManager()
                processing_manager = ProcessingRequestManager()
                datastore_id = (
                    self.qwp_upload_edition.cbx_datastore.current_datastore_id()
                )
                stored_data = stored_data_manager.get_stored_data(
                    datastore=datastore_id, stored_data=self.created_stored_data_id
                )

                if (
                    stored_data.tags is not None
                    and "proc_int_id" in stored_data.tags.keys()
                ):
                    execution = processing_manager.get_execution(
                        datastore=datastore_id, exec_id=stored_data.tags["proc_int_id"]
                    )
                # Stop timer if stored_data generated
                status = StoredDataStatus[stored_data.status]
                if status == StoredDataStatus.GENERATED:
                    self.upload_check_timer.stop()
                    self.loading_movie.stop()
                    self.setTitle(
                        self.tr("Your data has been stored on the remote storage.")
                    )
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

            except (
                ProcessingRequestManager.UnavailableProcessingException,
                StoredDataRequestManager.UnavailableStoredData,
            ) as exc:
                self._report_processing_error(
                    self.tr("Stored database integration check"), str(exc)
                )
        return execution

    def integrate(self):
        """
        Run UploadDatabaseIntegrationAlgorithm

        """
        # Run database integration only if created upload available and no integrate task running
        if self.created_upload_id and not self.created_stored_data_id:

            # Stop timer for upload check during processing to avoid multiple integration launch
            self.upload_check_timer.stop()

            self.log("Launch UploadDatabaseIntegrationAlgorithm")
            algo_str = f"{GeotuileurProvider().id()}:{UploadDatabaseIntegrationAlgorithm().name()}"
            alg = QgsApplication.processingRegistry().algorithmById(algo_str)

            data = {
                UploadDatabaseIntegrationAlgorithm.DATASTORE: self.qwp_upload_edition.cbx_datastore.current_datastore_id(),
                UploadDatabaseIntegrationAlgorithm.UPLOAD: self.created_upload_id,
                UploadDatabaseIntegrationAlgorithm.STORED_DATA_NAME: self.qwp_upload_edition.wdg_upload_creation.get_name(),
            }
            filename = tempfile.NamedTemporaryFile(suffix=".json").name
            with open(filename, "w") as file:
                json.dump(data, file)

            params = {UploadDatabaseIntegrationAlgorithm.INPUT_JSON: filename}

            context = QgsProcessingContext()
            feedback = QgsProcessingFeedback()
            results, successful = alg.run(params, context, feedback)

            if successful:
                self.created_stored_data_id = results[
                    UploadDatabaseIntegrationAlgorithm.CREATED_STORED_DATA_ID
                ]

                # Start timer for upload check
                self.upload_check_timer.start(self.STATUS_CHECK_INTERVAL)
                self.loading_movie.start()

                # Emit completeChanged to update finish button
                self.completeChanged.emit()
            else:
                self._report_processing_error(
                    self.tr("Database integration"), feedback.textLog()
                )

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
        elif not self.created_stored_data_id and not self.processing_failed:
            result = False
            QMessageBox.warning(
                self,
                self.tr("Database integration not finished."),
                self.tr(
                    "Database integration not finished. You must wait for database integration before closing this "
                    "dialog."
                ),
            )

        return result

    def isComplete(self) -> bool:
        """
        Check if QWizardPage is complete for next/finish button enable.
        Here we check that upload was created.

        Returns: True if upload was created, False otherwise

        """
        result = True
        if not self.created_upload_id and not self.processing_failed:
            result = False
        elif not self.created_upload_id and not self.processing_failed:
            result = False

        return result

    def _stop_timer_and_display_error(self, error: str) -> None:
        self.upload_check_timer.stop()
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
