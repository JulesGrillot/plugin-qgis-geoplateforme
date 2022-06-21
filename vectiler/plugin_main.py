#! python3  # noqa: E265

"""
    Main plugin module.
"""
# PyQGIS
from qgis.core import QgsApplication
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QToolBar
from qgis.utils import showPluginHelp

# project
from vectiler.__about__ import DIR_PLUGIN_ROOT, __title__
from vectiler.gui.dlg_authentication import AuthenticationDialog
from vectiler.gui.dlg_settings import PlgOptionsFactory
from vectiler.gui.tile_creation.wzd_tile_creation import TileCreationWizard
from vectiler.gui.upload_creation.wzd_upload_creation import UploadCreationWizard
from vectiler.processing import VectilerProvider
from vectiler.toolbelt import PlgLogger, PlgTranslator


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

        self.options_factory = None
        self.action_help = None
        self.action_settings = None

        self.toolbar = None
        self.dlg_authentication = None

        self.action_authentication = None
        self.action_import = None
        self.action_tile_create = None

        self.btn_autentification = None
        self.btn_import = None
        self.btn_configuration = None

        self.import_wizard = None
        self.tile_creation_wizard = None

    def initGui(self):
        """Set up plugin UI elements."""

        # settings page within the QGIS preferences menu
        self.options_factory = PlgOptionsFactory()
        self.iface.registerOptionsWidgetFactory(self.options_factory)

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
        self.toolbar = QToolBar("Vectiler toolbar")
        self.iface.addToolBar(self.toolbar)

        # Login
        self.dlg_authentication = AuthenticationDialog(self.iface.mainWindow())
        self.action_authentication = QAction(
            QIcon(str(DIR_PLUGIN_ROOT / "resources" / "images" / "icons" / "User.svg")),
            self.tr("Login"),
            self.iface.mainWindow(),
        )
        self.action_authentication.triggered.connect(self.authentication)
        self.toolbar.addAction(self.action_authentication)

        # Import
        self.action_import = QAction(
            QIcon(
                str(DIR_PLUGIN_ROOT / "resources" / "images" / "icons" / "Deposer.png")
            ),
            self.tr("Create a new upload"),
            self.iface.mainWindow(),
        )
        self.action_import.triggered.connect(self.import_data)
        self.toolbar.addAction(self.action_import)

        # Tile creation
        self.action_tile_create = QAction(
            QIcon(
                str(DIR_PLUGIN_ROOT / "resources" / "images" / "icons" / "Tuile@1x.png")
            ),
            self.tr("Tile creation"),
            self.iface.mainWindow(),
        )
        self.action_tile_create.triggered.connect(self.tile_creation)
        self.toolbar.addAction(self.action_tile_create)

        # -- Processings
        self.initProcessing()

    def initProcessing(self):
        self.provider = VectilerProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        """Cleans up when plugin is disabled/uninstalled."""
        # -- Clean up menu
        self.iface.removePluginMenu(__title__, self.action_help)
        self.iface.removePluginMenu(__title__, self.action_settings)
        # remove toolbar :
        self.toolbar.deleteLater()
        # -- Clean up preferences panel in QGIS settings
        self.iface.unregisterOptionsWidgetFactory(self.options_factory)

        # -- Unregister processing
        QgsApplication.processingRegistry().removeProvider(self.provider)

        # remove actions
        del self.action_settings
        del self.action_help

    def tile_creation(self):
        """
        Open tile creation Wizard

        """
        if self.tile_creation_wizard is None:
            self.tile_creation_wizard = TileCreationWizard(self.iface.mainWindow())
        self.tile_creation_wizard.show()

    def import_data(self):
        """
        Open import data Wizard

        """
        if self.import_wizard is None:
            self.import_wizard = UploadCreationWizard(self.iface.mainWindow())
        self.import_wizard.show()

    def authentication(self):
        """
        Open authentification dialog

        """
        if self.dlg_authentication is not None:
            self.dlg_authentication.exec()

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
