# from PyQt4.Qt import *
from qgis.gui import QgsAbstractDataSourceWidget

# from geoplateforme.__about__ import DIR_PLUGIN_ROOT
from geoplateforme.gui.provider import Ui_ProviderForm

# from qgis.PyQt.QtCore import QModelIndex, QSize, Qt
# from qgis.PyQt.QtWidgets import QDialogButtonBox


class ProviderDialog(QgsAbstractDataSourceWidget, Ui_ProviderForm):
    """
    Boite de dialogue de sélection des couches
    """

    def __init__(self, iface):
        super(ProviderDialog, self).__init__()

        self.iface = iface
        self.setupUi(self)

        # self._treeViewModel = LayerModel()
        # self._treeViewModel.setHorizontalHeaderLabels(["Couches"])
        # self._layerProxyModel = LayerProxyModel(self)
        # self._layerProxyModel.setSourceModel(self._treeViewModel)
        # self.treeView.setModel(self._layerProxyModel)
        # self._expansionList = None

        # self._treeViewModelWMTS = LayerModel()
        # self._treeViewModelWMTS.setHorizontalHeaderLabels(["Fonds de plan"])
        # self._layerProxyModelWMTS = LayerProxyModel(self)
        # self._layerProxyModelWMTS.setSourceModel(self._treeViewModelWMTS)
        # self.treeView_wmts.setModel(self._layerProxyModelWMTS)

        # self.buttonBox.button(QDialogButtonBox.Apply).setText("Ajouter")

        # # Gestion des icons pour le WMTS
        # self.treeView_wmts.setIconSize(QSize(96, 96))

        # # Avec ou sans alias
        # self.dictCheckBox.setChecked(ThemesDict.instance().getWithAlias())
        # self._showAlias = ThemesDict.instance().getWithAlias()

        # # groupes de fonds de plans

        # self._themerasters = [
        #     LayerThemeItem(theme, self._showAlias)
        #     for theme in ThemesDictRaster.instance().getThemes()
        # ]
        # for themeraster in self._themerasters:
        #     self._treeViewModelWMTS.appendRow(themeraster)

        # # Themes
        # self._themes = [
        #     LayerThemeItem(theme, self._showAlias)
        #     for theme in ThemesDict.instance().getThemes()
        #     if not theme.name.startswith("SOCL")
        # ]
        # for theme in self._themes:
        #     self._treeViewModel.appendRow(theme)
        # # Actions
        # self._registerActions()

        # for theme in self._themes:
        #     theme.setText(theme.text().replace("\\n", " "))
        #     for layer in theme.childs:
        #         layer.setText(layer.text().replace("\\n", " "))

    # def _registerActions(self):
    #     # GUI
    #     self.treeView.clicked.connect(self._onTreeViewClicked)
    #     self.treeView_wmts.clicked.connect(self._onTreeViewWMTSClicked)
    #     self.dictCheckBox.clicked.connect(self._onDictCheckboxClicked)
    #     self.lineEdit.textChanged.connect(self._onTextChanged)

    #     self.buttonBox.clicked.connect(self.onAccept)

    # def _onTextChanged(self, text):
    #     self._searchForLayer(text)

    # def _searchForLayer(self, text):
    #     self._layerProxyModel.textFilter = text
    #     self._layerProxyModel.invalidateFilter()
    #     if len(text) > 0:
    #         self.treeView.expandAll()
    #         self.treeView_wmts.expandAll()
    #     else:
    #         self.treeView.collapseAll()
    #         self.treeView_wmts.collapseAll()

    # def _saveExpansionState(self):
    #     self._expansionList = []
    #     self._expansionListWMTS = []

    #     # On appelle la fonction récursive sur la racine
    #     self._recSaveExpansionState(QModelIndex())

    # def _recSaveExpansionState(self, parent):
    #     for row in range(self._layerProxyModel.rowCount(parent)):
    #         index = self._layerProxyModel.index(row, 0, parent)
    #         if self.treeView.isExpanded(index):
    #             self._expansionList.append(index)
    #             if self._layerProxyModel.hasChildren(index):
    #                 self._recSaveExpansionState(index)

    #     for row in range(self._layerProxyModelWMTS.rowCount(parent)):
    #         index = self._layerProxyModelWMTS.index(row, 0, parent)
    #         if self.treeView_wmts.isExpanded(index):
    #             self._expansionListWMTS.append(index)
    #             if self._layerProxyModelWMTS.hasChildren(index):
    #                 self._recSaveExpansionState(index)

    # def _restoreExpansionState(self):
    #     for index in self._expansionList:
    #         self.treeView.setExpanded(index, True)

    #     for index in self._expansionListWMTS:
    #         self.treeView_wmts.setExpanded(index, True)

    #     self._expansionList = []
    #     self._expansionListWMTS = []

    # def _onDictCheckboxClicked(self):
    #     self._showAlias = self.dictCheckBox.isChecked()
    #     ThemesDict.instance().setWithAlias(self._showAlias)

    #     for theme in self._themes:
    #         theme.showText(self._showAlias)
    #         for layer in theme.childs:
    #             layer.showText(self._showAlias)
    #             for relation in layer.childs:
    #                 relation.showText(self._showAlias)

    #     for raster in self._themerasters:
    #         raster.showText(self._showAlias)
    #         for layer in raster.childs:
    #             layer.showText(self._showAlias)
    #             for relation in layer.childs:
    #                 relation.showText(self._showAlias)

    #     # Sauvegarde de l'état de déploiement de l'arbre
    #     self._saveExpansionState()

    #     # Lancement de la recherche
    #     self._searchForLayer(self.lineEdit.text())

    #     # Restauration de l'état de déploiement de l'arbre
    #     self._restoreExpansionState()

    # def _onTreeViewClicked(self, index):
    #     """
    #     @type index: QModelIndex
    #     """

    #     # Suppression du contenu des métadonnées
    #     self.metaTextBrowser.clear()

    #     root = self._treeViewModel.itemFromIndex(
    #         self._layerProxyModel.mapToSource(index)
    #     )
    #     if isinstance(root, LayerDefaultItem):
    #         root.switchCheckState()
    #     if isinstance(root, LayerThemeItem):
    #         root.setCheckStateChild()
    #     elif isinstance(root, LayerItem):
    #         if isinstance(root.parent(), LayerThemeItem):
    #             # Rafraichissement de l'état du parent
    #             root.parent().refreshCheckState()

    #         # Metadonnées de la couche
    #         _xsltTemplateFile = "{pluginDir}/templates/metadata.xslt".format(
    #             pluginDir=str(DIR_PLUGIN_ROOT)
    #         )
    #         _metaData = root.layer.getMetaData(xsltTemplateFile=_xsltTemplateFile)
    #         self.metaTextBrowser.document().setDefaultStyleSheet(
    #             ".panel-heading {\
    #                  background-color: lightgrey;\
    #              }"
    #         )
    #         self.metaTextBrowser.setHtml(
    #             _metaData if _metaData else "Pas de métadonnées pour cette couche"
    #         )

    # def _onTreeViewWMTSClicked(self, index):
    #     """
    #     @type index: QModelIndex
    #     """

    #     root = self._treeViewModelWMTS.itemFromIndex(
    #         self._layerProxyModelWMTS.mapToSource(index)
    #     )
    #     if isinstance(root, LayerDefaultItem):
    #         root.switchCheckState()
    #     if isinstance(root, LayerThemeItem):
    #         root.setCheckStateChild()
    #     elif isinstance(root, LayerItem):
    #         if isinstance(root.parent(), LayerThemeItem):
    #             # Rafraichissement de l'état du parent
    #             root.parent().refreshCheckState()

    # def initDialogState(self):
    #     for theme in self._themes:
    #         theme.setCheckState(Qt.Unchecked)
    #         theme.setCheckStateChild()
    #     self.treeView.collapseAll()

    #     for themeraster in self._themerasters:
    #         themeraster.setCheckState(Qt.Unchecked)
    #         themeraster.setCheckStateChild()
    #     self.treeView_wmts.collapseAll()

    # def onAccept(self, button):
    #     """
    #     Lorsque l'utilisateur valide
    #     """
    #     if self.buttonBox.buttonRole(button) == QDialogButtonBox.ApplyRole:
    #         for theme in self._themes:
    #             for layerItem in theme.childs:
    #                 themeLayer = layerItem.layer
    #                 if layerItem.checkState() == Qt.Checked:
    #                     if self.layerCheckBox.isChecked():
    #                         themeLayer.addLayerAndRelations(self._showAlias)
    #                     else:
    #                         themeLayer.addLayer(self._showAlias)
    #         for themeraster in self._themerasters:
    #             for layerItem in themeraster.childs:
    #                 themeLayer = layerItem.layer
    #                 if layerItem.checkState() == Qt.Checked:
    #                     themeLayer.addLayerRaster(self._showAlias)

    #         self.initDialogState()
    #         self.accept()
