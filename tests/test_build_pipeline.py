from pathlib import Path
import shutil

import scripts.build as build


def test_build_pipeline_generates_ics(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[1]

    # Copy the current CSV inputs into a temporary workspace.
    (tmp_path / "data").mkdir(parents=True, exist_ok=True)
    for name in ["graduation.csv", "masters.csv", "industry.csv", "conferences.csv"]:
        shutil.copy(root / "data" / name, tmp_path / "data" / name)

    monkeypatch.setattr(build, "ROOT_DIR", tmp_path)

    code = build.main()
    assert code == 0

    for name in ["graduation.ics", "masters.ics", "industry.ics", "conferences.ics"]:
        out = tmp_path / "output" / name
        assert out.exists()
        text = out.read_text(encoding="utf-8")
        assert "BEGIN:VCALENDAR" in text
        assert "BEGIN:VEVENT" in text
