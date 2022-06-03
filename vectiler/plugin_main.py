#! python3  # noqa: E265

"""
    Main plugin module.
"""
import os
import sys
# PyQGIS
from qgis.core import QgsApplication,QgsProject
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QCoreApplication,QUrl
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction,QPushButton,QToolBar
from qgis.utils import showPluginHelp
from qgis.PyQt.QtGui import QDesktopServices, QIcon
# project
from vectiler.__about__ import __title__
from vectiler.gui.wzd_import import wzd_import
from vectiler.gui.dlg_settings import PlgOptionsFactory
from vectiler.processing import VectilerProvider
from vectiler.toolbelt import PlgLogger, PlgTranslator
from vectiler.gui.dlg_authentication_form import dlg_authentication_form

# from vectiler.gui.wzd_import import wzd_import

# ############################################################################
# ########## Classes ###############
# ##################################


class VectilerPlugin:
    def __init__(self, iface: QgisInterface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class which \
        provides the hook by which you can manipulate the QGIS application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface
        self.log = PlgLogger().log
        self.provider = None

        # translation
        plg_translation_mngr = PlgTranslator()
        translator = plg_translation_mngr.get_translator()
        if translator:
            QCoreApplication.installTranslator(translator)
        self.tr = plg_translation_mngr.tr

    def initGui(self):
        """Set up plugin UI elements."""

        # settings page within the QGIS preferences menu
        self.options_factory = PlgOptionsFactory()
        self.iface.registerOptionsWidgetFactory(self.options_factory)


        # functions to keep the windows open 
        def authentication_form ():
            self.project = QgsProject.instance()
            self.window = dlg_authentication_form()
            self.window.show()

        def import_data ():
            self.project = QgsProject.instance()
            self.window = wzd_import()
            self.window.show()
            
         
        # -- Actions
        self.action_help = QAction(
            QIcon(":/images/themes/default/mActionHelpContents.svg"),
            self.tr("Help", context="VectilerPlugin"),
            self.iface.mainWindow(),
        )
        self.action_help.triggered.connect(
            lambda: showPluginHelp(filename="resources/help/index")
        )

        self.action_settings = QAction(
            QgsApplication.getThemeIcon("console/iconSettingsConsole.svg"),
            self.tr("Settings"),
            self.iface.mainWindow(),
        )
        self.action_settings.triggered.connect(
            lambda: self.iface.showOptionsDialog(
                currentPage="mOptionsPage{}".format(__title__)
            )
        )
        # -- Menu
        self.iface.addPluginToMenu(__title__, self.action_settings)
        self.iface.addPluginToMenu(__title__, self.action_help)
        self.toolbar_auth = QToolBar("authentication form")
        self.iface.addToolBar(self.toolbar_auth)
        self.toolbar_import = QToolBar("import data")
        self.iface.addToolBar(self.toolbar_import)

        # -- Processing
        self.initProcessing()

        icon = QIcon(QgsApplication.iconPath("console/iconShowEditorConsole.svg"))
        self.btn_autentification = QPushButton(icon, "Login")
        self.btn_autentification.clicked.connect(authentication_form)
        self.toolbar_auth.addWidget(self.btn_autentification)
        self.window = dlg_authentication_form(self.iface.mainWindow())
        


        icon = QIcon(QgsApplication.iconPath("console/iconSearchEditorConsole.svg"))
        self.btn_import = QPushButton(icon, "import data")
        self.btn_import.clicked.connect(import_data)
        self.toolbar_import.addWidget(self.btn_import)
        self.window = wzd_import(self.iface.mainWindow())




    def initProcessing(self):
        self.provider = VectilerProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        """Cleans up when plugin is disabled/uninstalled."""
        # -- Clean up menu
        self.iface.removePluginMenu(__title__, self.action_help)
        self.iface.removePluginMenu(__title__, self.action_settings)
        # remove toolbar :
        self.toolbar_auth.deleteLater()
        self.toolbar_import.deleteLater()
        # -- Clean up preferences panel in QGIS settings
        self.iface.unregisterOptionsWidgetFactory(self.options_factory)

        # -- Unregister processing
        QgsApplication.processingRegistry().removeProvider(self.provider)

        # remove actions
        del self.action_settings
        del self.action_help

    def run(self):
        """Main process.

        :raises Exception: if there is no item in the feed
        """
        try:
            self.log(
                message=self.tr(
                    text="Everything ran OK.",
                    context="VectilerPlugin",
                ),
                log_level=3,
                push=False,
            )
        except Exception as err:
            self.log(
                message=self.tr(
                    text="Houston, we've got a problem: {}".format(err),
                    context="VectilerPlugin",
                ),
                log_level=2,
                push=True,
            )
