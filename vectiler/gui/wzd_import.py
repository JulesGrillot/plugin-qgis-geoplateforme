# standard

import os

# PyQGIS

from qgis.PyQt import uic
from PyQt5.QtWidgets import QWizard, QShortcut
from PyQt5 import QtCore, QtGui


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

        self.phb_ok.clicked.connect(self.add_file_path)

        self.shortcut_close = QShortcut(QtGui.QKeySequence('Del'), self)
        self.shortcut_close.activated.connect(self.shortcut_del)

    def shortcut_del(self):
        """
         To create  shortcut which delete a filepath 

        """

        row = self.lvw_import_data.currentRow()
        item = self.lvw_import_data.takeItem(row)
        del item

    def add_file_path(self):

        """ 
        to accept only a true file path and to show this only once  

        """

        savepath = self.flw_files_put.filePath()

        items = self.lvw_import_data.findItems(savepath, QtCore.Qt.MatchCaseSensitive)

        if QtCore.QFileInfo(savepath).exists():
            if len(items) == 0:
                self.lvw_import_data.addItem(savepath)
