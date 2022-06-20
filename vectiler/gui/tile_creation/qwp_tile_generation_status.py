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

from vectiler.api.processing import ProcessingRequestManager
from vectiler.api.stored_data import StoredDataRequestManager
from vectiler.api.upload import UploadRequestManager
from vectiler.gui.mdl_execution_list import ExecutionListModel
from vectiler.gui.tile_creation.qwp_tile_generation_edition import TileGenerationEditionPageWizard
from vectiler.gui.tile_creation.qwp_tile_generation_fields_selection import TileGenerationFieldsSelectionPageWizard
from vectiler.gui.tile_creation.qwp_tile_generation_generalization import TileGenerationGeneralizationPageWizard
from vectiler.processing import VectilerProvider
from vectiler.processing.tile_creation import TileCreationAlgorithm


class TileGenerationStatusPageWizard(QWizardPage):
    def __init__(self, qwp_tile_generation_edition: TileGenerationEditionPageWizard,
                 qwp_tile_generation_fields_selection: TileGenerationFieldsSelectionPageWizard,
                 qwp_tile_generation_generalization: TileGenerationGeneralizationPageWizard, parent=None):

        """
        QWizardPage to create tile vector

        Args:
            parent: parent QObject
        """

        super().__init__(parent)
        self.qwp_tile_generation_edition = qwp_tile_generation_edition
        self.qwp_tile_generation_fields_selection = qwp_tile_generation_fields_selection
        self.qwp_tile_generation_generalization = qwp_tile_generation_generalization

        uic.loadUi(os.path.join(os.path.dirname(__file__), "qwp_tile_generation_status.ui"), self)

        # Task and feedback for tile creation
        self.create_tile_task = None
        self.create_tile_feedback = QgsProcessingFeedback()

        # Processing results
        self.created_stored_data_id = ""

        # Timer for processing execution check after tile creation
        self.create_tile_check_timer = QTimer(self)
        self.create_tile_check_timer.timeout.connect(self.check_create_tile_status)

        # Model for executions display
        self.mdl_execution_list = ExecutionListModel(self)
        self.tableview_execution_list.setModel(self.mdl_execution_list)

        self.tableview_execution_list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.initializePage()

    def initializePage(self) -> None:
        """
        Initialize page before show.

        """
        self._disconnect_btn(self.btn_create)
        self.btn_create.clicked.connect(self.create_tile)
        self.btn_create.setIcon(QIcon(QgsApplication.iconPath('mActionStart.svg')))
        self.btn_create.setEnabled(True)

        self.created_stored_data_id = ""

    def create_tile(self) -> None:
        """
        Run TileCreationAlgorithm with parameters defined from previous QWizardPage

        """
        algo_str = f'{VectilerProvider().id()}:{TileCreationAlgorithm().name()}'
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)

        datastore_id = self.qwp_tile_generation_edition.cbx_datastore.current_datastore_id()
        vector_db_stored_id = self.qwp_tile_generation_edition.cbx_stored_data.current_stored_data_id()

        params = {TileCreationAlgorithm.DATASTORE: datastore_id,
                  TileCreationAlgorithm.VECTOR_DB_STORED_DATA_ID: vector_db_stored_id,
                  TileCreationAlgorithm.STORED_DATA_NAME: self.qwp_tile_generation_edition.lne_flux.text(),
                  TileCreationAlgorithm.TIPPECANOE_OPTIONS: self.qwp_tile_generation_generalization.get_tippecanoe_value(),
                  TileCreationAlgorithm.TMS: 0,
                  TileCreationAlgorithm.BOTTOM_LEVEL: self.qwp_tile_generation_edition.get_bottom_level(),
                  TileCreationAlgorithm.TOP_LEVEL: self.qwp_tile_generation_edition.get_top_level(),
                  TileCreationAlgorithm.ATTRIBUTES: self.qwp_tile_generation_fields_selection.get_selected_attributes(),
                  }

        self.create_tile_task = self._run_alg(alg, params, self.create_tile_feedback, self.create_tile_finished,
                                              self.btn_create)

    def create_tile_finished(self, context, successful, results):
        """
        Callback executed when TileCreationAlgorithm is finished

        Args:
            context:  algorithm context
            successful: algorithm success
            results: algorithm results
        """
        self._disconnect_btn(self.btn_create)
        if successful:
            self.created_stored_data_id = results[TileCreationAlgorithm.CREATED_STORED_DATA_ID]
            self.btn_create.setEnabled(False)
            self.btn_create.setToolTip(self.tr("Tile already created"))
            # Run timer for upload check
            self.create_tile_check_timer.start(300)
        else:
            self.btn_create.setIcon(QIcon(QgsApplication.iconPath('mActionStart.svg')))
            self.btn_create.clicked.connect(self.create_tile)
            msgBox = QMessageBox(QMessageBox.Warning,
                                 self.tr("Tile creation failed"),
                                 self.tr("Check details for more informations"))
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
                datastore_id = self.qwp_tile_generation_edition.cbx_datastore.current_datastore_id()

                stored_data = stored_data_manager.get_stored_data(datastore=datastore_id,
                                                                  stored_data=self.created_stored_data_id)

                execution_list = []
                if stored_data.tags and "upload_id" in stored_data.tags.keys():
                    execution_list = upload_manager.get_upload_checks_execution(datastore=datastore_id,
                                                                                upload=stored_data.tags["upload_id"])

                # Stop timer if stored_data generated
                if stored_data.status == "GENERATED":
                    self.create_tile_check_timer.stop()
                if stored_data.tags is not None and "proc_pyr_creat_id" in stored_data.tags.keys():
                    execution_list.append(processing_manager.get_execution(datastore=datastore_id,
                                                                           exec_id=stored_data.tags[
                                                                               "proc_pyr_creat_id"])
                                          )
                self.mdl_execution_list.set_execution_list(execution_list)
            except StoredDataRequestManager.UnavailableStoredData as exc:
                msgBox = QMessageBox(QMessageBox.Warning,
                                     self.tr("Stored data check status failed"),
                                     self.tr("Check details for more informations"))
                msgBox.setDetailedText(str(exc))
                msgBox.exec()
            except ProcessingRequestManager.UnavailableProcessingException as exc:
                msgBox = QMessageBox(QMessageBox.Warning,
                                     self.tr("Stored data check status failed"),
                                     self.tr("Check details for more informations"))
                msgBox.setDetailedText(str(exc))
                msgBox.exec()
            except UploadRequestManager.UnavailableUploadException as exc:
                msgBox = QMessageBox(QMessageBox.Warning,
                                     self.tr("Stored data check status failed"),
                                     self.tr("Check details for more informations"))
                msgBox.setDetailedText(str(exc))
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
