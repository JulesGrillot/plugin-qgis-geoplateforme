import os

from qgis.core import QgsApplication, QgsProcessingContext, QgsProcessingFeedback
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QWidget


class UserKeyCreationDialog(QDialog):
    def __init__(self, parent: QWidget):
        """
        QDialog for user key creation

        Args:
            parent: parent QWidget
        """
        super().__init__(parent)

        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "dlg_user_key_creation.ui"),
            self,
        )
        self.setWindowTitle(self.tr("Création d'une clé"))

    def accept(self) -> None:
        """Create user key from creation widget.
        Dialog is not closed if an error occurs during creation
        """

        algo_str = self.wdg_user_key_creation.get_creation_algo_str()
        params = self.wdg_user_key_creation.get_creation_parameters()

        alg = QgsApplication.processingRegistry().algorithmById(algo_str)

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        _, success = alg.run(params, context, feedback)

        if not success:
            QMessageBox.warning(
                self,
                self.tr("Erreur lors de la création de la clé."),
                feedback.textLog(),
            )
            return None

        return super().accept()
