# standard
import os
from functools import partial
from typing import List, Optional

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

from geoplateforme.__about__ import DIR_PLUGIN_ROOT
from geoplateforme.api.check import CheckExecution
from geoplateforme.api.custom_exceptions import (
    UnavailableProcessingException,
    UnavailableStoredData,
    UnavailableUploadException,
)
from geoplateforme.api.processing import Execution, ProcessingRequestManager
from geoplateforme.api.stored_data import StoredDataRequestManager, StoredDataStatus
from geoplateforme.api.upload import UploadRequestManager
from geoplateforme.gui.mdl_execution_list import ExecutionListModel
from geoplateforme.gui.upload_creation.qwp_upload_edition import UploadEditionPageWizard
from geoplateforme.processing import GeoplateformeProvider
from geoplateforme.processing.utils import tags_to_qgs_parameter_matrix_string
from geoplateforme.processing.vector_db_creation import (
    VectorDatabaseCreationAlgorithm,
    VectorDatabaseCreationProcessingFeedback,
)
from geoplateforme.toolbelt import PlgLogger, PlgOptionsManager


class UploadCreationPageWizard(QWizardPage):
    def __init__(self, qwp_upload_edition: UploadEditionPageWizard, parent=None):
        """
        QWizardPage to define create upload to geoplateforme platform

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
        self.create_vector_db_task_id = None
        self.create_vector_db_feedback = VectorDatabaseCreationProcessingFeedback()

        # Processing results
        self.processing_failed = False
        self.created_upload_id = ""
        self.upload_check_execution_list: List[CheckExecution] = []
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
            QHeaderView.ResizeMode.ResizeToContents
        )

    def initializePage(self) -> None:
        """
        Initialize page before show.

        """
        self.tbw_errors.setVisible(False)
        self.create_vector_db_task_id = None

        # Processing results
        self.processing_failed = False
        self.created_upload_id = ""
        self.upload_check_execution_list = []
        self.created_stored_data_id = ""

        self.mdl_execution_list.clear_executions()
        self._create_vector_db()

    def _create_vector_db(self) -> None:
        """
        Run VectorDatabaseCreationAlgorithm with UploadCreatePageWizard parameters

        """
        algo_str = (
            f"{GeoplateformeProvider().id()}:{VectorDatabaseCreationAlgorithm().name()}"
        )
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)

        params = {
            VectorDatabaseCreationAlgorithm.DATASTORE: self.qwp_upload_edition.cbx_datastore.current_datastore_id(),
            VectorDatabaseCreationAlgorithm.NAME: self.qwp_upload_edition.wdg_upload_creation.get_name(),
            # TODO : add option for reprojection VectorDatabaseCreationAlgorithm.SRS: self.qwp_upload_edition.wdg_upload_creation.get_crs(),
            VectorDatabaseCreationAlgorithm.FILES: ";".join(
                self.qwp_upload_edition.wdg_upload_creation.get_filenames()
            ),
            VectorDatabaseCreationAlgorithm.LAYERS: self.qwp_upload_edition.wdg_upload_creation.get_layers(),
            VectorDatabaseCreationAlgorithm.TAGS: tags_to_qgs_parameter_matrix_string(
                {
                    "datasheet_name": self.qwp_upload_edition.wdg_upload_creation.get_dataset_name()
                }
            ),
            VectorDatabaseCreationAlgorithm.SRS: self.qwp_upload_edition.wdg_upload_creation.get_crs(),
        }
        self.lbl_step_icon.setMovie(self.loading_movie)
        self.loading_movie.start()

        self.create_vector_db_task_id = self._run_alg(
            alg,
            params,
            self.create_vector_db_feedback,
            self._vector_db_creation_finished,
        )

        # Run timer for upload check
        self.upload_check_timer.start(
            int(PlgOptionsManager.get_plg_settings().status_check_sleep * 1000.0)
        )

    def _vector_db_creation_finished(self, context, successful, results):
        """
        Callback executed when VectorDatabaseCreationAlgorithm is finished

        Args:
            context:  algorithm context
            successful: algorithm success
            results: algorithm results
        """
        if successful:
            self.created_upload_id = results[
                VectorDatabaseCreationAlgorithm.CREATED_UPLOAD_ID
            ]
            self.created_stored_data_id = results[
                VectorDatabaseCreationAlgorithm.CREATED_STORED_DATA_ID
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
                self.tr("Vector database creation"),
                self.create_vector_db_feedback.textLog(),
            )

    def check_upload_status(self):
        """
        Check upload status and run database integration if upload closed

        """
        self.mdl_execution_list.clear_executions()

        # Don't ask again for upload check execution list if stored data is defined
        if not self.created_stored_data_id:
            self.upload_check_execution_list = self._check_upload_creation()
        self.mdl_execution_list.set_check_execution_list(
            self.upload_check_execution_list
        )

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
        if self.create_vector_db_feedback.created_upload_id:
            self.created_upload_id = self.create_vector_db_feedback.created_upload_id
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

    def _check_stored_data_creation(self) -> Optional[Execution]:
        """
        Check if stored data creation is done and return processing execution
        If stored data is generated, stop check timer

        Returns: [Execution] database integration processing execution

        """
        execution = None
        if self.create_vector_db_feedback.created_vector_db_id:
            self.created_stored_data_id = (
                self.create_vector_db_feedback.created_vector_db_id
            )
            try:
                stored_data_manager = StoredDataRequestManager()
                processing_manager = ProcessingRequestManager()
                datastore_id = (
                    self.qwp_upload_edition.cbx_datastore.current_datastore_id()
                )
                stored_data = stored_data_manager.get_stored_data(
                    datastore_id=datastore_id,
                    stored_data_id=self.created_stored_data_id,
                )

                if (
                    stored_data.tags is not None
                    and "proc_int_id" in stored_data.tags.keys()
                ):
                    execution = processing_manager.get_execution(
                        datastore_id=datastore_id,
                        exec_id=stored_data.tags["proc_int_id"],
                    )
                # Stop timer if stored_data generated
                status = stored_data.status
                if status == StoredDataStatus.GENERATED:
                    self.upload_check_timer.stop()

            except (
                UnavailableProcessingException,
                UnavailableStoredData,
            ) as exc:
                self._report_processing_error(
                    self.tr("Stored database integration check"), str(exc)
                )
        return execution

    def validatePage(self) -> bool:
        """
        Validate current page content : return True

        Returns: True if upload and vector db was created, False otherwise

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
        if result:
            self.upload_check_timer.stop()

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
        Run a QgsProcessingAlgorithm and connect execution callback

        Args:
            alg: QgsProcessingAlgorithm to run
            params: QgsProcessingAlgorithm params
            feedback: QgsProcessingFeedback
            executed_callback: executed callback after algorithm execution

        Returns: created QgsTask

        """
        context = QgsProcessingContext()
        task = QgsProcessingAlgRunnerTask(alg, params, context, feedback)
        task.executed.connect(partial(executed_callback, context))
        return QgsApplication.taskManager().addTask(task)
