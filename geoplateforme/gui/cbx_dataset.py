from qgis.PyQt.QtCore import QSortFilterProxyModel, Qt
from qgis.PyQt.QtWidgets import QComboBox

from geoplateforme.gui.mdl_dataset import DatasetListModel


class DatasetComboBox(QComboBox):
    def __init__(self, parent=None):
        """
        QComboBox for dataset selection.

        Use DatasetListModel to get available dataset for connected user

        Args:
            parent:
        """
        super().__init__(parent)

        self.datastore_id = None
        self.mdl_dataset = DatasetListModel(self)

        self.proxy_model_dataset = QSortFilterProxyModel(self)
        self.proxy_model_dataset.setSourceModel(self.mdl_dataset)
        self.proxy_model_dataset.sort(
            DatasetListModel.NAME_COL, Qt.SortOrder.AscendingOrder
        )

        self.setModel(self.proxy_model_dataset)

    def refresh(self, force: bool = False) -> None:
        """
        Refresh DatasetListModel

        Args:
            force: force refresh

        """
        self.mdl_dataset.refresh(force)

    def set_datastore_id(self, datastore_id: str, force_refresh: bool = False) -> None:
        """
        Define current datastore id

        Args:
            datastore_id: (str) datastore id
            force_refresh: force refresh of dataset store if datastore_id is not changed
        """
        if datastore_id and (datastore_id != self.datastore_id or force_refresh):
            self.datastore_id = datastore_id
            self.mdl_dataset.set_datastore_id(datastore_id)
            self.refresh(True)
            self.activated.emit(1)

    def set_dataset_name(self, dataset_name: str) -> None:
        """
        Define current index from dataset name

        Args:
            dataset_name: (str) dataset name
        """
        row = self.mdl_dataset.get_dataset_row(dataset_name)
        if row != -1:
            row = self.proxy_model_dataset.mapFromSource(
                self.mdl_dataset.index(row, self.mdl_dataset.NAME_COL)
            ).row()
            self.setCurrentIndex(row)

    def current_dataset_name(self) -> str:
        """
        Get current selected dataset name

        Returns: (str) selected dataset name

        """
        return self.currentText()
