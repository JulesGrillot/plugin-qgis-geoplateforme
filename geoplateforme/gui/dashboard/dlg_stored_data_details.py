import os

from qgis.core import QgsApplication, QgsProject
from qgis.PyQt import QtCore, uic
from qgis.PyQt.QtCore import QSize, Qt
from qgis.PyQt.QtGui import QCursor, QGuiApplication, QIcon, QPixmap
from qgis.PyQt.QtWidgets import (
    QAbstractItemView,
    QAction,
    QDialog,
    QHeaderView,
    QToolBar,
    QToolButton,
    QWidget,
)

from geoplateforme.__about__ import DIR_PLUGIN_ROOT
from geoplateforme.api.custom_exceptions import (
    UnavailableExecutionException,
    UnavailableStoredData,
    UnavailableUploadException,
)
from geoplateforme.api.processing import ProcessingRequestManager
from geoplateforme.api.stored_data import (
    StoredData,
    StoredDataRequestManager,
    StoredDataStatus,
    StoredDataType,
)
from geoplateforme.api.upload import UploadRequestManager
from geoplateforme.gui.mdl_table_relation import TableRelationTreeModel
from geoplateforme.gui.publication_creation.wzd_publication_creation import (
    PublicationFormCreation,
)
from geoplateforme.gui.report.mdl_stored_data_details import StoredDataDetailsModel
from geoplateforme.gui.report.wdg_execution_log import ExecutionLogWidget
from geoplateforme.gui.report.wdg_upload_log import UploadLogWidget
from geoplateforme.gui.tile_creation.wzd_tile_creation import TileCreationWizard
from geoplateforme.toolbelt import PlgLogger


class StoredDataDetailsDialog(QDialog):
    def __init__(self, parent: QWidget = None):
        """
        QDialog to display report for a stored data

        Args:
            parent: parent QWidget
        """
        super().__init__(parent)
        self.log = PlgLogger().log

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "dlg_stored_data_details.ui"),
            self,
        )

        self.setWindowTitle(self.tr("Details"))

        self._stored_data = None

        self.mdl_stored_data_details = StoredDataDetailsModel(self)
        self.tbv_details.setModel(self.mdl_stored_data_details)
        self.tbv_details.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.tbv_details.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.mdl_table_relation = TableRelationTreeModel(self)
        self.mdl_table_relation.check_state_enabled = False
        self.trv_table_relation.setModel(self.mdl_table_relation)
        self.trv_table_relation.setSortingEnabled(True)

        self.trv_table_relation.header().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.trv_table_relation.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.btn_add_extent_layer.pressed.connect(self._add_extent_layer)
        self.btn_load_report.pressed.connect(self._load_generation_report)

        # Add toolbar for stored data actions
        self.edit_toolbar = QToolBar(self)
        self.layout().setMenuBar(self.edit_toolbar)

    def set_stored_data(self, stored_data: StoredData) -> None:
        """
        Define displayed stored data

        Args:
            stored_data: StoredData
        """
        self._stored_data = stored_data
        self._set_stored_data_details(stored_data)

        # Remove all available action in toolbar
        self.edit_toolbar.clear()

        status = stored_data.status

        # Only generated stored data have actions
        if status == StoredDataStatus.GENERATED:
            # Vector DB :
            # - tile generation
            if stored_data.type == StoredDataType.VECTORDB:
                generate_tile_action = QAction(
                    QIcon(str(DIR_PLUGIN_ROOT / "resources/images/icons/Tuile@1x.png")),
                    self.tr("Génération tuile"),
                    self,
                )
                generate_tile_action.triggered.connect(
                    self._show_tile_generation_wizard
                )
                button = QToolButton(self)
                button.setDefaultAction(generate_tile_action)
                button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
                self.edit_toolbar.addWidget(button)
            elif stored_data.type == StoredDataType.PYRAMIDVECTOR:
                publish_tile_action = QAction(
                    QIcon(
                        str(
                            DIR_PLUGIN_ROOT
                            / "resources"
                            / "images"
                            / "icons"
                            / "Publie@2x.png"
                        )
                    ),
                    self.tr("Publication tuile"),
                    self,
                )
                button = QToolButton(self)
                button.setDefaultAction(publish_tile_action)
                button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

                publish_tile_action.triggered.connect(self._show_tile_publish_wizard)
                self.edit_toolbar.addWidget(button)

    def _show_tile_generation_wizard(self) -> None:
        """Show tile generation wizard for current stored data"""
        self._generate_tile_wizard(self._stored_data)

    def _generate_tile_wizard(self, stored_data: StoredData) -> None:
        """
        Show tile generation wizard for a stored data

        Args:
            stored_data: (StoredData) stored data to generate tile
        """
        QGuiApplication.setOverrideCursor(QCursor(QtCore.Qt.CursorShape.WaitCursor))
        publication_wizard = TileCreationWizard(
            self,
            stored_data.datastore_id,
            stored_data.tags["datasheet_name"],
            stored_data._id,
        )
        QGuiApplication.restoreOverrideCursor()
        publication_wizard.show()

    def _show_tile_publish_wizard(self) -> None:
        """Show tile generation wizard for current stored data"""
        self._tile_publish_wizard(self._stored_data)

    def _tile_publish_wizard(self, stored_data: StoredData) -> None:
        """
        Show publish wizard for a stored data

        Args:
            stored_data: (StoredData) stored data to publish
        """
        QGuiApplication.setOverrideCursor(QCursor(QtCore.Qt.CursorShape.WaitCursor))
        publication_wizard = PublicationFormCreation(
            self,
            stored_data.datastore_id,
            stored_data.tags["datasheet_name"],
            stored_data._id,
        )
        QGuiApplication.restoreOverrideCursor()
        publication_wizard.show()

    def _load_generation_report(self) -> None:
        """
        Define displayed stored data

        Args:
            stored_data: StoredData
        """
        QGuiApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        self._add_upload_log(self._stored_data)
        self._add_vectordb_stored_data_logs(self._stored_data)
        self._add_stored_data_execution_logs(self._stored_data)
        QGuiApplication.restoreOverrideCursor()

    def _set_stored_data_details(self, stored_data: StoredData) -> None:
        """
        Define stored data details

        Args:
            stored_data: (StoredData)
        """
        status = stored_data.status
        self.lbl_status_icon.setText("")
        self.lbl_status_icon.setPixmap(self._get_status_icon(status))
        self.lbl_status.setText(self._get_status_text(stored_data))

        self.lne_name.setText(stored_data.name)
        self.lne_id.setText(stored_data._id)
        self.mdl_stored_data_details.set_stored_data(stored_data)
        self.gpx_data_structure.setVisible(len(stored_data.get_tables()) != 0)
        self.mdl_table_relation.set_stored_data_tables(stored_data)
        vlayer = stored_data.create_extent_layer()
        self.gpx_data_extent.setVisible(vlayer.isValid())

    def _add_extent_layer(self) -> None:
        """
        Slot called for extent layer add in canvas

        """
        if self._stored_data:
            vlayer = self._stored_data.create_extent_layer()
            if vlayer.isValid():
                QgsProject.instance().addMapLayer(vlayer)

    def _add_upload_log(self, stored_data: StoredData) -> None:
        """
        Add log for stored data upload if defined

        Args:
            stored_data: StoredData
        """
        if stored_data.tags and "upload_id" in stored_data.tags:
            upload_id = stored_data.tags["upload_id"]

            try:
                manager = UploadRequestManager()
                upload = manager.get_upload(stored_data.datastore_id, upload_id)
                widget = UploadLogWidget(self)
                widget.set_upload(upload)
                self.vlayout_execution.addWidget(widget)
            except UnavailableUploadException as exc:
                self.log(
                    self.tr("Can't define upload logs : {0}").format(exc), push=True
                )

    def _add_vectordb_stored_data_logs(self, stored_data: StoredData) -> None:
        """
        Add log for stored data vector db if defined

        Args:
            stored_data: StoredData
        """
        if stored_data.tags and "vectordb_id" in stored_data.tags:
            vectordb_id = stored_data.tags["vectordb_id"]
            try:
                manager = StoredDataRequestManager()
                vectordb_stored_data = manager.get_stored_data(
                    datastore_id=stored_data.datastore_id, stored_data_id=vectordb_id
                )
                self._add_stored_data_execution_logs(vectordb_stored_data)
            except UnavailableStoredData as exc:
                self.log(
                    self.tr("Can't define execution logs : {0}").format(exc), push=True
                )

    def _add_stored_data_execution_logs(self, stored_data: StoredData) -> None:
        """
        Add log for stored data execution

        Args:
            stored_data: StoredData
        """
        try:
            manager = ProcessingRequestManager()
            executions = manager.get_stored_data_executions(
                datastore_id=stored_data.datastore_id, stored_data_id=stored_data._id
            )
            for execution in executions:
                widget = ExecutionLogWidget(stored_data.datastore_id, self)
                widget.set_processing_execution(execution)
                self.vlayout_execution.addWidget(widget)
        except UnavailableExecutionException as exc:
            self.log(
                self.tr("Can't define execution logs : {0}").format(exc), push=True
            )

    def _get_status_text(self, stored_data: StoredData) -> str:
        """
        Define status text from a stored data

        Args:
            stored_data: (StoredData) stored data

        Returns: status text

        """
        status = stored_data.status
        if status == StoredDataStatus.CREATED:
            result = self.tr(
                "Waiting for data creation. You will find above technical information about executing "
                "processing."
            )
        elif status == StoredDataStatus.GENERATING:
            result = self.tr(
                "Data is generating. You will find above technical information about executing processing."
            )
        elif status == StoredDataStatus.UNSTABLE:
            if stored_data.type == "VECTOR-DB":
                result = self.tr("Database integration failed.")
            else:
                result = self.tr("Tile creation failed.")
            result += self.tr(
                " You will find above technical information about processing executed and encountered "
                "problem."
            )
        elif status == StoredDataStatus.MODIFYING:
            result = self.tr(
                "Data is generating. You will find above technical information about executing processing."
            )
        else:
            # GENERATED and DELETED
            if stored_data.type == "VECTOR-DB":
                result = self.tr("Database integration successful.")
            else:
                result = self.tr("Tile creation successful.")
            result += self.tr(
                " You will find above technical information about executed processing."
            )
        return result

    @staticmethod
    def _get_status_icon(status: StoredDataStatus) -> QPixmap:
        """
        Get status icon

        Args:
            status: StoredDataStatus

        Returns: QPixmap

        """
        if status == StoredDataStatus.CREATED:
            result = QIcon(QgsApplication.iconPath("mTaskQueued.svg")).pixmap(
                QSize(16, 16)
            )
        elif status == StoredDataStatus.GENERATING:
            result = QIcon(QgsApplication.iconPath("mTaskRunning.svg")).pixmap(
                QSize(16, 16)
            )
        elif status == StoredDataStatus.UNSTABLE:
            result = QIcon(QgsApplication.iconPath("mIconWarning.svg")).pixmap(
                QSize(16, 16)
            )
        elif status == StoredDataStatus.MODIFYING:
            result = QIcon(QgsApplication.iconPath("mTaskRunning.svg")).pixmap(
                QSize(16, 16)
            )
        else:
            # GENERATED and DELETED
            result = QIcon(QgsApplication.iconPath("mIconSuccess.svg")).pixmap(
                QSize(16, 16)
            )

        return result
