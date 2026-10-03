import pytest
from pydantic import ValidationError

from prepza_common.settings import ServiceSettings


def test_the_auth_emulator_is_allowed_only_for_a_demo_project():
    demo = ServiceSettings(
        firebase_project_id="demo-prepza", firebase_auth_emulator_host="auth:9199"
    )

    assert demo.firebase_auth_emulator_host == "auth:9199"
    assert ServiceSettings(firebase_project_id="prepza-prod").firebase_auth_emulator_host == ""

    with pytest.raises(ValidationError):
        ServiceSettings(firebase_project_id="prepza-prod", firebase_auth_emulator_host="auth:9199")
