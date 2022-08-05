import os
import sys

from qgis.core import QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.PyQt.QtWidgets import QWidget

from geotuileur.api.upload import Upload, UploadRequestManager, UploadStatus
from geotuileur.gui.report.wdg_execution_log import ExecutionLogWidget
from geotuileur.toolbelt import PlgLogger


class UploadLogWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        """
        QWidget to display dashboard

        Args:
            parent: parent QWidget
        """
        super().__init__(parent)
        self.log = PlgLogger().log

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "wdg_upload_log.ui"),
            self,
        )

        if sys.platform.startswith("win"):
            self.tbw_logs.setFontFamily("Courier New")
        else:
            self.tbw_logs.setFontFamily("monospace")

    def set_upload(self, upload: Upload) -> None:
        status = UploadStatus(upload.status)
        self.lbl_status.setPixmap(self._get_status_icon(status))

        try:
            manager = UploadRequestManager()
            executions = manager.get_upload_checks_execution(
                datastore=upload.datastore_id, upload=upload.id
            )
            for execution in executions:
                widget = ExecutionLogWidget(upload.datastore_id, self)
                widget.set_check_execution(execution)
                self.vlayout_checks.addWidget(widget)
        except UploadRequestManager.UnavailableUploadException as exc:
            self.log(self.tr(f"Can't define execution logs : {exc}"), push=True)

    def _get_status_icon(self, status: UploadStatus) -> QPixmap:
        if status == UploadStatus.CREATED:
            result = QIcon(QgsApplication.iconPath("mTaskQueued.svg")).pixmap(
                QSize(16, 16)
            )
        elif status == UploadStatus.GENERATING:
            result = QIcon(QgsApplication.iconPath("mTaskRunning.svg")).pixmap(
                QSize(16, 16)
            )
        elif status == UploadStatus.UNSTABLE:
            result = QIcon(QgsApplication.iconPath("mIconWarning.svg")).pixmap(
                QSize(16, 16)
            )
        else:
            result = QIcon(QgsApplication.iconPath("mIconSuccess.svg")).pixmap(
                QSize(16, 16)
            )
        return result
