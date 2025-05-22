# standard
import os
from typing import Optional

# PyQGIS
from qgis.PyQt import uic
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
