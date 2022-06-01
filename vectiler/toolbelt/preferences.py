#! python3  # noqa: E265

"""
    Plugin settings.
"""

# standard
from dataclasses import asdict, dataclass, fields

# PyQGIS
from qgis.core import QgsSettings

# package
import vectiler.toolbelt.log_handler as log_hdlr
from vectiler.__about__ import __title__, __version__

# ############################################################################
# ########## Classes ###############
# ##################################


@dataclass
class PlgSettingsStructure:
    """Plugin settings structure and defaults values."""

    # global
    debug_mode: bool = False
    version: str = __version__

    # network and authentication
    url_geotuileur: str = "https://qlf-portail-gpf-beta.ign.fr/"
    url_service_vt: str = "https://qlf-vt-gpf-beta.ign.fr/"
    url_auth: str = "https://iam-ign-qa-ext.cegedim.cloud/"
    auth_realm: str = "demo"
    auth_client_id: str = "guichet"
    qgis_auth_id: str = ""

    @property
    def url_authentication_token(self) -> str:
        """Return the URL to get the token from the authentication service."""
        return f"{self.url_auth}auth/realms/{self.auth_realm}/protocol/openid-connect/token"

    @property
    def url_authentication_redirect(self) -> str:
        """Return the URL to redirect to the authentication service."""
        return f"{self.url_auth}login/check"


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

        # instanciate new settings object
        options = PlgSettingsStructure(
            # normal
            settings.value(
                key=settings_fields[0].name,
                defaultValue=settings_fields[0].default,
                type=settings_fields[0].type,
            ),
            settings.value(
                key=settings_fields[1].name,
                defaultValue=settings_fields[1].default,
                type=settings_fields[1].type,
            ),
            # network and authentication
            settings.value(
                key=settings_fields[2].name,
                defaultValue=settings_fields[2].default,
                type=settings_fields[2].type,
            ),
            settings.value(
                key=settings_fields[3].name,
                defaultValue=settings_fields[3].default,
                type=settings_fields[3].type,
            ),
            settings.value(
                key=settings_fields[4].name,
                defaultValue=settings_fields[4].default,
                type=settings_fields[4].type,
            ),
            settings.value(
                key=settings_fields[5].name,
                defaultValue=settings_fields[5].default,
                type=settings_fields[5].type,
            ),
            settings.value(
                key=settings_fields[6].name,
                defaultValue=settings_fields[6].default,
                type=settings_fields[6].type,
            ),
            settings.value(
                key=settings_fields[7].name,
                defaultValue=settings_fields[7].default,
                type=settings_fields[7].type,
            ),
        )

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
