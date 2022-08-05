import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QWidget

from geotuileur.api.processing import ProcessingRequestManager
from geotuileur.api.stored_data import StoredData
from geotuileur.api.upload import UploadRequestManager
from geotuileur.gui.report.wdg_execution_log import ExecutionLogWidget
from geotuileur.gui.report.wdg_upload_log import UploadLogWidget
from geotuileur.toolbelt import PlgLogger


class ReportDialog(QDialog):
    def __init__(self, parent: QWidget = None):
        """
        QWidget to display report for a stored data

        Args:
            parent: parent QWidget
        """
        super().__init__(parent)
        self.log = PlgLogger().log

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "dlg_report.ui"),
            self,
        )

        self.setWindowTitle(self.tr("Report"))

    def set_stored_data(self, stored_data: StoredData) -> None:
        self.lne_name.setText(stored_data.name)
        self.lne_id.setText(stored_data.id)

        if stored_data.tags and "upload_id" in stored_data.tags:
            upload_id = stored_data.tags["upload_id"]

            try:
                manager = UploadRequestManager()
                upload = manager.get_upload(stored_data.datastore_id, upload_id)
                widget = UploadLogWidget(self)
                widget.set_upload(upload)
                self.vlayout_execution.addWidget(widget)
            except UploadRequestManager.UnavailableUploadException as exc:
                self.log(self.tr(f"Can't define upload logs : {exc}"), push=True)

        try:
            manager = ProcessingRequestManager()
            executions = manager.get_stored_data_executions(
                datastore=stored_data.datastore_id, stored_data=stored_data.id
            )
            for execution in executions:
                widget = ExecutionLogWidget(stored_data.datastore_id, self)
                widget.set_processing_execution(execution)
                self.vlayout_execution.addWidget(widget)
        except ProcessingRequestManager.UnavailableExecutionException as exc:
            self.log(self.tr(f"Can't define execution logs : {exc}"), push=True)
