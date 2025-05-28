# standard
import os
from typing import Optional

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QMessageBox, QWizardPage
from qgis.utils import OverrideCursor

from geoplateforme.api.configuration import WmsVectorTableStyle
from geoplateforme.api.stored_data import StoredDataStatus, StoredDataType
from geoplateforme.gui.wms_vector_publication.wdg_table_style_selection import (
    TableStyleSelectionWidget,
)


class TableRelationPageWizard(QWizardPage):
    def __init__(
        self,
        parent=None,
        datastore_id: Optional[str] = None,
        dataset_name: Optional[str] = None,
        stored_data_id: Optional[str] = None,
    ):
        """
        QWizardPage to define table relation for a WMS-VECTOR publication

        Args:
            parent: parent None
            datastore_id: datastore id
            dataset_name: dataset name
            stored_data_id: store data id

        """

        super().__init__(parent)
        self.setTitle(self.tr("Créer et publier un service WMS-Vecteur"))

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "qwp_table_style_selection.ui"),
            self,
        )
        self.table_style_widgets = []

        # Only display vector db ready for publication
        self.cbx_stored_data.set_filter_type([StoredDataType.VECTORDB])
        self.cbx_stored_data.set_visible_status([StoredDataStatus.GENERATED])

        self.cbx_datastore.currentIndexChanged.connect(self._datastore_updated)
        self.cbx_dataset.currentIndexChanged.connect(self._dataset_updated)
        self.cbx_stored_data.currentIndexChanged.connect(self._stored_data_updated)

        if datastore_id:
            self.set_datastore_id(datastore_id)
            self.cbx_datastore.setEnabled(False)
        self._datastore_updated()

        if dataset_name:
            self.set_dataset_name(dataset_name)
            self.cbx_dataset.setEnabled(False)
        self._dataset_updated()

        if stored_data_id:
            self.set_stored_data_id(stored_data_id)
            self.cbx_stored_data.setEnabled(False)
        self._stored_data_updated()

        self.setCommitPage(False)

    def set_datastore_id(self, datastore_id: str) -> None:
        """
        Define current datastore from datastore id

        Args:
            datastore_id: (str) datastore id
        """
        self.cbx_datastore.set_datastore_id(datastore_id)

    def set_dataset_name(self, dataset_name: str) -> None:
        """
        Define current dataset name

        Args:
            dataset_name: (str) dataset name
        """
        self.cbx_dataset.set_dataset_name(dataset_name)

    def set_stored_data_id(self, stored_data_id: str) -> None:
        """
        Define current stored data from stored data id

        Args:
            stored_data_id: (str) stored data id
        """
        self.cbx_stored_data.set_stored_data_id(stored_data_id)

    def validatePage(self) -> bool:
        """
        Validate current page content by checking files

        Returns: True

        """
        table_styles = self.get_selected_table_styles()
        if len(table_styles) == 0:
            QMessageBox.warning(
                self,
                self.tr("Aucune table sélectionnée"),
                self.tr("Veuillez choisir au moins une table."),
            )
            return False

        errors: list[str] = []
        for table_style in table_styles:
            if not table_style.stl_file:
                errors.append(
                    self.tr("Fichier de style .sld non défini pour la table {}").format(
                        table_style.native_name
                    )
                )
        if errors:
            QMessageBox.warning(
                self,
                self.tr("Champs manquants"),
                "\n".join(errors),
            )
            return False

        return True

    def _datastore_updated(self) -> None:
        """
        Update dataset combobox when datastore is updated

        """
        with OverrideCursor(Qt.CursorShape.WaitCursor):
            self.cbx_dataset.currentIndexChanged.disconnect(self._dataset_updated)
            self.cbx_dataset.set_datastore_id(self.cbx_datastore.current_datastore_id())
            self.cbx_dataset.currentIndexChanged.connect(self._dataset_updated)
            self._dataset_updated()

    def _dataset_updated(self) -> None:
        """
        Update stored data combobox when dataset is updated

        """
        with OverrideCursor(Qt.CursorShape.WaitCursor):
            self.cbx_stored_data.set_datastore(
                self.cbx_datastore.current_datastore_id(),
                self.cbx_dataset.current_dataset_name(),
            )

    @staticmethod
    def clear_layout(layout):
        """Clear a layout from all added widget

        :param layout: layout to clear
        :type layout: any Qt type layouy
        """
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    layout.removeItem(item)

    def _stored_data_updated(self) -> None:
        """
        Update displayed table relation when stored data is updated
        """
        with OverrideCursor(Qt.CursorShape.WaitCursor):
            self.clear_layout(self.lyt_table_relation)
            self.table_style_widgets = []

            stored_data = self.cbx_stored_data.current_stored_data()
            if stored_data:
                for table in stored_data.get_tables():
                    wdg_table_style = TableStyleSelectionWidget(self)
                    wdg_table_style.set_table_name(table.name)
                    self.lyt_table_relation.addWidget(wdg_table_style)
                    self.table_style_widgets.append(wdg_table_style)

    def get_selected_table_styles(self) -> list[WmsVectorTableStyle]:
        """Get selected table style for WMS-Vector publish

        :return: selected table relation
        :rtype: list[WmsVectorTableStyle]
        """
        result = []
        for wdg_table_style in self.table_style_widgets:
            if table_relation := wdg_table_style.get_relation():
                result.append(table_relation)

        return result
