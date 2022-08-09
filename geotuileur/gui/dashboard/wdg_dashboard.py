import os

from qgis.PyQt import QtCore, uic
from qgis.PyQt.QtCore import QModelIndex
from qgis.PyQt.QtGui import QCursor, QGuiApplication
from qgis.PyQt.QtWidgets import QAbstractItemView, QAction, QMenu, QTableView, QWidget

from geotuileur.api.stored_data import StoredData, StoredDataStatus, StoredDataStep
from geotuileur.gui.mdl_stored_data import StoredDataListModel
from geotuileur.gui.proxy_model_stored_data import StoredDataProxyModel
from geotuileur.gui.publication_creation.wzd_publication_creation import (
    PublicationFormCreation,
)
from geotuileur.gui.report.dlg_report import ReportDialog
from geotuileur.gui.tile_creation.wzd_tile_creation import TileCreationWizard
from geotuileur.toolbelt import PlgLogger


class DashboardWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        """
        QWidget to display dashboard

        Args:
            parent: parent QWidget
        """
        super().__init__(parent)
        self.log = PlgLogger().log

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "wdg_dashboard.ui"),
            self,
        )

        # Create model for stored data display
        self.mdl_stored_data = StoredDataListModel(self)

        # Create proxy model for each table

        # Action to finish
        self._init_table_view(
            tbv=self.tbv_actions_to_finish,
            visible_steps=[
                StoredDataStep.TILE_GENERATION,
                StoredDataStep.TILE_SAMPLE,
                StoredDataStep.TILE_PUBLICATION,
            ],
            visible_status=[StoredDataStatus.GENERATED, StoredDataStatus.UNSTABLE],
        )
        self.tbv_actions_to_finish.setColumnHidden(
            self.mdl_stored_data.OTHER_ACTIONS_COL, True
        )

        # Running actions
        self._init_table_view(
            tbv=self.tbl_running_actions,
            visible_steps=[],
            visible_status=[StoredDataStatus.GENERATING],
        )
        self.tbl_running_actions.setColumnHidden(
            self.mdl_stored_data.OTHER_ACTIONS_COL, True
        )

        # Publicated tiles
        self._init_table_view(
            tbv=self.tbl_publicated_tiles,
            visible_steps=[StoredDataStep.PUBLISHED],
            visible_status=[StoredDataStatus.GENERATED],
        )

        self.cbx_datastore.currentIndexChanged.connect(self._datastore_updated)
        self._datastore_updated()

    def _init_table_view(
        self,
        tbv: QTableView,
        visible_steps: [StoredDataStep],
        visible_status: [StoredDataStatus],
    ) -> None:
        """
        Initialization of a table view for specific stored data steps and status visibility

        Args:
            tbv:  QTableView table view
            visible_steps: [StoredDataStep] visible stored data steps
            visible_status: [StoredDataStatus] visible stored data status
        """
        proxy_mdl = self._create_proxy_model(
            visible_steps=visible_steps,
            visible_status=visible_status,
        )
        tbv.setModel(proxy_mdl)
        tbv.verticalHeader().setVisible(False)
        tbv.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tbv.clicked.connect(lambda index: self._item_clicked(index, proxy_mdl))

    def refresh(self):
        """
        Force refresh of stored data model

        """
        self._datastore_updated()

    def _item_clicked(
        self, index: QModelIndex, proxy_model: StoredDataProxyModel
    ) -> None:
        """
        Launch action for selected table item depending on clicked column

        Args:
            index: selected index
            proxy_model: used StoredDataProxyModel
        """
        # Get StoredData
        stored_data = proxy_model.data(
            proxy_model.index(index.row(), self.mdl_stored_data.NAME_COL),
            QtCore.Qt.UserRole,
        )
        if stored_data:
            if index.column() == self.mdl_stored_data.ACTION_COL:
                self._stored_data_main_action(stored_data)
            elif index.column() == self.mdl_stored_data.DELETE_COL:
                self._delete(stored_data)
            elif index.column() == self.mdl_stored_data.REPORT_COL:
                self._show_report(stored_data)
            elif index.column() == self.mdl_stored_data.OTHER_ACTIONS_COL:
                self._stored_data_other_actions(stored_data)

    def _stored_data_main_action(self, stored_data: StoredData):
        """
        Execute stored data main action depending on current stored data status and step

        Args:
            stored_data: (StoredData) stored data
        """
        status = StoredDataStatus[stored_data.status]
        if status == StoredDataStatus.GENERATING:
            self._show_report(stored_data)
        elif status == StoredDataStatus.GENERATED:
            current_step = stored_data.get_current_step()
            if current_step == StoredDataStep.TILE_GENERATION:
                self._generate_tile_wizard(stored_data)
            elif current_step == StoredDataStep.TILE_SAMPLE:
                self._tile_sample_wizard(stored_data)
            elif current_step == StoredDataStep.TILE_PUBLICATION:
                self._publish_wizard(stored_data)
            elif current_step == StoredDataStep.PUBLISHED:
                self._view_tile(stored_data)
        else:
            self._show_report(stored_data)

    def _stored_data_other_actions(self, stored_data: StoredData):
        """
        Display menu for other actions on stored data

        Args:
            stored_data: (StoredData) stored data
        """
        if stored_data.get_current_step() == StoredDataStep.PUBLISHED:
            menu = QMenu(self)

            replace_action = QAction(self.tr("Replace data"))
            replace_action.triggered.connect(
                lambda: self._replace_data_wizard(stored_data)
            )
            menu.addAction(replace_action)

            style_action = QAction(self.tr("Manage styles"))
            style_action.triggered.connect(lambda: self._style_wizard(stored_data))
            menu.addAction(style_action)

            update_publish_action = QAction(self.tr("Update publication informations"))
            update_publish_action.triggered.connect(
                lambda: self._publish_info_update_wizard(stored_data)
            )
            menu.addAction(update_publish_action)

            unpublish_action = QAction(self.tr("Unpublish"))
            unpublish_action.triggered.connect(lambda: self._unpublish(stored_data))
            menu.addAction(unpublish_action)

            menu.exec(QCursor.pos())

    def _delete(self, stored_data: StoredData) -> None:
        """
        Delete a stored data

        Args:
            stored_data: (StoredData) stored data to delete
        """
        self.log("Stored data delete not implemented yet", push=True)

    def _show_report(self, stored_data: StoredData) -> None:
        """
        Show report for a stored data

        Args:
            stored_data: (StoredData) stored data to publish
        """
        dialog = ReportDialog(self)
        dialog.set_stored_data(stored_data)
        dialog.show()

    def _tile_sample_wizard(self, stored_data: StoredData) -> None:
        """
        Show tile sample wizard for a stored data

        Args:
            stored_data: (StoredData) stored data to view tile sample wizard
        """
        self.log("Tile sample wizard not implemented yet", push=True)

    def _generate_tile_wizard(self, stored_data: StoredData) -> None:
        """
        Show tile generation wizard for a stored data

        Args:
            stored_data: (StoredData) stored data to generate tile
        """
        QGuiApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
        publication_wizard = TileCreationWizard(self)
        publication_wizard.set_datastore_id(stored_data.datastore_id)
        publication_wizard.set_stored_data_id(stored_data.id)
        QGuiApplication.restoreOverrideCursor()
        publication_wizard.show()

    def _publish_wizard(self, stored_data: StoredData) -> None:
        """
        Show publish wizard for a stored data

        Args:
            stored_data: (StoredData) stored data to publish
        """
        QGuiApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
        publication_wizard = PublicationFormCreation(self)
        publication_wizard.set_datastore_id(stored_data.datastore_id)
        publication_wizard.set_stored_data_id(stored_data.id)
        QGuiApplication.restoreOverrideCursor()
        publication_wizard.show()

    def _view_tile(self, stored_data: StoredData) -> None:
        """
        View tile for a stored data

        Args:
            stored_data: (StoredData) stored data to be viewed
        """
        self.log("Tile view not implemented yet", push=True)

    def _replace_data_wizard(self, stored_data: StoredData) -> None:
        """
        Show replace data wizard for a stored data

        Args:
            stored_data: (StoredData) stored data
        """
        self.log("Replace data not implemented yet", push=True)

    def _style_wizard(self, stored_data: StoredData) -> None:
        """
        Show style wizard for a stored data

        Args:
            stored_data: (StoredData) stored data
        """
        self.log("Tile style management not implemented yet", push=True)

    def _publish_info_update_wizard(self, stored_data: StoredData) -> None:
        """
        Show publish information update wizard for a stored data

        Args:
            stored_data: (StoredData) stored data
        """
        self.log("Publish information update not implemented yet", push=True)

    def _unpublish(self, stored_data: StoredData) -> None:
        """
        Unpublish a stored data

        Args:
            stored_data: (StoredData) stored data
        """
        self.log("Unpublish not implemented yet", push=True)

    def _create_proxy_model(
        self,
        visible_steps: [StoredDataStep],
        visible_status: [StoredDataStatus],
    ) -> StoredDataProxyModel:
        """
        Create StoredDataProxyModel with filters

        Args:
            visible_steps: [StoredDataStep] visible stored data steps
            visible_status: [StoredDataStatus] visible stored data status

        Returns: StoredDataProxyModel

        """
        proxy_mdl = StoredDataProxyModel(self)
        proxy_mdl.setSourceModel(self.mdl_stored_data)

        proxy_mdl.set_visible_steps(visible_steps)
        proxy_mdl.set_visible_status(visible_status)

        return proxy_mdl

    def _datastore_updated(self) -> None:
        """
        Update stored data combobox when datastore is updated

        """
        self.mdl_stored_data.set_datastore(self.cbx_datastore.current_datastore_id())

        self.tbv_actions_to_finish.resizeRowsToContents()
        self.tbv_actions_to_finish.resizeColumnsToContents()

        self.tbl_running_actions.resizeRowsToContents()
        self.tbl_running_actions.resizeColumnsToContents()

        self.tbl_publicated_tiles.resizeRowsToContents()
        self.tbl_publicated_tiles.resizeColumnsToContents()
