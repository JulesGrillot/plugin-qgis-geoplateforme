# standard
import os
from typing import Optional

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QRegularExpression
from qgis.PyQt.QtGui import QRegularExpressionValidator
from qgis.PyQt.QtWidgets import QWidget

# Project
from geoplateforme.api.configuration import WfsRelation


class TableRelationWidget(QWidget):
    def __init__(
        self,
        parent=None,
    ):
        """
        QWidget to define relation for a table

        Args:
            parent: parent None

        """

        super().__init__(parent)

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "wdg_table_relation.ui"), self
        )

        # Issue when publishing with a public name with spaces. Using validator
        # ASCII letters :  A-Za-z
        # with accent : À-ÖØ-öø-ÿ
        # numeric : 0-9
        # underscore : _
        # dash : \\- (need escape)
        # point : \\. (need escape)
        alphanum_with_accent_qreg = QRegularExpression("[A-Za-zÀ-ÖØ-öø-ÿ0-9_\\-\\.]+")
        alphanum_with_accent_qval = QRegularExpressionValidator(
            alphanum_with_accent_qreg
        )

        self.lne_public_name.setValidator(alphanum_with_accent_qval)

    def set_table_name(self, table_name: str) -> None:
        """Define table name

        :param table_name: table name
        :type table_name: str
        """
        self.grp_table.setTitle(table_name)

    def get_relation(self) -> Optional[WfsRelation]:
        """Get WfsRelation for a table

        :return: None if table is not selected, WfsRelation otherwise
        :rtype: Optional[WfsRelation]
        """
        result = None
        if self.grp_table.isChecked():
            return WfsRelation(
                native_name=self.grp_table.title(),
                title=self.lne_title.text(),
                abstract=self.txt_abstract.toPlainText(),
                public_name=self.lne_public_name.text(),
                keywords=self.lne_keywords.text().split(","),
            )

        return result
