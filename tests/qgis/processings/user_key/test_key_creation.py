import pytest_httpserver

from geoplateforme.processing.user_key.create_basic_key import CreateBasicKeyAlgorithm
from tests.qgis.processings.conftest import run_alg


def test_basic_key_creation(
    data_geopf_srv: pytest_httpserver.HTTPServer,
):
    """
    Check no error is raised when server return valid return code

    Args:
        data_geopf_srv: pytest fixture to simulate server and mock plugin settings
    """

    created_key_id = "key_id"

    # Respond valid return code
    data_geopf_srv.expect_oneshot_request(
        "/api/users/me/keys", method="POST"
    ).respond_with_json(
        {
            "name": "name",
            "type": "BASIC",
            "_id": created_key_id,
        }
    )

    params = {
        CreateBasicKeyAlgorithm.NAME: "name",
        CreateBasicKeyAlgorithm.LOGIN: "login",
        CreateBasicKeyAlgorithm.PASSWORD: "password",
    }
    result, success = run_alg(CreateBasicKeyAlgorithm().name(), params)
    assert success
    assert result[CreateBasicKeyAlgorithm.CREATED_KEY_ID] == created_key_id
