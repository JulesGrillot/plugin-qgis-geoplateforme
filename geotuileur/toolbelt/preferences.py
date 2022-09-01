#! python3  # noqa: E265

"""
    Plugin settings.
"""

# standard
from dataclasses import asdict, dataclass, fields

# PyQGIS
from qgis.core import QgsApplication, QgsAuthMethodConfig, QgsSettings

# package
import geotuileur.toolbelt.log_handler as log_hdlr
from geotuileur.__about__ import __title__, __version__

# ############################################################################
# ########## Classes ###############
# ##################################

CFG_AUTH_NAME = "geotuileur_cfg"


@dataclass
class PlgSettingsStructure:
    """Plugin settings structure and defaults values."""

    # global
    debug_mode: bool = False
    version: str = __version__

    # network and authentication
    url_geotuileur: str = "https://portail-gpf-beta.ign.fr/"
    url_api_entrepot: str = "https://gpf-beta.ign.fr/geotuileur/"
    url_api_appendices: str = "https://gpf-beta.ign.fr/geotuileur/annexes/"
    url_service_vt: str = "https://vt-gpf-beta.ign.fr/"
    url_auth: str = "https://compte-gpf-beta.ign.fr/"
    auth_realm: str = "demo"
    auth_client_id: str = "geotuileur-qgis-plugin"
    qgis_auth_id: str = None

    # status check sleep (in seconds)
    status_check_sleep: int = 1

    @property
    def url_authentication_token(self) -> str:
        """Return the URL to get the token from the authentication service."""
        return f"{self.url_auth}auth/realms/{self.auth_realm}/protocol/openid-connect/token"

    @property
    def url_authentication_redirect(self) -> str:
        """Return the URL to redirect to the authentication service."""
        return f"{self.url_auth}login/check"

    @property
    def base_url_api_entrepot(self) -> str:
        """Return the URL for API entrepot"""
        return f"{self.url_api_entrepot}api/v1"

    @property
    def url_forgotten_password(self) -> str:
        """URL where an user can reset its credentials.

        :return: reset URL
        :rtype: str
        """
        return f"{self.url_auth}auth/realms/{self.auth_realm}/login-actions/reset-credentials?client_id={self.auth_client_id}"

    @property
    def url_sign_in(self) -> str:
        """URL where an user can register himself to create an account.

        :return: registration URL
        :rtype: str
        """
        # not working for now. See #95
        # return f"{self.url_auth}auth/realms/{self.auth_realm}/login-actions/authenticate?client_id={self.auth_client_id}"
        return f"{self.url_geotuileur}login"

    def create_auth_config(self, username: str, password: str) -> QgsAuthMethodConfig:
        """
        Create QgsAuthMethodConfig for OAuth2 authentification

        Args:
            username: (str) username
            password: (str) password

        Returns: QgsAuthMethodConfig (warning : config must be added to QgsApplication.authManager() before use

        """
        newAU = QgsAuthMethodConfig()

        newAU.setId(QgsApplication.authManager().uniqueConfigId())
        newAU.setName(CFG_AUTH_NAME)
        newAU.setMethod("OAuth2")

        # Create config map for oauth2config
        # Integer index match enum defined in QgsAuthOAuth2Config (not available in python binding)
        configured_map = {
            "accessMethod": 0,  # QgsAuthOAuth2Config.AccessMethod.Header
            "grantFlow": 2,  # QgsAuthOAuth2Config.GrantFlow.ResourceOwner
            "configType": 1,  # QgsAuthOAuth2Config.ConfigType.Custom
            "tokenUrl": self.url_authentication_token,
            "clientId": self.auth_client_id,
            "username": username,
            "password": password,
            "redirectPort": 7070,
            "persistToken": False,
            "requestTimeout": 30,
            "version": 1,
        }

        # We need to use a string for config_map
        config_str = str(configured_map)

        # ' not supported by pyqgis, replace by "
        config_str = config_str.replace("'", '"')

        # replace also boolean str
        config_str = config_str.replace("False", "false")
        config_str = config_str.replace("True", "true")

        config_map = {"oauth2config": config_str}
        newAU.setConfigMap(config_map)

        return newAU


class PlgOptionsManager:
    @staticmethod
    def get_plg_settings() -> PlgSettingsStructure:
        """Load and return plugin settings as a dictionary. \
        Useful to get user preferences across plugin logic.

        :return: plugin settings
        :rtype: PlgSettingsStructure
        """
        # get dataclass fields definition
        settings_fields = fields(PlgSettingsStructure)

        # retrieve settings from QGIS/Qt
        settings = QgsSettings()
        settings.beginGroup(__title__)

        # map settings values to preferences object
        li_settings_values = []
        for i in settings_fields:
            li_settings_values.append(
                settings.value(key=i.name, defaultValue=i.default, type=i.type)
            )

        # instanciate new settings object
        options = PlgSettingsStructure(*li_settings_values)

        settings.endGroup()

        return options

    @staticmethod
    def get_value_from_key(key: str, default=None, exp_type=None):
        """Load and return plugin settings as a dictionary. \
        Useful to get user preferences across plugin logic.

        :return: plugin settings value matching key
        """
        if not hasattr(PlgSettingsStructure, key):
            log_hdlr.PlgLogger.log(
                message="Bad settings key. Must be one of: {}".format(
                    ",".join(PlgSettingsStructure._fields)
                ),
                log_level=1,
            )
            return None

        settings = QgsSettings()
        settings.beginGroup(__title__)

        try:
            out_value = settings.value(key=key, defaultValue=default, type=exp_type)
        except Exception as err:
            log_hdlr.PlgLogger.log(
                message="Error occurred trying to get settings: {}.Trace: {}".format(
                    key, err
                )
            )
            out_value = None

        settings.endGroup()

        return out_value

    @classmethod
    def set_value_from_key(cls, key: str, value) -> bool:
        """Set plugin QSettings value using the key.

        :param key: QSettings key
        :type key: str
        :param value: value to set
        :type value: depending on the settings
        :return: operation status
        :rtype: bool
        """
        if not hasattr(PlgSettingsStructure, key):
            log_hdlr.PlgLogger.log(
                message="Bad settings key. Must be one of: {}".format(
                    ",".join(PlgSettingsStructure._fields)
                ),
                log_level=2,
            )
            return False

        settings = QgsSettings()
        settings.beginGroup(__title__)

        try:
            settings.setValue(key, value)
            out_value = True
        except Exception as err:
            log_hdlr.PlgLogger.log(
                message="Error occurred trying to set settings: {}.Trace: {}".format(
                    key, err
                )
            )
            out_value = False

        settings.endGroup()

        return out_value

    @classmethod
    def save_from_object(cls, plugin_settings_obj: PlgSettingsStructure):
        """Load and return plugin settings as a dictionary. \
        Useful to get user preferences across plugin logic.

        :return: plugin settings value matching key
        """
        settings = QgsSettings()
        settings.beginGroup(__title__)

        for k, v in asdict(plugin_settings_obj).items():
            cls.set_value_from_key(k, v)

        settings.endGroup()


if __name__ == "__main__":
    fi = fields(PlgSettingsStructure)
    print(fi)
