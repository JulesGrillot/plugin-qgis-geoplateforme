# standard
import os
from typing import Optional

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QMessageBox, QWizardPage
from qgis.utils import OverrideCursor

from geoplateforme.api.configuration import WfsRelation
from geoplateforme.api.stored_data import StoredDataStatus, StoredDataType
from geoplateforme.gui.wfs_publication.wdg_table_relation import TableRelationWidget


class TableRelationPageWizard(QWizardPage):
    def __init__(
        self,
        parent=None,
        datastore_id: Optional[str] = None,
        dataset_name: Optional[str] = None,
        stored_data_id: Optional[str] = None,
    ):
        """
        QWizardPage to define table relation for a WFS publication

        Args:
            parent: parent None
            datastore_id: datastore id
            dataset_name: dataset name
            stored_data_id: store data id

        """

        super().__init__(parent)
        self.setTitle(self.tr("Describe and publish your tiles"))

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "qwp_table_relation.ui"), self
        )
        self.table_relation_widgets = []

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
        table_relation = self.get_selected_table_relations()
        if len(table_relation) == 0:
            QMessageBox.warning(
                self,
                self.tr("Aucune table sélectionnée"),
                self.tr("Veuillez choisir au moins une table."),
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
            self.table_relation_widgets = []

            stored_data = self.cbx_stored_data.current_stored_data()
            if stored_data:
                for table in stored_data.get_tables():
                    wdg_table_relation = TableRelationWidget(self)
                    wdg_table_relation.set_table_name(table.name)
                    self.lyt_table_relation.addWidget(wdg_table_relation)
                    self.table_relation_widgets.append(wdg_table_relation)

    def get_selected_table_relations(self) -> list[WfsRelation]:
        """Get selected table relation for WFS publish

        :return: selected table relation
        :rtype: list[WfsRelation]
        """
        result = []
        for wdg_table_relation in self.table_relation_widgets:
            if table_relation := wdg_table_relation.get_relation():
                result.append(table_relation)

        return result
