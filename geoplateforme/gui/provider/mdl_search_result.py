import json

# PyQGIS
from qgis.PyQt.QtCore import QByteArray, QObject, Qt, QUrl
from qgis.PyQt.QtGui import QStandardItemModel

# plugin
from geoplateforme.toolbelt import NetworkRequestsManager, PlgLogger


class SearchResultModel(QStandardItemModel):
    TITLE_COL = 0
    PRODUCER_COL = 1
    THEME_COL = 2
    TYPE_COL = 3

    authorized_type = ["WMS", "TMS", "WMTS", "WFS"]

    def __init__(self, parent: QObject = None):
        """QStandardItemModel for search result display

        :param parent: parent
        :type parent: QObject
        """
        super().__init__(parent)
        self.log = PlgLogger().log
        self.setHorizontalHeaderLabels(
            [
                self.tr("Title"),
                self.tr("Producer"),
                self.tr("Theme"),
                self.tr("Type"),
            ]
        )

    def get_result_row(self, result_id: str) -> int:
        """Get result row from result id, returns -1 if result not available

        :param resultid: result id
        :type result_id: str

        :return: result id row, -1 if result not available
        :rtype: int
        """
        result = -1
        for row in range(0, self.rowCount()):
            if (
                self.data(self.index(row, self.TITLE_COL), Qt.ItemDataRole.UserRole).id
                == result_id
            ):
                result = row
                break
        return result

    def set_search_text(self, text: str) -> None:
        """Refresh QStandardItemModel data with result on text search

        :param text: seach text
        :type text: str
        """
        self.removeRows(0, self.rowCount())
        request_manager = NetworkRequestsManager()
        # plg_settings = PlgOptionsManager.get_plg_settings()

        try:
            data = QByteArray()
            data_map = {
                "title": text,
            }
            data.append(json.dumps(data_map))
            reply = request_manager.post_url(
                url=QUrl(
                    "https://data.geopf.fr/recherche/api/indexes/geoplateforme?page=1&size=50"
                ),
                data=data,
                headers={b"Content-Type": bytes("application/json", "utf8")},
            )
        except ConnectionError as err:
            self.log(
                f"Error while searching layers: {err}",
                log_level=2,
                push=False,
            )

        search_results = json.loads(reply.data())
        for document in search_results["documents"]:
            if document["type"] in self.authorized_type:
                self.insert_result(document)

    def insert_result(self, result: dict) -> None:
        """Insert result in model

        :param result: result to insert
        :type result: dict
        """
        row = self.rowCount()
        self.insertRow(row)

        self.setData(self.index(row, self.TITLE_COL), result["title"])
        self.setData(self.index(row, self.TITLE_COL), result, Qt.ItemDataRole.UserRole)
        if "producers" in result:
            self.setData(
                self.index(row, self.PRODUCER_COL), ", ".join(result["producers"])
            )
        else:
            self.setData(self.index(row, self.PRODUCER_COL), "")
        if "theme" in result:
            self.setData(self.index(row, self.THEME_COL), result["theme"])
        else:
            self.setData(self.index(row, self.THEME_COL), "")
        self.setData(self.index(row, self.TYPE_COL), result["type"])
