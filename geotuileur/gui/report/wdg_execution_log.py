import os
import sys

from qgis.core import QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.PyQt.QtWidgets import QWidget

from geotuileur.api.check import (
    CheckExecution,
    CheckExecutionStatus,
    CheckRequestManager,
)
from geotuileur.api.custom_exceptions import UnavailableExecutionException
from geotuileur.api.processing import (
    Execution,
    ExecutionStatus,
    ProcessingRequestManager,
)
from geotuileur.api.utils import as_localized_datetime
from geotuileur.toolbelt import PlgLogger


class ExecutionLogWidget(QWidget):
    def __init__(self, datastore: str, parent: QWidget = None):
        """
        QWidget to display execution log

        Args:
            datastore: (str) datastore id
            parent: parent QWidget
        """
        super().__init__(parent)
        self.datastore = datastore
        self.log = PlgLogger().log

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "wdg_execution_log.ui"),
            self,
        )

        if sys.platform.startswith("win"):
            self.tbw_logs.setFontFamily("Courier New")
        else:
            self.tbw_logs.setFontFamily("monospace")

    def set_processing_execution(self, execution: Execution) -> None:
        """
        Define visible processing execution

        Args:
            execution: (Execution)
        """
        self.lbl_execution_name.setText(execution.name)
        status = ExecutionStatus(execution.status)
        self.lbl_execution_status.setPixmap(self._get_execution_status_icon(status))
        self.lbl_execution_time.setText(as_localized_datetime(execution.creation))
        try:
            manager = ProcessingRequestManager()
            logs = self.tr("Execution ID :{0}\n").format(execution.id)
            if execution.output:
                if "stored_data" in execution.output:
                    logs += self.tr("Output stored data ID :{0}\n").format(
                        execution.output["stored_data"]["_id"]
                    )

            logs += self.tr("Logs:\n")
            logs += manager.get_execution_logs(self.datastore, execution.id)
            self.tbw_logs.setPlainText(logs)
        except ProcessingRequestManager.UnavailableExecutionException as exc:
            self.tbw_logs.setPlainText(
                self.tr("Can't define execution logs : {0}").format(exc)
            )

    def set_check_execution(self, execution: CheckExecution) -> None:
        """
        Define visible check execution

        Args:
            execution: (CheckExecution)
        """
        self.lbl_execution_name.setText(execution.name)
        status = CheckExecutionStatus(execution.status)
        self.lbl_execution_status.setPixmap(
            self._get_check_execution_status_icon(status)
        )
        self.lbl_execution_time.setText(as_localized_datetime(execution.creation))
        try:
            manager = CheckRequestManager()
            logs = self.tr("Execution ID :{0}\n").format(execution.id)
            logs += self.tr("Logs:\n")
            logs += manager.get_execution_logs(self.datastore, execution.id)
            self.tbw_logs.setPlainText(logs)
        except UnavailableExecutionException as exc:
            self.tbw_logs.setPlainText(
                self.tr("Can't define execution logs : {0}").format(exc)
            )

    @staticmethod
    def _get_execution_status_icon(status: ExecutionStatus) -> QPixmap:
        if status == ExecutionStatus.WAITING or status == ExecutionStatus.CREATED:
            result = QIcon(QgsApplication.iconPath("mTaskQueued.svg")).pixmap(
                QSize(16, 16)
            )
        elif status == ExecutionStatus.PROGRESS:
            result = QIcon(QgsApplication.iconPath("mTaskRunning.svg")).pixmap(
                QSize(16, 16)
            )
        elif status == ExecutionStatus.SUCCESS:
            result = QIcon(QgsApplication.iconPath("mIconSuccess.svg")).pixmap(
                QSize(16, 16)
            )
        elif status == ExecutionStatus.FAILURE:
            result = QIcon(QgsApplication.iconPath("mIconWarning.svg")).pixmap(
                QSize(16, 16)
            )
        elif status == ExecutionStatus.ABORTED:
            result = QIcon(QgsApplication.iconPath("mTaskTerminated.svg")).pixmap(
                QSize(16, 16)
            )
        return result

    @staticmethod
    def _get_check_execution_status_icon(status: CheckExecutionStatus) -> QPixmap:
        if status == CheckExecutionStatus.WAITING:
            result = QIcon(QgsApplication.iconPath("mTaskQueued.svg")).pixmap(
                QSize(16, 16)
            )
        elif status == CheckExecutionStatus.PROGRESS:
            result = QIcon(QgsApplication.iconPath("mTaskRunning.svg")).pixmap(
                QSize(16, 16)
            )
        elif status == CheckExecutionStatus.SUCCESS:
            result = QIcon(QgsApplication.iconPath("mIconSuccess.svg")).pixmap(
                QSize(16, 16)
            )
        elif status == CheckExecutionStatus.FAILURE:
            result = QIcon(QgsApplication.iconPath("mIconWarning.svg")).pixmap(
                QSize(16, 16)
            )
        return result
