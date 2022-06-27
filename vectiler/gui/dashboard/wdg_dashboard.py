import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWidget

from vectiler.gui.mdl_stored_data import StoredDataListModel
from vectiler.gui.proxy_model_stored_data import StoredDataProxyModel


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
            expected_tags=["upload_id"], forbidden_tags=["pyramid_id", "tms_url"]
        )
        self.tbv_actions_to_finish.setModel(self.proxy_mdl_action_to_finish)

        # Running actions
        # TODO running actions need filter on stored data status : for now display all stored_data
        self.tbl_running_actions.setModel(self.mdl_stored_data)

        # Publicated tiles
        self.proxy_mdl_publicated_tiles = self._create_proxy_model(
            expected_tags=["upload_id", "tms_url"], forbidden_tags=[]
        )
        self.tbl_publicated_tiles.setModel(self.proxy_mdl_publicated_tiles)

        self.cbx_datastore.currentIndexChanged.connect(self._datastore_updated)
        self._datastore_updated()

    def refresh(self):
        """
        Force refresh of stored data model

        """
        self._datastore_updated()

    def _create_proxy_model(
        self, expected_tags: [str], forbidden_tags: [str]
    ) -> StoredDataProxyModel:
        """
        Create StoredDataProxyModel with filters

        Args:
            expected_tags: [str] expected tag filter
            forbidden_tags: [str] forbidden tag filter

        Returns: StoredDataProxyModel

        """
        proxy_mdl = StoredDataProxyModel(self)
        proxy_mdl.setSourceModel(self.mdl_stored_data)

        proxy_mdl.set_expected_tags(expected_tags)
        proxy_mdl.set_forbidden_tags(forbidden_tags)

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
