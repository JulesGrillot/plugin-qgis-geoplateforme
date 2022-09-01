#! python3  # noqa E265

"""
    Usage from the repo root folder:

    .. code-block:: bash

        # for whole tests
        python -m unittest tests.qgis.test_plg_preferences
        # for specific test
        python -m unittest tests.qgis.test_plg_preferences.TestPlgPreferences.test_plg_preferences_structure
"""

# standard library
from qgis.testing import unittest

# project
from geotuileur.__about__ import __version__
from geotuileur.toolbelt.preferences import PlgSettingsStructure

# ############################################################################
# ########## Classes #############
# ################################


class TestPlgPreferences(unittest.TestCase):
    def test_plg_preferences_structure(self):
        """Test settings types and default values."""
        settings = PlgSettingsStructure()

        # global
        self.assertTrue(hasattr(settings, "debug_mode"))
        self.assertIsInstance(settings.debug_mode, bool)
        self.assertEqual(settings.debug_mode, False)

        self.assertTrue(hasattr(settings, "version"))
        self.assertIsInstance(settings.version, str)
        self.assertEqual(settings.version, __version__)

        # network and authentication
        self.assertTrue(hasattr(settings, "url_geotuileur"))
        self.assertIsInstance(settings.url_geotuileur, str)
        self.assertEqual(settings.url_geotuileur, "https://portail-gpf-beta.ign.fr/")

        self.assertTrue(hasattr(settings, "url_api_entrepot"))
        self.assertIsInstance(settings.url_api_entrepot, str)
        self.assertEqual(
            settings.url_api_entrepot, "https://gpf-beta.ign.fr/geotuileur/"
        )

        self.assertTrue(hasattr(settings, "url_api_appendices"))
        self.assertIsInstance(settings.url_api_appendices, str)
        self.assertEqual(
            settings.url_api_appendices, "https://gpf-beta.ign.fr/geotuileur/annexes/"
        )

        self.assertTrue(hasattr(settings, "url_service_vt"))
        self.assertIsInstance(settings.url_service_vt, str)
        self.assertEqual(settings.url_service_vt, "https://vt-gpf-beta.ign.fr/")

        self.assertTrue(hasattr(settings, "url_auth"))
        self.assertIsInstance(settings.url_auth, str)
        self.assertEqual(settings.url_auth, "https://compte-gpf-beta.ign.fr/")

        self.assertTrue(hasattr(settings, "auth_realm"))
        self.assertIsInstance(settings.auth_realm, str)
        self.assertEqual(settings.auth_realm, "demo")

        self.assertTrue(hasattr(settings, "auth_client_id"))
        self.assertIsInstance(settings.auth_client_id, str)
        self.assertEqual(settings.auth_client_id, "geotuileur-qgis-plugin")

        self.assertTrue(hasattr(settings, "qgis_auth_id"))
        self.assertIsInstance(settings.qgis_auth_id, str)
        self.assertEqual(settings.qgis_auth_id, None)


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
