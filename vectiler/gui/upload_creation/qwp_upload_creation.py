# standard

import os
from functools import partial

from PyQt5.QtCore import QByteArray, QTimer
from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtWidgets import QHeaderView, QMessageBox, QWizardPage

# PyQGIS
from qgis.core import (
    QgsApplication,
    QgsProcessingAlgorithm,
    QgsProcessingAlgRunnerTask,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsTask,
)
from qgis.PyQt import uic

from vectiler.__about__ import DIR_PLUGIN_ROOT
from vectiler.api.execution import Execution
from vectiler.api.processing import ProcessingRequestManager
from vectiler.api.stored_data import StoredDataRequestManager
from vectiler.api.upload import UploadRequestManager
from vectiler.gui.mdl_execution_list import ExecutionListModel
from vectiler.gui.upload_creation.qwp_upload_edition import UploadEditionPageWizard
from vectiler.processing import VectilerProvider
from vectiler.processing.upload_creation import UploadCreationAlgorithm
from vectiler.processing.upload_database_integration import (
    UploadDatabaseIntegrationAlgorithm,
)
from vectiler.toolbelt import PlgLogger


class UploadCreationPageWizard(QWizardPage):
    STATUS_CHECK_INTERVAL = 500

    def __init__(self, qwp_upload_edition: UploadEditionPageWizard, parent=None):

        """
        QWizardPage to define create upload to geotuileur platform

        Args:
            parent: parent QObject
        """

        super().__init__(parent)
        self.log = PlgLogger().log
        self.qwp_upload_edition = qwp_upload_edition

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "qwp_upload_creation.ui"), self
        )

        # Task ID and feedback for upload creation
        self.upload_task_id = None
        self.upload_feedback = QgsProcessingFeedback()

        # Task ID and feedback for database integration
        self.integrate_task_id = None
        self.integrate_feedback = QgsProcessingFeedback()

        # Processing results
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
        self.upload_task_id = None
        self.integrate_task_id = None

        self.created_upload_id = ""
        self.created_stored_data_id = ""

        self.mdl_execution_list.set_execution_list([])
        self.upload()

    def upload(self) -> None:
        """
        Run UploadCreationAlgorithm with UploadEditionPageWizard parameters

        """
        self.log(f"Launch UploadCreationAlgorithm")
        algo_str = f"{VectilerProvider().id()}:{UploadCreationAlgorithm().name()}"
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)

        params = {
            UploadCreationAlgorithm.DATASTORE: self.qwp_upload_edition.cbx_datastore.current_datastore_id(),
            UploadCreationAlgorithm.NAME: self.qwp_upload_edition.lne_data.text(),
            UploadCreationAlgorithm.DESCRIPTION: self.qwp_upload_edition.lne_data.text(),
            UploadCreationAlgorithm.SRS: self.qwp_upload_edition.psw_projection.crs(),
            UploadCreationAlgorithm.INPUT_LAYERS: self.qwp_upload_edition.get_filenames(),
        }
        self.lbl_step_text.setText(
            self.tr("Vérification et intégration des données en cours")
        )
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
            msgBox = QMessageBox(
                QMessageBox.Warning,
                self.tr("Upload creation failed"),
                self.tr("Check details for more informations"),
            )
            msgBox.setDetailedText(self.upload_feedback.textLog())
            msgBox.exec()

    def check_upload_status(self):
        """
        Check upload status and run database integration if upload closed

        """
        execution_list = self._check_upload_creation()

        if self.created_stored_data_id:
            execution_list.append(self._check_stored_data_creation())

        self.mdl_execution_list.set_execution_list(execution_list)

    def _check_upload_creation(self) -> [Execution]:
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
                status = manager.get_upload_status(
                    datastore=datastore_id, upload=self.created_upload_id
                )

                execution_list = manager.get_upload_checks_execution(
                    datastore=datastore_id, upload=self.created_upload_id
                )

                # Run database integration
                if status == "CLOSED":
                    self.integrate()

            except UploadRequestManager.UnavailableUploadException as exc:
                msgBox = QMessageBox(
                    QMessageBox.Warning,
                    self.tr("Upload check status failed"),
                    self.tr("Check details for more informations"),
                )
                msgBox.setDetailedText(str(exc))
                msgBox.exec()
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
                if stored_data.status == "GENERATED":
                    self.upload_check_timer.stop()
                    self.loading_movie.stop()
                    self.lbl_step_text.setText(self.tr("Votre données est prête"))
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
            except ProcessingRequestManager.UnavailableProcessingException as exc:
                msgBox = QMessageBox(
                    QMessageBox.Warning,
                    self.tr("Stored data database integration check failed"),
                    self.tr("Check details for more informations"),
                )
                msgBox.setDetailedText(str(exc))
                msgBox.exec()
            except StoredDataRequestManager.UnavailableStoredData as exc:
                msgBox = QMessageBox(
                    QMessageBox.Warning,
                    self.tr("Stored data database integration check failed"),
                    self.tr("Check details for more informations"),
                )
                msgBox.setDetailedText(str(exc))
                msgBox.exec()
        return execution

    def integrate(self):
        """
        Run UploadDatabaseIntegrationAlgorithm

        """
        # Run database integration only if created upload available and no integrate task running
        if self.created_upload_id and not self.integrate_task_id:
            self.log(f"Launch UploadDatabaseIntegrationAlgorithm")
            algo_str = f"{VectilerProvider().id()}:{UploadDatabaseIntegrationAlgorithm().name()}"
            alg = QgsApplication.processingRegistry().algorithmById(algo_str)

            params = {
                UploadDatabaseIntegrationAlgorithm.DATASTORE: self.qwp_upload_edition.cbx_datastore.current_datastore_id(),
                UploadDatabaseIntegrationAlgorithm.UPLOAD: self.created_upload_id,
                UploadDatabaseIntegrationAlgorithm.STORED_DATA_NAME: self.qwp_upload_edition.lne_data.text(),
            }

            self.integrate_task_id = self._run_alg(
                alg, params, self.integrate_feedback, self.integrate_finished
            )

    def integrate_finished(self, context, successful, results):
        """
        Callback executed when UploadDatabaseIntegrationAlgorithm is finished

        Args:
            context:  algorithm context
            successful: algorithm success
            results: algorithm results
        """

        if successful:
            self.created_stored_data_id = results[
                UploadDatabaseIntegrationAlgorithm.CREATED_STORED_DATA_ID
            ]
        else:
            msgBox = QMessageBox(
                QMessageBox.Warning,
                self.tr("Database integration failed"),
                self.tr("Check details for more informations"),
            )
            msgBox.setDetailedText(self.integrate_feedback.textLog())
            msgBox.exec()

    def validatePage(self) -> bool:
        """
        Validate current page content : return True

        Returns: True

        """
        return True

    @staticmethod
    def _run_alg(
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
