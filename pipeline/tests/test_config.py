import pytest
from pathlib import Path


def test_config_loads_all_vars(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@h/db")
    monkeypatch.setenv("AUDIO_DIR", str(tmp_path))

    from config import load_config
    cfg = load_config()

    assert cfg["ANTHROPIC_API_KEY"] == "sk-ant-test"
    assert cfg["DATABASE_URL"] == "postgresql://u:p@h/db"
    assert cfg["AUDIO_DIR"] == tmp_path
    assert isinstance(cfg["AUDIO_DIR"], Path)


def test_config_raises_if_key_missing(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@h/db")
    monkeypatch.setenv("AUDIO_DIR", "/tmp")

    from config import load_config
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        load_config()


def test_config_raises_if_value_empty_string(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@h/db")
    monkeypatch.setenv("AUDIO_DIR", "/tmp")

    from config import load_config
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        load_config()


def test_config_raises_for_each_missing_var(monkeypatch):
    required = ["ANTHROPIC_API_KEY", "DATABASE_URL", "AUDIO_DIR"]
    all_vars = {
        "ANTHROPIC_API_KEY": "sk-ant-test",
        "DATABASE_URL": "postgresql://u:p@h/db",
        "AUDIO_DIR": "/tmp",
    }
    for missing_key in required:
        env = {k: v for k, v in all_vars.items() if k != missing_key}
        for k, v in env.items():
            monkeypatch.setenv(k, v)
        monkeypatch.delenv(missing_key, raising=False)

        from config import load_config
        with pytest.raises(RuntimeError, match=missing_key):
            load_config()

        # restore
        for k in env:
            monkeypatch.delenv(k, raising=False)
