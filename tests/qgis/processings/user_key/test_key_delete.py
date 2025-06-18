import pytest_httpserver

from geoplateforme.processing.user_key.delete_key import DeleteUserKeyAlgorithm
from tests.qgis.processings.conftest import run_alg


def test_key_delete(
    data_geopf_srv: pytest_httpserver.HTTPServer,
):
    """
    Check no error is raised when server return valid return code

    Args:
        data_geopf_srv: pytest fixture to simulate server and mock plugin settings
    """
    key_id = "key_id"
    # Respond valid return code
    data_geopf_srv.expect_oneshot_request(
        f"/api/users/me/keys/{key_id}", method="DELETE"
    ).respond_with_data(status=202)

    params = {
        DeleteUserKeyAlgorithm.KEY_ID: key_id,
    }
    _, success = run_alg(DeleteUserKeyAlgorithm().name(), params)
    assert success
