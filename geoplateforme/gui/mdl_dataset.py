from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtGui import QStandardItemModel

from geoplateforme.api.custom_exceptions import UnavailableUserException
from geoplateforme.api.stored_data import StoredDataRequestManager
from geoplateforme.toolbelt import PlgLogger


class DatasetListModel(QStandardItemModel):
    NAME_COL = 0

    def __init__(self, parent: QObject = None):
        """
        QStandardItemModel for dataset list display

        Args:
            parent: QObject parent
        """
        super().__init__(parent)
        self.log = PlgLogger().log
        self.setHorizontalHeaderLabels([self.tr("Name")])
        self.datastore_id = None

    def set_datastore_id(self, datastore_id: str) -> None:
        """
        Define current datastore id

        Args:
            datastore_id: (str) datastore id
        """
        self.datastore_id = datastore_id

    def get_dataset_row(self, dataset_name: str) -> int:
        """
        Get dataset row from dataset name, returns -1 if dataset not available

        Args:
            dataset_name: (str) dataset name

        Returns: (int) dataset name row, -1 if dataset not available

        """
        result = -1
        for row in range(0, self.rowCount()):
            if self.data(self.index(row, self.NAME_COL)) == dataset_name:
                result = row
                break
        return result

    def refresh(self, force: bool = False) -> None:
        """
        Refresh QStandardItemModel data with current user dataset

        Args:
            force: force refresh

        """
        if force or self.rowCount() == 0:
            self.removeRows(0, self.rowCount())
            try:
                if self.datastore_id:
                    manager = StoredDataRequestManager()
                    stored_datas = manager.get_stored_data_list(self.datastore_id, True)

                    for stored_data in stored_datas:
                        for key, value in dict.items(stored_data["tags"]):
                            if (
                                key == "datasheet_name"
                                and self.get_dataset_row(value) == -1
                            ):
                                self.insertRow(self.rowCount())
                                row = self.rowCount() - 1
                                self.setData(self.index(row, self.NAME_COL), value)

            except UnavailableUserException as exc:
                self.log(
                    f"Error while getting user dataset: {exc}",
                    log_level=2,
                    push=False,
                )
