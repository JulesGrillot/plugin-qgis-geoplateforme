import json

from PyQt5.QtCore import QByteArray, QObject
from PyQt5.QtGui import QStandardItemModel

from vectiler.api.client import NetworkRequestsManager


class DatastoreListModel(QStandardItemModel):
    NAME_COL = 0
    ID_COL = 1

    def __init__(self, parent: QObject = None):
        """
        QStandardItemModel for datastore list display

        Args:
            parent: QObject parent
        """
        super().__init__(parent)
        self.setHorizontalHeaderLabels([self.tr("Name"), self.tr("id")])
        self.refresh()

    def refresh(self) -> None:
        """
        Refresh QStandardItemModel data with current user datastore

        """
        self.removeRows(0, self.rowCount())

        network_requests_manager = NetworkRequestsManager()
        check = network_requests_manager.get_user_info()
        if isinstance(check, (dict, QByteArray, bytes)):
            # decode token as dict
            data = json.loads(check.data().decode("utf-8"))
            if not isinstance(data, dict):
                self.log(
                    message=f"ERROR - Invalid user data received. Expected dict, not {type(data)}",
                    log_level=2,
                    push=True,
                )
            else:
                # For now, not using any User object : will be done later
                communities_member = data["communities_member"]
                for community_member in communities_member:
                    community = community_member["community"]
                    self.insertRow(self.rowCount())
                    row = self.rowCount() - 1

                    self.setData(self.index(row, self.NAME_COL), community["name"])
                    self.setData(self.index(row, self.ID_COL), community["datastore"])
