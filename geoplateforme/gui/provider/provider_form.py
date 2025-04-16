from pathlib import Path

from qgis.PyQt import uic

FORM_CLASS, FORM_BASE = uic.loadUiType(
    Path(__file__).parent / "{}.ui".format(Path(__file__).stem)
)


class Ui_ProviderForm(FORM_CLASS, object):
    def __init__(self):
        super().__init__()
