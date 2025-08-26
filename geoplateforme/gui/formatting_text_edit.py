"""A text editor with button for formatting"""

# standard
from functools import partial
from typing import List

# PyQGIS
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QContextMenuEvent, QIcon, QKeySequence
from qgis.PyQt.QtWidgets import QAction, QTextEdit

# project
from geoplateforme.__about__ import DIR_PLUGIN_ROOT

SINGLE_LINE_CODE_SEPARATOR = "`"
BLOCK_CODE_SEPARATOR = "```"


class FormattingTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.textChanged.connect(self.updateGeometry)

        self._edit_actions = []

        format_buttons = [
            {
                "description": self.tr("Bold"),
                "text": "**",
                "icon": str(DIR_PLUGIN_ROOT / "resources/images/bold.svg"),
                "shortcut": QKeySequence(self.tr("Ctrl+B", "Bold")),
            },
            {
                "description": self.tr("Italic"),
                "text": "*",
                "icon": str(DIR_PLUGIN_ROOT / "resources/images/italic.svg"),
                "shortcut": QKeySequence(self.tr("Ctrl+I", "Italic")),
            },
            {
                "description": self.tr("Strike"),
                "text": "~~",
                "icon": str(DIR_PLUGIN_ROOT / "resources/images/strikethrough.svg"),
            },
        ]

        for button in format_buttons:
            action = QAction(QIcon(button["icon"]), button["description"], self)
            action.triggered.connect(
                partial(self.insert_after_and_before_selection, button["text"])
            )
            if "shortcut" in button:
                action.setShortcut(button["shortcut"])
                # action.setShortcutContext(Qt.ShortcutContext.WidgetShortcut)
                action.setShortcutContext(Qt.ShortcutContext.WidgetShortcut)
                self.addAction(action)

            self._edit_actions.append(action)

        self._insert_separator_in_edit_action()
        code_action = QAction(
            QIcon(str(DIR_PLUGIN_ROOT / "resources/images/code.svg")),
            self.tr("Insert code"),
        )
        code_action.triggered.connect(self.insert_code_for_selection)
        self._edit_actions.append(code_action)

    def get_edit_actions(self) -> List[QAction]:
        """Get list of actions available for edition, contains separators

        :return: list of action for edition
        :rtype: List[QAction]
        """
        return self._edit_actions

    def _insert_separator_in_edit_action(self) -> QAction:
        """Insert a QAction as separator in internal edit actions

        :return: _description_
        :rtype: QAction
        """
        sep = QAction(self)
        sep.setSeparator(True)
        self._edit_actions.append(sep)
        return sep

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        """Display context menu for right click

        :param event: _description_
        :type event: QContextMenuEvent
        """
        # Get standard menu for QTextEdit
        menu = self.createStandardContextMenu()

        # Add custom edit action
        menu.addSeparator()
        for action in self._edit_actions:
            menu.addAction(action)

        menu.exec(event.globalPos())

    def insert_after_and_before_selection(self, text: str) -> None:
        """Insert text after and before current selection

        :param text: text to insert
        :type text: str
        """
        cursor = self.textCursor()
        cursor.insertText(f"{text}{cursor.selectedText()}{text}")

    def insert_code_for_selection(self) -> None:
        """Insert code separator for selection
        ` if a single line is selected
        ```
        ```
        if multiple line are selected
        """
        cursor = self.textCursor()
        selection = cursor.selection().toPlainText()
        if "\n" in selection:
            cursor.insertText(BLOCK_CODE_SEPARATOR)
            cursor.insertText("\n")
            cursor.insertText(selection)
            cursor.insertText("\n")
            cursor.insertText(BLOCK_CODE_SEPARATOR)
        else:
            cursor.insertText(
                f"{SINGLE_LINE_CODE_SEPARATOR}{selection}{SINGLE_LINE_CODE_SEPARATOR}"
            )
