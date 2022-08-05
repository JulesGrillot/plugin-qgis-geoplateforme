#! python3  # noqa: E265

"""
    Common GUI utils.
"""

# PyQGIS
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QApplication, QLabel, QLineEdit, QWidget

# plugin
from geotuileur.toolbelt import PlgLogger


class GuiCommonUtils:
    def copy_widget_txt_to_clipboard(
        self, wdg_source: QWidget, custom_log_header: str = None
    ) -> bool:
        """Copy source widget content into the system clipboard.

        :param wdg_source: widget source. Accepts only QLabel or QLineEdit.
        :type wdg_source: QWidget
        :param custom_log_header: customize the log header, defaults to None
        :type custom_log_header: str, optional

        :return: True if content has been copied
        :rtype: bool
        """

        if not isinstance(wdg_source, (QLabel, QLineEdit)):
            return False

        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(wdg_source.text(), mode=cb.Clipboard)

        # Refine the log message
        if custom_log_header:
            log_msg = custom_log_header
        elif isinstance(wdg_source, QLabel) and wdg_source.buddy():
            log_msg = wdg_source.buddy().text()
        else:
            log_msg = wdg_source.objectName()

        PlgLogger().log(
            message=log_msg + self.tr(" content has been copied into the clipboard."),
            push=True,
        )
        return True

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)
