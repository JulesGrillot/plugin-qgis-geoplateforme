# standard

import os

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QAbstractItemView, QShortcut, QWizard
from qgis.PyQt import uic

# PyQGIS


class WzdImport(QWizard):
    def __init__(self, parent=None):

        """
        Dialog to define current geotuileur import data

        Args:
            parent: parent QObject
        """

        super().__init__(parent)

        uic.loadUi(os.path.join(os.path.dirname(__file__), "wzd_import.ui"), self)

        # # To avoid some characters

        rx = QtCore.QRegExp("[a-z-A-Z-0-9-_]+")
        validator = QtGui.QRegExpValidator(rx)
        self.lne_data.setValidator(validator)

        self.lvw_import_data.setSelectionMode(QAbstractItemView.MultiSelection)

        self.phb_ok.clicked.connect(self.add_file_path)

        self.shortcut_close = QShortcut(QtGui.QKeySequence("Del"), self)
        self.shortcut_close.activated.connect(self.shortcut_del)

    def shortcut_del(self):

        """
        Create  shortcut which delete a filepath

        """
        for x in self.lvw_import_data.selectedIndexes():

            row = x.row()
            item = self.lvw_import_data.takeItem(row)
            del item

    def add_file_path(self):

        """
        Add the file path to the list Widget

        """
        savepath = self.flw_files_put.filePath()
        print(savepath)
        items = self.lvw_import_data.findItems(savepath, QtCore.Qt.MatchCaseSensitive)

        if QtCore.QFileInfo(savepath).exists():
            if len(items) == 0:
                self.lvw_import_data.addItem(savepath)
