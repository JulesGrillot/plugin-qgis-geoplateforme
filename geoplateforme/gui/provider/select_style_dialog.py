from qgis.PyQt.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
)


class SelectStyleDialog(QDialog):
    def __init__(self, styles: list[str]):
        super().__init__()

        self.setWindowTitle("Choose TMS style")

        QBtn = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        message = QLabel("""
            <b>Please choose between available styles.</b>
        """)
        self.style_combo = QComboBox()
        for style in styles:
            self.style_combo.addItem(style)
        layout.addWidget(message)
        layout.addWidget(self.style_combo)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
