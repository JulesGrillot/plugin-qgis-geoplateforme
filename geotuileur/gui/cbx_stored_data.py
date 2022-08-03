from typing import List

from qgis.PyQt.QtWidgets import QComboBox

from geotuileur.api.stored_data import StoredDataStatus, StoredDataStep
from geotuileur.gui.mdl_stored_data import StoredDataListModel
from geotuileur.gui.proxy_model_stored_data import StoredDataProxyModel


class StoredDataComboBox(QComboBox):
    def __init__(self, parent=None):
        """
        QComboBox for stored data selection.

        Use StoredDataListModel to get available stored data for selected stored data
        and StoredDataProxyModel for stored data filter

        Args:
            parent:
        """
        super().__init__(parent)

        self.mdl_stored_data = StoredDataListModel(self)
        self.proxy_model_stored_data = StoredDataProxyModel(self)
        self.proxy_model_stored_data.setSourceModel(self.mdl_stored_data)
        # By default we can't display UNSTABLE and DELETED
        self.proxy_model_stored_data.set_invisible_status(
            [StoredDataStatus.UNSTABLE, StoredDataStatus.DELETED]
        )
        self.setModel(self.proxy_model_stored_data)

    def set_filter_type(self, filter_type: []) -> None:
        """
        Define filter of expected stored data type

        Args:
            filter_type: expected stored data type
        """
        self.proxy_model_stored_data.set_filter_type(filter_type)

    def set_visible_steps(self, steps: [StoredDataStep]) -> None:
        """
        Define filter of visible steps for stored data

        Args:
            steps: List[StoredDataStep] visible step list
        """
        self.proxy_model_stored_data.set_visible_steps(steps)

    def set_visible_status(self, status: List[StoredDataStatus]) -> None:
        """
        Define filter of visible status for stored data

        Args:
            status: List[StoredDataStatus] visible status list
        """
        self.proxy_model_stored_data.set_visible_status(status)

    def set_datastore(self, datastore: str) -> None:
        """
        Refresh StoredDataListModel with current datastore stored data

        """
        self.mdl_stored_data.set_datastore(datastore)

    def current_stored_data_name(self) -> str:
        """
        Get current selected stored data name

        Returns: (str) selected stored data name

        """
        return self.currentText()

    def current_stored_data_id(self) -> str:
        """
        Get current selected stored data id

        Returns: (str) selected stored data id

        """
        index = self.currentIndex()
        model = self.model()
        return model.data(model.index(index, StoredDataListModel.ID_COL))
