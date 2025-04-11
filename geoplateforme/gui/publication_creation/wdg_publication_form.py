# standard
import os

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QMessageBox, QWidget

# Plugin
from geoplateforme.api.configuration import Configuration
from geoplateforme.gui.lne_validators import alphanum_qval, url_qval


class PublicationForm(QWidget):
    def __init__(self, parent=QWidget):
        """
        QWidget to for geoplateforme data publication

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

    def validatePage(self) -> bool:
        """
        Validate current page content by checking files

        Returns: True

        """
        if (
            len(self.lne_name.text()) == 0
            or len(self.lne_title.text()) == 0
            or len(self.txe_abstract.toPlainText()) == 0
            or len(self.lne_legal_notice.text()) == 0
            or len(self.lne_url_legal.text()) == 0
        ):
            valid = False
            QMessageBox.warning(
                self,
                self.tr("Missing informations."),
                self.tr("Please fill all fields."),
            )
        else:
            valid = True
        return valid

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

    def set_config(self, configuration: Configuration) -> None:
        self.lne_name.setText(configuration.name)
        self.lne_title.setText(configuration.title)
        self.txe_abstract.setPlainText(configuration.abstract)

        self.lne_legal_notice.setText(configuration.url_title)
        self.lne_url_legal.setText(configuration.url)
