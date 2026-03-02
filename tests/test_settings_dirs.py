from email_mcp.settings import Settings


def test_settings_ensure_dirs(tmp_path):
    settings = Settings()
    settings.data_dir = tmp_path / "data"
    settings.cache_dir = tmp_path / "cache"
    settings.store_dir = tmp_path / "eml"
    settings.vector_dir = tmp_path / "vector"

    settings.ensure_dirs()

    assert settings.data_dir.exists()
    assert settings.cache_dir.exists()
    assert settings.store_dir.exists()
    assert settings.vector_dir.exists()


def test_settings_resolved_store_dir(tmp_path):
    settings = Settings()
    settings.data_dir = tmp_path / "data"
    assert settings.resolved_store_dir == settings.data_dir / "eml"
