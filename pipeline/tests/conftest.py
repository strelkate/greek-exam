import pytest


@pytest.fixture(autouse=True)
def set_required_env(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/test")
    monkeypatch.setenv("AUDIO_DIR", "/tmp/test_audio")
