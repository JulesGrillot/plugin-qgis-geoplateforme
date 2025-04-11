from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtGui import QStandardItemModel

from geoplateforme.api.stored_data import StoredData


class StoredDataDetailsModel(QStandardItemModel):
    NAME_COL = 0
    VALUE_COL = 1

    def __init__(self, parent: QObject = None):
        """
        QStandardItemModel override for stored data details display

        Args:
            parent: QObject
        """
        super().__init__(0, 2, parent)
        self.setHorizontalHeaderLabels([self.tr("Name"), self.tr("Value")])

    def set_stored_data(self, stored_data: StoredData) -> None:
        """
        Define display StoredData

        Args:
            stored_data: StoredData
        """
        while self.rowCount():
            self.removeRow(0)

        if stored_data.size:
            # Display in Mo
            self._insert_value(self.tr("Size"), str(f"{stored_data.size / 1e6} Mo"))
        if stored_data.srs:
            self._insert_value(self.tr("SRS"), stored_data.srs)
        if len(stored_data.zoom_levels()) != 0:
            self._insert_value(
                self.tr("Pyramid levels"), ",".join(stored_data.zoom_levels())
            )

    def _insert_value(self, name: str, value: str) -> None:
        """
        Insert executions and status

        Args:
            execution: Execution execution
        """
        row = self.rowCount()
        self.insertRow(row)
        self.setData(self.index(row, self.NAME_COL), name)
        self.setData(self.index(row, self.VALUE_COL), value)
