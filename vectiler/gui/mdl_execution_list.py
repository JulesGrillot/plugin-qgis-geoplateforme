from PyQt5.QtCore import QObject
from PyQt5.QtGui import QStandardItemModel

from vectiler.api.execution import Execution


class ExecutionListModel(QStandardItemModel):
    NAME_COL = 0
    STATUS_COL = 1
    START_COL = 2
    FINISH_COL = 3

    def __init__(self, parent: QObject = None):
        """
        QStandardItemModel override for execution map display as a tree

        Args:
            parent: QObject
        """
        super().__init__(0, 2, parent)
        self.setHorizontalHeaderLabels(
            [self.tr("Name"), self.tr("Status"), self.tr("Start"), self.tr("Finish")]
        )

    def set_execution_list(self, execution_list: [Execution]) -> None:
        """
        Define display execution list

        Args:
            execution_list: execution list
        """
        while self.rowCount():
            self.removeRow(0)

        for executions in execution_list:
            self._insert_execution(executions)

    def _insert_execution(self, execution: Execution) -> None:
        """
        Insert executions and status

        Args:
            execution: Execution execution
        """
        row = self.rowCount()
        self.insertRow(row)
        self.setData(self.index(row, self.NAME_COL), execution.name)
        self.setData(self.index(row, self.STATUS_COL), execution.status)
        self.setData(self.index(row, self.START_COL), execution.start)
        self.setData(self.index(row, self.FINISH_COL), execution.finish)
