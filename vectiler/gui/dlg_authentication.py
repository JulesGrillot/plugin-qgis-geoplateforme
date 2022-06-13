import os

# PyQGIS
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QDialog
from qgis.PyQt import uic, QtCore, QtGui
from qgis.PyQt.QtGui import QDesktopServices


class AuthenticationDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "dlg_authentication.ui"), self)

        rx = QtCore.QRegExp("[a-z-A-Z-0-9-_.@]+")
        validator = QtGui.QRegExpValidator(rx)
        self.lbl_userEdit.setValidator(validator)

        # Click and Open URl
        self.clb_url.clicked.connect(lambda: self.openUrl())
        self.clb_forgot.clicked.connect(lambda: self.openUrl())

    def openUrl(self):
        QDesktopServices.openUrl(
            QUrl(str('https://qlf-portail-gpf-beta.ign.fr'))
        )
