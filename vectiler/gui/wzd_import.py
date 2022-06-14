# standard

import os


# PyQGIS

from qgis.PyQt import uic
from PyQt5.QtWidgets import QWizard,QShortcut
from PyQt5 import QtCore, QtGui

# ############################################################################
# ########## Classes ###############
# ##################################

class WzdImport(QWizard):

    def __init__(self, parent=None):
        super().__init__(parent)
        
        """
        Dialog to define current geotuileur import data

        Args:
            parent: parent QObject
        """
        uic.loadUi(os.path.join(os.path.dirname(__file__), "wzd_import.ui"), self)

        # # To avoid some characters 
        rx=QtCore.QRegExp("[a-z-A-Z-0-9-_]+")
        validator = QtGui.QRegExpValidator(rx)
        self.lne_data.setValidator(validator)

        self.phb_ok.clicked.connect(self.file_path)

        self.shortcut_close = QShortcut(QtGui.QKeySequence('Del'), self)
        self.shortcut_close.activated.connect(self.shortcut_del)
        self.list_filepath=[]

    def shortcut_del(self) :
        """
         To create  shortcut which delete a filepath 

        """

        row = self.lvw_import_data.currentRow()
        item = self.lvw_import_data.takeItem(row)
        del item       
        
    def file_path(self):
        """
        to accept only a true file path and to show this only once  
         
        """

        savepath=self.flw_files_put.filePath()
        
        for i in range (0,len(self.list_filepath)):
            if savepath==self.list_filepath[i]:
                return

        if QtCore.QFileInfo(savepath).exists() :
            self.lvw_import_data.addItem(savepath)
            self.list_filepath.append(savepath)

