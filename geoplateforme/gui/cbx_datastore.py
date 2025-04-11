from qgis.PyQt.QtWidgets import QComboBox

from geoplateforme.gui.mdl_datastore import DatastoreListModel


class DatastoreComboBox(QComboBox):
    def __init__(self, parent=None):
        """
        QComboBox for datastore selection.

        Use DatastoreListModel to get available datastore for connected user

        Args:
            parent:
        """
        super().__init__(parent)

        self.mdl_datastore = DatastoreListModel(self)
        self.setModel(self.mdl_datastore)

    def refresh(self) -> None:
        """
        Refresh DatastoreListModel

        """
        self.mdl_datastore.refresh()

    def set_datastore_id(self, datastore_id: str) -> None:
        """
        Define current index from datastore id

        Args:
            datastore_id: (str) datastore id
        """
        row = self.mdl_datastore.get_datastore_row(datastore_id)
        if row != -1:
            self.setCurrentIndex(row)

    def current_datastore_name(self) -> str:
        """
        Get current selected datastore name

        Returns: (str) selected datastore name

        """
        return self.currentText()

    def current_datastore_id(self) -> str:
        """
        Get current selected datastore id

        Returns: (str) selected datastore id

        """
        index = self.currentIndex()
        model = self.model()
        return model.data(model.index(index, DatastoreListModel.ID_COL))
