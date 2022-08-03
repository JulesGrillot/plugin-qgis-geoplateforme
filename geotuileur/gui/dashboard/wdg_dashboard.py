import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QAbstractItemView, QWidget

from geotuileur.api.stored_data import StoredDataStatus, StoredDataStep
from geotuileur.gui.mdl_stored_data import StoredDataListModel
from geotuileur.gui.proxy_model_stored_data import StoredDataProxyModel


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

        # Running actions
        self.proxy_mdl_running_action = self._create_proxy_model(
            visible_steps=[],
            visible_status=[StoredDataStatus.GENERATING],
        )
        self.tbl_running_actions.setModel(self.proxy_mdl_running_action)
        self.tbl_running_actions.verticalHeader().setVisible(False)
        self.tbl_running_actions.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Publicated tiles
        self.proxy_mdl_publicated_tiles = self._create_proxy_model(
            visible_steps=[StoredDataStep.PUBLISHED],
            visible_status=[StoredDataStatus.GENERATED],
        )
        self.tbl_publicated_tiles.setModel(self.proxy_mdl_publicated_tiles)
        self.tbl_publicated_tiles.verticalHeader().setVisible(False)
        self.tbl_publicated_tiles.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.cbx_datastore.currentIndexChanged.connect(self._datastore_updated)
        self._datastore_updated()

    def refresh(self):
        """
        Force refresh of stored data model

        """
        self._datastore_updated()

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
