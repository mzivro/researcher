import os

import pytest

# Ensure settings module can load before any src imports in tests
os.environ.setdefault("OPENAI_API_KEY", "test-api-key-for-unit-tests")


@pytest.fixture
def tmp_log_dir(tmp_path, monkeypatch):
    """Run logger tests in an isolated directory."""
    monkeypatch.chdir(tmp_path)
    return tmp_path
