import pytest_httpserver

from geoplateforme.processing.user_key.create_accesses import CreateAccessesAlgorithm
from tests.qgis.processings.conftest import run_alg


def test_accesses_creation(
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
        f"/api/users/me/keys/{key_id}/accesses", method="POST"
    ).respond_with_data(status=204)

    params = {
        CreateAccessesAlgorithm.KEY_ID: key_id,
        CreateAccessesAlgorithm.PERMISSION_ID: "permission_id",
        CreateAccessesAlgorithm.OFFERING_IDS: "offering_id_1,offering_id_2",
    }
    _, success = run_alg(CreateAccessesAlgorithm().name(), params)
    assert success
