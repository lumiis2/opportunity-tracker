"""Build and serve an isolated copy of the application for browser tests."""

import csv
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
from threading import Thread

import pytest
from playwright.sync_api import expect

from scripts import build


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_BASE_URL = "https://lumiis2.github.io/opportunity-tracker/"

PROGRAMS = [
    {"Program": "Past Program", "Application Deadline": "2026-12-15"},
    {"Program": "Late Program", "Application Deadline": "2027-03-10"},
    {"Program": "Early Program", "Application Deadline": "2027-01-20"},
    {"Program": "Estimated Program", "Expected Deadline Month": "February 2027"},
]


@pytest.fixture(scope="session")
def site_url(tmp_path_factory):
    workspace = tmp_path_factory.mktemp("published-site")
    shutil.copy(ROOT / "config.yaml", workspace / "config.yaml")
    data_dir = workspace / "data"
    data_dir.mkdir()

    # Keep real CSV schemas and use controlled rows for predictable assertions.
    for source in (ROOT / "data").glob("*.csv"):
        with source.open(encoding="utf-8-sig", newline="") as file:
            columns = next(csv.reader(file))
        with (data_dir / source.name).open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            if source.name == "graduation.csv":
                writer.writerows(PROGRAMS)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(build, "ROOT_DIR", workspace)
        assert build.main() == 0

    public_dir = workspace / "public"
    shutil.copytree(
        ROOT / "public",
        public_dir,
        ignore=shutil.ignore_patterns("*.ics", "*.json", "data"),
    )
    for artifact in (workspace / "output").iterdir():
        shutil.copy(artifact, public_dir / artifact.name)
    shutil.copytree(data_dir, public_dir / "data")

    handler = partial(SimpleHTTPRequestHandler, directory=str(public_dir))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "timezone_id": "UTC",
        "locale": "en-US",
    }


@pytest.fixture
def app_page(page, site_url):
    # Only the calendar host is redirected; files come from the real build.
    def redirect_calendar(route):
        relative_path = route.request.url.removeprefix(PUBLIC_BASE_URL)
        route.fulfill(
            status=302,
            headers={"location": f"{site_url}/{relative_path}"},
        )

    page.route(f"{PUBLIC_BASE_URL}**", redirect_calendar)
    page.clock.set_fixed_time(datetime(2027, 1, 1, 12, tzinfo=timezone.utc))
    page.goto(site_url)
    expect(page.locator("#calendar-list")).to_have_attribute("aria-busy", "false")
    return page
