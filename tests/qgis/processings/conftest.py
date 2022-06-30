import pytest
from qgis.core import QgsApplication, QgsProcessingFeedback

from geotuileur.processing import VectilerProvider


class QgsProcessingFeedBackTest(QgsProcessingFeedback):
    def __init__(self):
        """
        QgsProcessingFeedback to store calls from QgsProcessingAlgorithm

        """
        super().__init__()
        self.progressTexts = []
        self.warnings = []
        self.infos = []
        self.commandInfos = []
        self.debugInfos = []
        self.consoleInfos = []
        self.reportErrors = []

    def setProgressText(self, text: str):
        self.progressTexts.append(text)

    def pushWarning(self, warning: str):
        self.warnings.append(warning)

    def pushInfo(self, info: str):
        self.infos.append(info)

    def pushCommandInfo(self, info: str):
        self.commandInfos.append(info)

    def pushDebugInfo(self, info):
        self.debugInfos.append(info)

    def pushConsoleInfo(self, info: str):
        self.consoleInfos.append(info)

    def reportError(self, error: str, fatalError=False):
        self.reportErrors.append(error)


@pytest.fixture(autouse=True)
def add_provider(qgis_processing) -> VectilerProvider:
    """
    Add VectilerProvider to processing registry and remove it after use

    Args:
        qgis_processing: pytest-qgis fixture to initialize qgis processing
    """
    prov = VectilerProvider()
    QgsApplication.processingRegistry().addProvider(prov)
    yield prov
    QgsApplication.processingRegistry().removeProvider(prov)
