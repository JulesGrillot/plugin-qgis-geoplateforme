# standard

import os
from functools import partial

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWizardPage, QMessageBox, QHeaderView
from qgis.PyQt import uic

# PyQGIS
from qgis.core import (
    QgsApplication,
    QgsProcessingContext,
    QgsProcessingAlgRunnerTask,
    QgsTask,
    QgsProcessingFeedback,
    QgsProcessingAlgorithm
)

from vectiler.api.upload import UploadRequestManager
from vectiler.gui.mdl_execution_list import ExecutionListModel
from vectiler.gui.upload_creation.qwp_upload_edition import UploadEditionPageWizard
from vectiler.processing import VectilerProvider
from vectiler.processing.upload_creation import UploadCreationAlgorithm
from vectiler.processing.upload_database_integration import UploadDatabaseIntegrationAlgorithm


class UploadCreationPageWizard(QWizardPage):
    def __init__(self, qwp_upload_edition: UploadEditionPageWizard, parent=None):

        """
        QWizardPage to define create upload to geotuileur platform

        Args:
            parent: parent QObject
        """

        super().__init__(parent)
        self.qwp_upload_edition = qwp_upload_edition

        uic.loadUi(os.path.join(os.path.dirname(__file__), "qwp_upload_creation.ui"), self)

        # Task and feedback for upload creation
        self.upload_task = None
        self.upload_feedback = QgsProcessingFeedback()

        # Task and feedback for database integration
        self.integrate_task = None
        self.integrate_feedback = QgsProcessingFeedback()

        # Processing results
        self.created_upload_id = ""
        self.created_stored_data_id = ""

        # Timer for upload check after upload creation
        self.upload_check_timer = QTimer(self)
        self.upload_check_timer.timeout.connect(self.check_upload_status)

        # Model for executions display
        self.mdl_execution_list = ExecutionListModel(self)
        self.tableview_execution_list.setModel(self.mdl_execution_list)
        self.tableview_execution_list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.initializePage()

    def initializePage(self) -> None:
        """
        Initialize page before show.

        """
        self._disconnect_btn(self.btn_upload)
        self.btn_upload.clicked.connect(self.upload)
        self.btn_upload.setIcon(QIcon(QgsApplication.iconPath('mActionStart.svg')))
        self.btn_upload.setEnabled(True)

        self._disconnect_btn(self.btn_integrate)
        self.btn_integrate.clicked.connect(self.integrate)
        self.btn_integrate.setIcon(QIcon(QgsApplication.iconPath('mActionStart.svg')))
        self.btn_integrate.setToolTip(self.tr("Upload not created. Can't integrate in database"))
        self.btn_integrate.setEnabled(False)

        self.created_upload_id = ""
        self.created_stored_data_id = ""

    def upload(self) -> None:
        """
        Run UploadCreationAlgorithm with UploadEditionPageWizard parameters

        """
        algo_str = f'{VectilerProvider().id()}:{UploadCreationAlgorithm().name()}'
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)

        params = {UploadCreationAlgorithm.DATASTORE: self.cbx_datastore.current_datastore_id(),
                  UploadCreationAlgorithm.NAME: self.qwp_upload_edition.lne_data.text(),
                  UploadCreationAlgorithm.DESCRIPTION: self.qwp_upload_edition.lne_data.text(),
                  UploadCreationAlgorithm.SRS: self.qwp_upload_edition.psw_projection.crs(),
                  UploadCreationAlgorithm.INPUT_LAYERS: self.qwp_upload_edition.get_filenames()}

        self.upload_task = self._run_alg(alg, params, self.upload_feedback, self.upload_finished, self.btn_upload)

    def upload_finished(self, context, successful, results):
        """
        Callback executed when UploadCreationAlgorithm is finished

        Args:
            context:  algorithm context
            successful: algorithm success
            results: algorithm results
        """
        self._disconnect_btn(self.btn_upload)
        if successful:
            self.created_upload_id = results[UploadCreationAlgorithm.CREATED_UPLOAD_ID]
            self.btn_upload.setEnabled(False)
            self.btn_upload.setToolTip(self.tr("Upload already created"))
            # Run timer for upload check
            self.upload_check_timer.start(300)
        else:
            self.btn_upload.setIcon(QIcon(QgsApplication.iconPath('mActionStart.svg')))
            self.btn_upload.clicked.connect(self.upload)
            msgBox = QMessageBox(QMessageBox.Warning,
                                 self.tr("Upload creation failed"),
                                 self.tr("Check details for more informations"))
            msgBox.setDetailedText(self.upload_feedback.textLog())
            msgBox.exec()

    def check_upload_status(self):
        """
        Check upload status and run database integration if upload closed

        """
        if self.created_upload_id:
            try:
                manager = UploadRequestManager()
                datastore_id = self.cbx_datastore.current_datastore_id()
                status = manager.get_upload_status(datastore=datastore_id, upload=self.created_upload_id)

                # Run integration and stop timer if upload closed
                if status == "CLOSED":
                    self.upload_check_timer.stop()
                    self.btn_integrate.setEnabled(True)
                    self.btn_integrate.setToolTip("")
                    self.integrate()

                execution_list = manager.get_upload_checks_execution(datastore=datastore_id,
                                                                     upload=self.created_upload_id)
                self.mdl_execution_list.set_execution_list(execution_list)

                # Expand all items
                self.tableview_execution_list.resizeColumnToContents(0)
                self.tableview_execution_list.resizeColumnToContents(1)

            except UploadRequestManager.UnavailableUploadException as exc:
                msgBox = QMessageBox(QMessageBox.Warning,
                                     self.tr("Upload check status failed"),
                                     self.tr("Check details for more informations"))
                msgBox.setDetailedText(str(exc))
                msgBox.exec()

    def integrate(self):
        """
        Run UploadDatabaseIntegrationAlgorithm

        """
        if self.created_upload_id:
            algo_str = f'{VectilerProvider().id()}:{UploadDatabaseIntegrationAlgorithm().name()}'
            alg = QgsApplication.processingRegistry().algorithmById(algo_str)

            params = {UploadDatabaseIntegrationAlgorithm.DATASTORE: self.cbx_datastore.current_datastore_id(),
                      UploadDatabaseIntegrationAlgorithm.UPLOAD: self.created_upload_id,
                      UploadDatabaseIntegrationAlgorithm.STORED_DATA_NAME: self.qwp_upload_edition.lne_data.text()}

            self.integrate_task = self._run_alg(alg, params, self.integrate_feedback, self.integrate_finished,
                                                self.btn_integrate)

    def integrate_finished(self, context, successful, results):
        """
        Callback executed when UploadDatabaseIntegrationAlgorithm is finished

        Args:
            context:  algorithm context
            successful: algorithm success
            results: algorithm results
        """

        self._disconnect_btn(self.btn_integrate)
        if successful:
            self.created_stored_data_id = results[UploadDatabaseIntegrationAlgorithm.CREATED_STORED_DATA_ID]

            self.btn_integrate.setEnabled(False)
            self.btn_integrate.setToolTip(self.tr("Database integration already done"))
        else:
            self.btn_integrate.setIcon(QIcon(QgsApplication.iconPath('mActionStart.svg')))
            self.btn_integrate.clicked.connect(self.integrate)
            msgBox = QMessageBox(QMessageBox.Warning,
                                 self.tr("Database integration failed"),
                                 self.tr("Check details for more informations"))
            msgBox.setDetailedText(self.integrate_feedback.textLog())
            msgBox.exec()

    def _run_alg(self,
                 alg: QgsProcessingAlgorithm, params: {},
                 feedback: QgsProcessingFeedback,
                 executed_callback,
                 btn=None) -> QgsTask:
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
        QgsApplication.taskManager().addTask(task)
        if btn:
            self._disconnect_btn(btn)
            btn.setIcon(QIcon(QgsApplication.iconPath('mActionStop.svg')))
            btn.clicked.connect(task.cancel)
        return task

    @staticmethod
    def _disconnect_btn(btn) -> None:
        try:
            btn.disconnect()
        except Exception:
            pass

    def validatePage(self) -> bool:
        """
        Validate current page content : Always returns true

        Returns: True

        """
        return True
