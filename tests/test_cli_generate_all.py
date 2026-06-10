from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.datasets import get_registry
from src.calendar_generator import process_all


class CLIGenerateAllTests(unittest.TestCase):
    def test_process_all_writes_outputs(self) -> None:
        registry = get_registry()

        # Use a temporary directory for outputs to avoid touching repo public/
        with tempfile.TemporaryDirectory() as td:
            tmpdir = Path(td)
            custom_registry = {}
            # create minimal CSV files for each registered input
            for csv_path, out_path in registry.items():
                src_csv = tmpdir / csv_path.name
                src_csv.write_text(csv_path.read_text() if csv_path.exists() else "")
                custom_out = tmpdir / out_path.name
                custom_registry[src_csv] = custom_out

            results = process_all(custom_registry)

            # ensure files were created and results recorded
            for out_path, stats in results.items():
                self.assertTrue(out_path.exists())
                self.assertIsInstance(stats, tuple)


if __name__ == "__main__":
    unittest.main()
