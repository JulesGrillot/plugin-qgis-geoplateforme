import os

from qgis.PyQt import QtCore, QtGui, uic
from qgis.PyQt.QtWidgets import QWidget

from geotuileur.api.configuration import Configuration


class PublicationForm(QWidget):
    def __init__(self, parent=QWidget):
        """
        QWidget to for geotuileur data publication

        Args:
            parent: parent QWidget
        """

        super().__init__(parent)
        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "wdg_publication_form.ui"),
            self,
        )
        rx = QtCore.QRegExp("[a-z-A-Z-0-9-_-.--]+")
        validator = QtGui.QRegExpValidator(rx)

        rx_url = QtCore.QRegExp("^https://[a-zA-ZS-.---_-]*")
        validator_url = QtGui.QRegExpValidator(rx_url)

        self.lbl_flux_name.setValidator(validator)
        self.lbl_URL_legal.setValidator(validator_url)

    def get_config(self) -> Configuration:

        configuration = Configuration(
            type_data="",
            metadata=[],
            name=self.lbl_flux_name.text(),
            layer_name=self.lbl_flux_name.text(),
            type_infos={},
            attribution={},
        )

        configuration.title = self.lbl_descriptif_title.text()
        configuration.abstract = self.pte_abstract.toPlainText()
        configuration.url_title = self.lbl_legal_notice.text()
        configuration.url = self.lbl_URL_legal.text()

        return configuration
