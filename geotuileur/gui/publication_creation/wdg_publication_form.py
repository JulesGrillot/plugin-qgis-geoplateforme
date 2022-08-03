# standard
import os

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWidget

# Plugin
from geotuileur.api.configuration import Configuration
from geotuileur.gui.lne_validators import alphanum_qval, url_qval


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

        self.lne_name.setValidator(alphanum_qval)
        self.lne_url_legal.setValidator(url_qval)

    def get_config(self) -> Configuration:

        configuration = Configuration(
            type_data="",
            metadata=[],
            name=self.lne_name.text(),
            layer_name=self.lne_name.text(),
            type_infos={},
            attribution={},
        )

        configuration.title = self.lne_title.text()
        configuration.abstract = self.txe_abstract.toPlainText()
        configuration.url_title = self.lne_legal_notice.text()
        configuration.url = self.lne_url_legal.text()

        return configuration
