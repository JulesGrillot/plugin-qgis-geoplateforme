# standard
from pathlib import Path

import os

# PyQGIS
from qgis.PyQt import uic
from qgis.core import  QgsProject
from qgis.PyQt.QtWidgets import QDialog

# project
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

class dlg_authentication_form(FORM_CLASS,QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.project = QgsProject.instance()
        self.Formulaire = uic.loadUi(
            os.path.join(os.path.dirname(__file__), "dlg_authentication_form.ui"), self
        )
        print(os.path.dirname(__file__))

