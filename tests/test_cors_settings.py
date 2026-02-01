
import importlib
import os
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from app import core, main


@pytest.fixture
def app_with_cors_settings():
    """
    Fixture that allows running a test with specific CORS settings,
    and ensures the app is restored to original state afterwards.
    """
    # We keep track of the cleanups we need to do
    cleanups = []

    def _get_app(cors_origins_json):
        # 1. Patch environment
        patcher = mock.patch.dict(os.environ, {"BACKEND_CORS_ORIGINS": cors_origins_json})
        patcher.start()

        # 2. Reload modules to pick up new env
        importlib.reload(core.config)
        importlib.reload(main)

        # Define cleanup for this specific setup
        def cleanup():
            patcher.stop()
            # Reload again to restore modules to original env state
            importlib.reload(core.config)
            importlib.reload(main)

        cleanups.append(cleanup)
        return main.app

    yield _get_app

    # Execute all cleanups (LIFO)
    for cleanup in reversed(cleanups):
        cleanup()

def test_cors_enabled(app_with_cors_settings):
    """Test that CORS headers are present when origin is allowed."""
    app = app_with_cors_settings('["http://localhost:8000"]')
    client = TestClient(app)

    response = client.options(
        "/api/v1/openapi.json",
        headers={
            "Origin": "http://localhost:8000",
            "Access-Control-Request-Method": "GET",
        }
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:8000"

def test_cors_disabled_for_disallowed_origin(app_with_cors_settings):
    """Test that CORS headers are missing for disallowed origin."""
    app = app_with_cors_settings('["http://localhost:8000"]')
    client = TestClient(app)

    response = client.options(
        "/api/v1/openapi.json",
        headers={
            "Origin": "http://evil.com",
            "Access-Control-Request-Method": "GET",
        }
    )
    assert "access-control-allow-origin" not in response.headers

def test_cors_no_config(app_with_cors_settings):
    """Test behavior when no CORS origins are configured (default behavior test)."""
    # This effectively tests the empty list case since we pass '[]'
    app = app_with_cors_settings('[]')
    client = TestClient(app)

    response = client.options(
        "/api/v1/openapi.json",
        headers={
            "Origin": "http://localhost:8000",
            "Access-Control-Request-Method": "GET",
        }
    )
    assert "access-control-allow-origin" not in response.headers
