"""Download Google Sheets worksheets and sync them into local CSV files.

Reads `config.yaml` at the repository root and downloads each configured
worksheet as CSV into the `data/` directory. Existing files are overwritten.

Usage:
	python scripts/sync_sheets.py

Logs concise progress to stdout.
"""

from pathlib import Path
import requests
import yaml


CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.yaml"
DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def load_config(path: Path) -> dict:
	if not path.exists():
		raise FileNotFoundError(f"Config not found: {path}")
	with path.open("r", encoding="utf-8") as fh:
		cfg = yaml.safe_load(fh)
	if not isinstance(cfg, dict) or "sheet_id" not in cfg or "datasets" not in cfg:
		raise ValueError("Invalid config: missing 'sheet_id' or 'datasets'")
	return cfg


def build_export_url(sheet_id: str, gid: int) -> str:
	return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


def download_csv(url: str, timeout: int = 30) -> str:
	resp = requests.get(url, timeout=timeout)
	resp.raise_for_status()
	return resp.text


def save_csv(text: str, dest: Path) -> None:
	dest.parent.mkdir(parents=True, exist_ok=True)
	with dest.open("w", encoding="utf-8", newline="") as fh:
		fh.write(text)


def sync_all(config_path: Path = CONFIG_PATH) -> None:
	cfg = load_config(config_path)
	sheet_id = cfg["sheet_id"]
	datasets = cfg.get("datasets", {})

	if not datasets:
		print("No datasets configured in config.yaml")
		return

	for name, meta in datasets.items():
		try:
			print(f"Downloading {name}...")
			gid = meta.get("gid")
			csv_name = meta.get("csv")
			if gid is None or not csv_name:
				print(f"Skipping {name}: invalid dataset entry (missing gid or csv)")
				continue

			url = build_export_url(sheet_id, gid)
			text = download_csv(url)
			if not text or not text.strip():
				print(f"Error: empty CSV for {name}")
				continue

			dest = DATA_DIR / csv_name
			save_csv(text, dest)
			print(f"Saved {dest}")

		except requests.exceptions.RequestException as exc:
			print(f"Network error downloading {name}: {exc}")
		except Exception as exc:  # defensive: invalid config, IO errors
			print(f"Error processing {name}: {exc}")

	print("Done.")


def main() -> int:
	try:
		sync_all()
		return 0
	except FileNotFoundError as exc:
		print(f"{exc}")
		return 2
	except ValueError as exc:
		print(f"{exc}")
		return 3


if __name__ == "__main__":
	raise SystemExit(main())

