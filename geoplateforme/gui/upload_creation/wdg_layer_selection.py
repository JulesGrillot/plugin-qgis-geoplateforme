# standard
import os
from typing import List, Optional

# PyQGIS
from qgis.core import QgsProject, QgsVectorLayer
from qgis.gui import (
    QgsPanelWidget,
    QgsPanelWidgetStack,
    QgsProcessingMultipleInputDialog,
    QgsProcessingMultipleInputPanelWidget,
)
from qgis.PyQt import QtGui, uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import QAbstractItemView, QShortcut, QWidget

# Plugin
from geoplateforme.gui.upload_creation.mdl_upload_files import UploadFilesTreeModel
from geoplateforme.processing.upload_from_layers import GpfUploadFromLayersAlgorithm


class LayerSelectionWidget(QgsPanelWidget):
    selection_updated = pyqtSignal()

    def __init__(self, parent: QWidget = None):
        """Widget to select layer for upload creation

        :param parent: parent widget, defaults to None
        :type parent: QWidget, optional
        """
        super().__init__(parent)

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "wdg_layer_selection.ui"), self
        )

        # Shortcut for layer/file remove
        self.shortcut_del = QShortcut(QtGui.QKeySequence("Del"), self)
        self.shortcut_del.activated.connect(self._remove_selected_rows)

        # Get parameter for layers definition
        processing = GpfUploadFromLayersAlgorithm()
        self.layer_parameter = processing.layer_parameter()
        self.wdg_layer_input: Optional[QgsProcessingMultipleInputPanelWidget] = None

        # Create model for layer/file display
        self.mdl_upload_files = UploadFilesTreeModel(self)
        self.trv_upload_files.setModel(self.mdl_upload_files)
        self.trv_upload_files.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        # Connect for layer selection panel display
        self.btn_open.clicked.connect(self._select_layer)

        self.last_selection: Optional[List[str]] = None

    def _remove_selected_rows(self):
        """
        Remove selected rows

        """
        rows = [x.row() for x in self.trv_upload_files.selectedIndexes()]
        rows.sort(reverse=True)
        for row in rows:
            self.mdl_upload_files.removeRow(row)

    def _select_layer(self):
        """Select layer"""

        selected_options = []
        if self.last_selection:
            selected_options = self.last_selection

        panel = self.findParentPanel(self)
        if panel and panel.dockMode():
            # Display panel for multiple input selection
            self.wdg_layer_input = QgsProcessingMultipleInputPanelWidget(
                self.layer_parameter,
                selected_options,
                [],
                None,
                None,
            )
            self.wdg_layer_input.setPanelTitle(self.layer_parameter.description())
            self.wdg_layer_input.setProject(QgsProject.instance())

            # Update selection from panel
            self.wdg_layer_input.selectionChanged.connect(
                lambda: self._set_selected_options(
                    self.wdg_layer_input.selectedOptions()
                )
            )
            self.wdg_layer_input.acceptClicked.connect(self.wdg_layer_input.acceptPanel)

            # Define current panel
            panel.openPanel(self.wdg_layer_input)
        else:
            # Display dialog for
            dialog = QgsProcessingMultipleInputDialog(
                self.layer_parameter, selected_options, [], None, self
            )
            dialog.setProject(QgsProject.instance())
            if dialog.exec():
                # Update selection
                self._set_selected_options(dialog.selectedOptions())

    def _set_selected_options(self, selected_options: List[str]) -> None:
        """Define layer and files from a QgsProcessingMultipleInputPanelWidget/QgsProcessingMultipleInputDialog selection option
        It can define layer id or path to file

        :param selected_options: selected option
        :type selected_options: List[str]
        """

        self.mdl_upload_files.clear_values()
        for selection in selected_options:
            layer = QgsProject.instance().mapLayer(selection)
            if layer:
                self.mdl_upload_files.add_layer(layer)
            else:
                self.mdl_upload_files.add_file(selection)

            self.trv_upload_files.resizeColumnToContents(self.mdl_upload_files.NAME_COL)
            self.trv_upload_files.expandAll()
        if self.last_selection != selected_options:
            self.selection_updated.emit()
        self.last_selection = selected_options

    def get_layers(self) -> List[QgsVectorLayer]:
        """Return selected QgsVectorLayer

        :return: selected layer
        :rtype: List[QgsVectorLayer]
        """
        return self.mdl_upload_files.get_layers()

    def get_filenames(self) -> List[str]:
        """Return selected files

        :return: selected files
        :rtype: [str]
        """
        return self.mdl_upload_files.get_filenames()

    def get_first_displayed_name(self) -> str:
        """Get first displayed name

        :return: first display name defined
        :rtype: str
        """
        return self.mdl_upload_files.get_first_displayed_name()

    def get_first_crs(self) -> str:
        """Get first defined crs auth id, empty str if no crs defined

        :return: first defined crs
        :rtype: str
        """
        return self.mdl_upload_files.get_first_crs()


class LayerSelectionStackPanel(QgsPanelWidgetStack):
    selection_updated = pyqtSignal()

    def __init__(self, parent: QWidget = None):
        """Widget to select layer for upload creation with stack used for multiple layer selection

        :param parent: parent, defaults to None
        :type parent: QWidget, optional
        """
        super().__init__(parent)

        self.wdg_layer_selection_panel = LayerSelectionWidget()
        self.wdg_layer_selection_panel.setDockMode(True)
        self.wdg_layer_selection_panel.selection_updated.connect(
            lambda: self.selection_updated.emit()
        )
        self.setMainPanel(self.wdg_layer_selection_panel)

    def get_layers(self) -> List[QgsVectorLayer]:
        """Return selected QgsVectorLayer

        :return: selected layer
        :rtype: List[QgsVectorLayer]
        """
        return self.wdg_layer_selection_panel.get_layers()

    def get_filenames(self) -> List[str]:
        """Return selected files

        :return: selected files
        :rtype: [str]
        """
        return self.wdg_layer_selection_panel.get_filenames()

    def get_first_displayed_name(self) -> str:
        """Get first displayed name

        :return: first display name defined
        :rtype: str
        """
        return self.wdg_layer_selection_panel.get_first_displayed_name()

    def get_first_crs(self) -> str:
        """Get first defined crs auth id, empty str if no crs defined

        :return: first defined crs
        :rtype: str
        """
        return self.wdg_layer_selection_panel.get_first_crs()
