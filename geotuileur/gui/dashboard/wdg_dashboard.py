import os

from qgis.PyQt import QtCore, uic
from qgis.PyQt.QtCore import QModelIndex
from qgis.PyQt.QtGui import QCursor
from qgis.PyQt.QtWidgets import QAbstractItemView, QAction, QMenu, QWidget

from geotuileur.api.stored_data import StoredData, StoredDataStatus, StoredDataStep
from geotuileur.gui.mdl_stored_data import StoredDataListModel
from geotuileur.gui.proxy_model_stored_data import StoredDataProxyModel
from geotuileur.gui.publication_creation.wzd_publication_creation import (
    PublicationFormCreation,
)


class DashboardWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        """
        QWidget to display dashboard

        Args:
            parent: parent QWidget
        """
        super().__init__(parent)

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "wdg_dashboard.ui"),
            self,
        )

        # Create model for stored data display
        self.mdl_stored_data = StoredDataListModel(self)

        # Create proxy model for each table

        # Action to finish
        self.proxy_mdl_action_to_finish = self._create_proxy_model(
            visible_steps=[
                StoredDataStep.TILE_GENERATION,
                StoredDataStep.TILE_SAMPLE,
                StoredDataStep.TILE_PUBLICATION,
            ],
            visible_status=[StoredDataStatus.GENERATED, StoredDataStatus.UNSTABLE],
        )
        self.tbv_actions_to_finish.setModel(self.proxy_mdl_action_to_finish)
        self.tbv_actions_to_finish.verticalHeader().setVisible(False)
        self.tbv_actions_to_finish.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbv_actions_to_finish.setColumnHidden(
            self.mdl_stored_data.OTHER_ACTIONS_COL, True
        )
        self.tbv_actions_to_finish.clicked.connect(
            lambda index: self._item_clicked(index, self.proxy_mdl_action_to_finish)
        )

        # Running actions
        self.proxy_mdl_running_action = self._create_proxy_model(
            visible_steps=[],
            visible_status=[StoredDataStatus.GENERATING],
        )
        self.tbl_running_actions.setModel(self.proxy_mdl_running_action)
        self.tbl_running_actions.verticalHeader().setVisible(False)
        self.tbl_running_actions.setColumnHidden(
            self.mdl_stored_data.OTHER_ACTIONS_COL, True
        )
        self.tbl_running_actions.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_running_actions.clicked.connect(
            lambda index: self._item_clicked(index, self.proxy_mdl_running_action)
        )

        # Publicated tiles
        self.proxy_mdl_publicated_tiles = self._create_proxy_model(
            visible_steps=[StoredDataStep.PUBLISHED],
            visible_status=[StoredDataStatus.GENERATED],
        )
        self.tbl_publicated_tiles.setModel(self.proxy_mdl_publicated_tiles)
        self.tbl_publicated_tiles.verticalHeader().setVisible(False)
        self.tbl_publicated_tiles.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_publicated_tiles.clicked.connect(
            lambda index: self._item_clicked(index, self.proxy_mdl_publicated_tiles)
        )

        self.cbx_datastore.currentIndexChanged.connect(self._datastore_updated)
        self._datastore_updated()

    def refresh(self):
        """
        Force refresh of stored data model

        """
        self._datastore_updated()

    def _item_clicked(
        self, index: QModelIndex, proxy_model: StoredDataProxyModel
    ) -> None:
        if index.column() == self.mdl_stored_data.ACTION_COL:
            source_index = proxy_model.mapToSource(index)
            stored_data = self.mdl_stored_data.data(
                self.mdl_stored_data.index(
                    source_index.row(), self.mdl_stored_data.NAME_COL
                ),
                QtCore.Qt.UserRole,
            )
            if stored_data:
                status = StoredDataStatus[stored_data.status]
                if status == StoredDataStatus.GENERATING:
                    print("TODO : implement report action")
                elif status == StoredDataStatus.GENERATED:
                    current_step = stored_data.get_current_step()
                    if current_step == StoredDataStep.TILE_GENERATION:
                        print("TODO : implement tile generation action")
                    elif current_step == StoredDataStep.TILE_SAMPLE:
                        print("TODO : implement view sample tile action")
                    elif current_step == StoredDataStep.TILE_PUBLICATION:
                        self._publish(stored_data)
                    elif current_step == StoredDataStep.PUBLISHED:
                        print("TODO : implement view tile action")
                else:
                    print("TODO : implement report action")

        elif index.column() == self.mdl_stored_data.DELETE_COL:
            print("TODO : implement delete action")
        elif index.column() == self.mdl_stored_data.REPORT_COL:
            print("TODO : implement report action")

        elif index.column() == self.mdl_stored_data.OTHER_ACTIONS_COL:
            source_index = proxy_model.mapToSource(index)
            stored_data = self.mdl_stored_data.data(
                self.mdl_stored_data.index(
                    source_index.row(), self.mdl_stored_data.NAME_COL
                ),
                QtCore.Qt.UserRole,
            )
            if stored_data:
                if stored_data.get_current_step() == StoredDataStep.PUBLISHED:
                    menu = QMenu(self)

                    replace_action = QAction(self.tr("Replace data"))
                    replace_action.setEnabled(False)
                    menu.addAction(replace_action)

                    style_action = QAction(self.tr("Manage styles"))
                    style_action.setEnabled(False)
                    menu.addAction(style_action)

                    update_publish_action = QAction(
                        self.tr("Update publication informations")
                    )
                    update_publish_action.setEnabled(False)
                    menu.addAction(update_publish_action)

                    unpublish_action = QAction(self.tr("Unpublish"))
                    unpublish_action.setEnabled(False)
                    menu.addAction(unpublish_action)

                    menu.exec(QCursor.pos())

    def _publish(self, stored_data: StoredData) -> None:
        publication_wizard = PublicationFormCreation(self)
        publication_wizard.set_datastore_id(stored_data.datastore_id)
        publication_wizard.set_stored_data_id(stored_data.id)
        publication_wizard.show()

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
