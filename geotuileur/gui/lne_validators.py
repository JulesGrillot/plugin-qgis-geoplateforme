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


# alphanumeric
alphanum_qreg = QRegularExpression("[a-z-A-Z-0-9-_]+")
alphanum_qval = QRegularExpressionValidator(alphanum_qreg)

# alphanumeric extended
alphanumx_qreg = QRegularExpression("[a-z-A-Z-0-9-_-.--]+")
alphanumx_qval = QRegularExpressionValidator(alphanumx_qreg)

# emails
email_qreg = QRegularExpression(
    "\\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,4}\\b",
    QRegularExpression.CaseInsensitiveOption,
)
email_qval = QRegularExpressionValidator(email_qreg)

# URL
url_qreg = QRegularExpression(
    "^https?://(?:[-\w.\/]|(?:%[\da-fA-F]{2}))+",
    QRegularExpression.UseUnicodePropertiesOption,
)
url_qval = QRegularExpressionValidator(url_qreg)
