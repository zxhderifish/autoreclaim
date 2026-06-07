from autoreclaim.config import data_dir


def test_data_dir_prefers_env(monkeypatch, tmp_path):
    monkeypatch.setenv("AUTORECLAIM_DATA_DIR", str(tmp_path))
    assert data_dir() == tmp_path
