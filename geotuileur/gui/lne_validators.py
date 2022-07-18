#! python3  # noqa: E265

"""
    Some useful validators for Qt Line Edit.
"""

# PyQGIS
from qgis.PyQt.QtCore import QRegularExpression
from qgis.PyQt.QtGui import QRegularExpressionValidator

# ############################################################################
# ########## Validators ############
# ##################################

# emails
email_qreg = QRegularExpression(
    "\\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,4}\\b",
    QRegularExpression.CaseInsensitiveOption,
)
email_qval = QRegularExpressionValidator(email_qreg)
