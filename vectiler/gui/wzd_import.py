# standard
from pathlib import Path

import os

# PyQGIS

from qgis.PyQt import uic
from qgis.core import QgsProject
from PyQt5.QtWidgets import QWizard
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QRegExpValidator 
from PyQt5.QtCore import QRegExp

from vectiler.__about__ import (
DIR_PLUGIN_ROOT,
__title__,
__uri_homepage__,
__uri_tracker__,
__version__,
)

# ############################################################################
# ########## Globals ###############
# ##################################

FORM_CLASS, _ = uic.loadUiType(
Path(__file__).parent / "{}.ui".format(Path(__file__).stem)
)

# ############################################################################
# ########## Classes ###############
# ##################################

class wzd_import(QWizard):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project = QgsProject.instance()
        self.importUI = uic.loadUi(
        os.path.join(os.path.dirname(__file__), "wzd_import.ui"), self )

        # # To avoid some characters 
        rx=QtCore.QRegExp("[a-z-A-Z-0-9-_]+")
        validator = QtGui.QRegExpValidator(rx)
        self.lne_data.setValidator(validator)

        # # To import files 
        self.phb_ok.clicked.connect(self.file_path)
        self.lwg_files_summary.setAcceptDrops(True)

    def file_path(self):
        savepath=self.flw_files_put.filePath()
        self.lwg_files_summary.append(savepath)