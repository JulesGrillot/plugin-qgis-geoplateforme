import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QWidget

from geotuileur.api.processing import ProcessingRequestManager
from geotuileur.api.stored_data import StoredData, StoredDataRequestManager
from geotuileur.api.upload import UploadRequestManager
from geotuileur.gui.report.wdg_execution_log import ExecutionLogWidget
from geotuileur.gui.report.wdg_upload_log import UploadLogWidget
from geotuileur.toolbelt import PlgLogger


class ReportDialog(QDialog):
    def __init__(self, parent: QWidget = None):
        """
        QDialog to display report for a stored data

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
        """
        Define displayed stored data

        Args:
            stored_data: StoredData
        """
        self.lne_name.setText(stored_data.name)
        self.lne_id.setText(stored_data.id)

        self._add_upload_log(stored_data)
        self._add_vectordb_stored_data_logs(stored_data)
        self._add_stored_data_execution_logs(stored_data)

    def _add_upload_log(self, stored_data: StoredData) -> None:
        """
        Add log for stored data upload if defined

        Args:
            stored_data: StoredData
        """
        if stored_data.tags and "upload_id" in stored_data.tags:
            upload_id = stored_data.tags["upload_id"]

            try:
                manager = UploadRequestManager()
                upload = manager.get_upload(stored_data.datastore_id, upload_id)
                widget = UploadLogWidget(self)
                widget.set_upload(upload)
                self.vlayout_execution.addWidget(widget)
            except UploadRequestManager.UnavailableUploadException as exc:
                self.log(
                    self.tr("Can't define upload logs : {0}").format(exc), push=True
                )

    def _add_vectordb_stored_data_logs(self, stored_data: StoredData) -> None:
        """
        Add log for stored data vector db if defined

        Args:
            stored_data: StoredData
        """
        if stored_data.tags and "vectordb_id" in stored_data.tags:
            vectordb_id = stored_data.tags["vectordb_id"]
            try:
                manager = StoredDataRequestManager()
                vectordb_stored_data = manager.get_stored_data(
                    datastore=stored_data.datastore_id, stored_data=vectordb_id
                )
                self._add_stored_data_execution_logs(vectordb_stored_data)
            except StoredDataRequestManager.UnavailableStoredData as exc:
                self.log(
                    self.tr("Can't define execution logs : {0}").format(exc), push=True
                )

    def _add_stored_data_execution_logs(self, stored_data: StoredData) -> None:
        """
        Add log for stored data execution

        Args:
            stored_data: StoredData
        """
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
            self.log(
                self.tr("Can't define execution logs : {0}").format(exc), push=True
            )
