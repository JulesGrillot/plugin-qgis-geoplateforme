# standard
import os
from typing import Dict, List

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWizardPage

from geotuileur.gui.mdl_table_relation import TableRelationTreeModel
from geotuileur.gui.tile_creation.qwp_tile_generation_edition import (
    TileGenerationEditionPageWizard,
)


class TileGenerationFieldsSelectionPageWizard(QWizardPage):
    def __init__(
        self, qwp_tile_generation_edition: TileGenerationEditionPageWizard, parent=None
    ):

        """
        QWizardPage to define fields for tile generation

        Args:
            parent: parent QObject
        """

        super().__init__(parent)
        self.setTitle(self.tr("Customize your vector tiles service"))
        self.qwp_tile_generation_edition = qwp_tile_generation_edition

        uic.loadUi(
            os.path.join(
                os.path.dirname(__file__), "qwp_tile_generation_fields_selection.ui"
            ),
            self,
        )

        self.mdl_table_relation = TableRelationTreeModel(self)
        self.tw_table_relation.setModel(self.mdl_table_relation)
        self.tw_table_relation.setSortingEnabled(True)

    def initializePage(self) -> None:
        """
        Initialize page before show.

        """
        datastore_id = (
            self.qwp_tile_generation_edition.cbx_datastore.current_datastore_id()
        )
        stored_data_id = (
            self.qwp_tile_generation_edition.cbx_stored_data.current_stored_data_id()
        )

        self.mdl_table_relation.set_stored_data(datastore_id, stored_data_id)

    def get_selected_attributes(self) -> Dict[str, List[str]]:
        """
        Get list of selected attributes

        Returns: {str:[str]} map of selected attributes for each table

        """
        attributes = {}
        tables_attributes = self.mdl_table_relation.get_selected_table_attributes()
        for table, table_attributes in tables_attributes.items():
            attributes[table] = table_attributes
        return attributes
