import yaml

import scripts.sync_sheets as sync


def test_new_calendar_sheet_link_is_configured():
    cfg = sync.load_config(sync.CONFIG_PATH)

    assert cfg["sheet_id"] == "1X9aMGn-l1KgrUDdIQ785psvy02tTyXfohgm9ydY9FGM"
    assert cfg["datasets"]["ai_ml_research_fellowships"] == {
        "gid": 1934629732,
        "output": "ai_ml_research_fellowships.ics",
        "csv": "ai_ml_research_fellowships.csv",
    }
    assert sync.build_export_url(
        cfg["sheet_id"], cfg["datasets"]["ai_ml_research_fellowships"]["gid"]
    ) == (
        "https://docs.google.com/spreadsheets/d/"
        "1X9aMGn-l1KgrUDdIQ785psvy02tTyXfohgm9ydY9FGM/"
        "export?format=csv&gid=1934629732"
    )


def test_sync_download_and_save(tmp_path, monkeypatch):
    # Arrange: point DATA_DIR to a temp folder and create a small config
    monkeypatch.setattr(sync, "DATA_DIR", tmp_path)
    cfg = {"sheet_id": "SHEETID", "datasets": {"demo": {"gid": 123, "csv": "demo.csv"}}}
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg))

    class Resp:
        def __init__(self, text):
            self.text = text

        def raise_for_status(self):
            return None

    def mock_get(url, timeout=30):
        assert "export?format=csv" in url
        return Resp("a,b\n1,2\n")

    monkeypatch.setattr(sync.requests, "get", mock_get)

    # Act
    sync.sync_all(config_path=cfg_path)

    # Assert
    assert (tmp_path / "demo.csv").exists()


def test_sync_http_error_is_reported(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sync, "DATA_DIR", tmp_path)
    cfg = {"sheet_id": "SHEETID", "datasets": {"demo": {"gid": 123, "csv": "demo.csv"}}}
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg))

    class ErrResp:
        def raise_for_status(self):
            raise sync.requests.exceptions.HTTPError("unauthorized")

    monkeypatch.setattr(sync.requests, "get", lambda url, timeout=30: ErrResp())

    sync.sync_all(config_path=cfg_path)
    captured = capsys.readouterr()
    assert "Network error downloading" in captured.out
