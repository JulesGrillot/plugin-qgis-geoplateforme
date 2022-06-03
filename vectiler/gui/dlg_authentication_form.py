# standard
from pathlib import Path

import os

# PyQGIS
from qgis.PyQt import uic
from qgis.core import  QgsProject
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtCore import QCoreApplication,QUrl
from PyQt5 import QtCore,Qt
from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
from vectiler.__about__ import (
    DIR_PLUGIN_ROOT,
    __title__,
    __uri_homepage__,
    __uri_tracker__,
    __version__,
)
from qgis.PyQt.QtGui import QDesktopServices, QIcon
# ############################################################################
# ########## Globals ###############
# ##################################

FORM_CLASS, _ = uic.loadUiType(
    Path(__file__).parent / "{}.ui".format(Path(__file__).stem)
)


# ############################################################################
# ########## Classes ###############
# ##################################

class dlg_authentication_form(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project = QgsProject.instance()
        self.authenticationUI = uic.loadUi(
        os.path.join(os.path.dirname(__file__), "dlg_authentication_form.ui"), self )

# To avoid some characters 

        rx=QtCore.QRegExp("[a-z-A-Z-0-9-_]+")
        validator = QtGui.QRegExpValidator(rx)
        self.lbl_userEdit.setValidator(validator)

# Click and Open URl
        self.clb_url.clicked.connect(lambda : self.openUrl())
        self.clb_forgot.clicked.connect(lambda : self.openUrl())

    def openUrl(self):   
        QDesktopServices.openUrl(
            QUrl(str('https://qlf-portail-gpf-beta.ign.fr'))
        )

