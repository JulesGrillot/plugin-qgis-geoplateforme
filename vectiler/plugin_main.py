#! python3  # noqa: E265

"""
    Main plugin module.
"""

# PyQGIS
from qgis.core import QgsApplication
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction,QPushButton,QToolBar
from qgis.utils import showPluginHelp
from qgis.PyQt.QtGui import QIcon
# project
from vectiler.__about__ import __title__
from vectiler.gui.wzd_import import WzdImport
from vectiler.gui.dlg_settings import PlgOptionsFactory
from vectiler.processing import VectilerProvider
from vectiler.toolbelt import PlgLogger, PlgTranslator



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
        def import_data ():
            self.window = WzdImport()
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
        self.toolbar_import = QToolBar("import data")
        self.iface.addToolBar(self.toolbar_import)

        # -- Processing
        self.initProcessing()

        icon = QIcon(QgsApplication.iconPath("console/iconSearchEditorConsole.svg"))
        self.btn_import = QPushButton(icon, "import data")
        self.btn_import.clicked.connect(import_data)
        self.toolbar_import.addWidget(self.btn_import)
        self.window = WzdImport(self.iface.mainWindow())




    def initProcessing(self):
        self.provider = VectilerProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        """Cleans up when plugin is disabled/uninstalled."""
        # -- Clean up menu
        self.iface.removePluginMenu(__title__, self.action_help)
        self.iface.removePluginMenu(__title__, self.action_settings)
        # remove toolbar :
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
