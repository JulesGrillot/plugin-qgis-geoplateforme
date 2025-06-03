import json
import logging
import os

from qgis.core import QgsProject, QgsRasterLayer, QgsVectorLayer, QgsVectorTileLayer
from qgis.gui import QgsAbstractDataSourceWidget
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QAbstractItemView, QDialogButtonBox

from geoplateforme.gui.provider.capabilities_reader import (
    read_tms_layer_capabilities,
    read_wmts_layer_capabilities,
)
from geoplateforme.gui.provider.mdl_search_result import SearchResultModel
from geoplateforme.toolbelt import PlgLogger

logger = logging.getLogger(__name__)


class ProviderDialog(QgsAbstractDataSourceWidget):
    """
    Boite de dialogue de sélection des couches
    """

    def __init__(self, iface):
        super(ProviderDialog, self).__init__()

        self.iface = iface
        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "provider_dialog.ui"),
            self,
        )

        self.log = PlgLogger().log

        self.mdl_search_result = SearchResultModel()
        self.tbv_results.setModel(self.mdl_search_result)
        self.tbv_results.verticalHeader().setVisible(False)
        self.tbv_results.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbv_results.pressed.connect(self._item_clicked)
        self.tbv_results.doubleClicked.connect(self._add_layer)

        self.buttonBox.button(QDialogButtonBox.StandardButton.Apply).setText("Ajouter")
        self.buttonBox.button(QDialogButtonBox.StandardButton.Apply).setEnabled(False)

        self.tw_search.currentChanged.connect(self._clear_search)

        self.le_search.textChanged.connect(self._simple_search)
        self.le_title.textChanged.connect(self._advanced_search)
        self.le_keywords.textChanged.connect(self._advanced_search)
        self.buttonBox.clicked.connect(self.onAccept)

    def _clear_search(self):
        self.le_search.clear()
        self.le_title.clear()
        self.le_keywords.clear()
        self.metaTextBrowser.clear()
        self.mdl_search_result.clear()
        self.buttonBox.button(QDialogButtonBox.StandardButton.Apply).setEnabled(False)

    def _simple_search(self, text):
        if len(text) > 2:
            self.mdl_search_result.simple_search_text(text)

    def _advanced_search(self):
        search_dict = {}
        if len(self.le_title.text()) > 2:
            search_dict["title"] = self.le_title.text()
        if len(self.le_keywords.text()) > 2:
            search_dict["keywords"] = self.le_keywords.text()
        if len(search_dict.keys()) > 0:
            self.mdl_search_result.advanced_search_text(search_dict)

    def _item_clicked(self, index):
        self.buttonBox.button(QDialogButtonBox.StandardButton.Apply).setEnabled(True)
        self.metaTextBrowser.clear()
        result = self.mdl_search_result.get_result(index)
        if result:
            self.metaTextBrowser.setText(json.dumps(result, indent=2))

    def _add_layer(self, index):
        result = self.mdl_search_result.get_result(index)
        layer = None
        if result:
            if result["type"] == "WMS":
                url = f"crs={result['srs'][0]}&format=image/png&layers={result['layer_name']}&styles&url={result['url'].split('?')[0]}"
                layer = QgsRasterLayer(url, result["title"], "wms")

            if result["type"] == "TMS":
                params = read_tms_layer_capabilities(result["url"])
                if params["format"] == "pbf":
                    url = (
                        "type=xyz&crs="
                        + result["srs"][0]
                        + f"&zmax={params['zmax']}"
                        + f"&zmin={params['zmin']}"
                        + "&url="
                        + result["url"]
                        + "/{z}/{x}/{y}.pbf"
                    )
                    layer = QgsVectorTileLayer(url, result["title"])
                elif params["format"] is not None:
                    url = (
                        "type=xyz&crs="
                        + result["srs"][0]
                        + "&url="
                        + result["url"]
                        + "/{z}/{x}/{y}."
                        + params["format"]
                    )
                    layer = QgsRasterLayer(url, result["title"], "wms")

            if result["type"] == "WMTS":
                params = read_wmts_layer_capabilities(
                    result["url"].split("?")[0], result["layer_name"]
                )
                if params:
                    url = f"crs={result['srs'][0]}&format={params['format']}&layers={result['layer_name']}&styles={params['style']}&tileMatrixSet={params['tileMatrixSet']}&url={result['url'].split('?')[0]}?SERVICE%3DWMTS%26version%3D1.0.0%26request%3DGetCapabilities"
                    layer = QgsRasterLayer(url, result["title"], "wms")

            if result["type"] == "WFS":
                url = f"{result['url'].split('?')[0]}?typename={result['layer_name']}&version=auto"
                layer = QgsVectorLayer(url, result["title"], "WFS")

        if layer is not None:
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)
            else:
                self.log(
                    "Layer failed to load !",
                    log_level=2,
                    push=False,
                )

    def onAccept(self, button):
        """
        Lorsque l'utilisateur valide
        """
        if self.buttonBox.buttonRole(button) == QDialogButtonBox.ButtonRole.ApplyRole:
            indexes = self.tbv_results.selectedIndexes()
            if len(indexes) > 0:
                self._add_layer(indexes[0])
            self.accept()
