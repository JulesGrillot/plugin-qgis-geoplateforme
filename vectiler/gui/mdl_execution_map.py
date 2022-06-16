from PyQt5.QtCore import QObject
from PyQt5.QtGui import QStandardItemModel

from vectiler.api.check import Execution


class ExecutionMapTreeModel(QStandardItemModel):
    NAME_COL = 0
    STATUS_COL = 1

    def __init__(self, parent: QObject = None):
        """
        QStandardItemModel override for execution map display as a tree

        Args:
            parent: QObject
        """
        super().__init__(0, 2, parent)
        self.setHorizontalHeaderLabels([self.tr("Name"), self.tr("Status")])

    def set_execution_map(self, execution_map: {str: [Execution]}) -> None:
        """
        Define display execution map

        Args:
            execution_map: execution map
        """
        while self.rowCount():
            self.removeRow(0)

        for status, executions in execution_map.items():
            self._insert_executions(status, executions)

    def _insert_executions(self, status: str, executions: [Execution]) -> None:
        """
        Insert executions and status

        Args:
            status: (str) execution list status
            executions: [Execution] execution list
        """
        row = self.rowCount()
        self.insertRow(row)
        status_index = self.index(row, self.NAME_COL)
        # Insert column in index for child display
        self.insertColumns(0, self.columnCount(), status_index)
        self.setData(status_index, status)
        for execution in executions:
            execution_row = self.rowCount(status_index)
            self.insertRow(execution_row, status_index)
            self.setData(self.index(execution_row, self.NAME_COL, status_index), execution.check.name)
            self.setData(self.index(execution_row, self.STATUS_COL, status_index), execution.status)
