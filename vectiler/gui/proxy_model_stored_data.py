from typing import List

from qgis.PyQt.QtCore import QModelIndex, QObject, QSortFilterProxyModel, Qt

from vectiler.gui.mdl_stored_data import StoredDataListModel


class StoredDataProxyModel(QSortFilterProxyModel):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.filter_type = []
        self.tags = []
        self.forbidden_tags = []

    def set_filter_type(self, filter_type: List) -> None:
        """
        Define filter of expected stored data type

        Args:
            filter_type: expected stored data type
        """
        self.filter_type = filter_type

    def set_expected_tags(self, tags: List[str]) -> None:
        """
        Define filter of expected tags for stored data tags key

        Args:
            tags: expected stored data tags key
        """
        self.tags = tags

    def set_forbidden_tags(self, forbidden_tags: List[str]) -> None:
        """
        Define filter of forbidden tags for stored data tags key

        Args:
            forbidden_tags: forbidden stored data tags key
        """
        self.forbidden_tags = forbidden_tags

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """
        Filter visible rows for stored data

        Args:
            source_row: (int) source row
            source_parent: (QModelIndex) source parent

        Returns: True if row is visible, False otherwise

        """
        result = True

        # Check stored_data type
        if len(self.filter_type):
            type_index = self.sourceModel().index(
                source_row, StoredDataListModel.TYPE_COL, source_parent
            )
            type_value = self.sourceModel().data(type_index, Qt.DisplayRole)

            result = type_value in self.filter_type

        # Check stored data flags
        if (len(self.tags) or len(self.forbidden_tags)) and result:
            name_index = self.sourceModel().index(
                source_row, StoredDataListModel.NAME_COL, source_parent
            )
            tags = self.sourceModel().data(name_index, Qt.UserRole)
            if tags is not None:
                available_tags = tags.keys()
                for tag in self.tags:
                    result &= tag in available_tags

                for tag in self.forbidden_tags:
                    result &= tag not in available_tags

        return result
