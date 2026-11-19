<p align="center">
  <img src="assets/banner.png" alt="Opportunity Tracker" width="100%">
</p>

<p align="center">
  <a href="https://lumiis2.github.io/opportunity-tracker/">Access calendars</a>
  ·
  <a href="https://github.com/lumiis2/opportunity-tracker/issues">Suggest or correct</a>
  ·
  <a href="tutorials-and-info/How-to-Contribute.md">Contribution guide</a>
  ·
  <a href="README-pt.md">Português</a>
</p>

---

## Team members (Integrantes)

- **Luisa**
- **Mateus Faria Zaparoli Monteiro**

## About the system (Sobre o sistema)

Incredible academic and professional opportunities exist by the thousands, but they are scattered across the internet — and many people only find them after the deadline has passed.

The **Opportunity Tracker** gathers opportunities for undergraduate, master's, conferences, and industry in easy-to-follow calendars. The proposal is straightforward: choose a category, add the link to your calendar application, and have the deadlines available where you already organize your routine.

This is both a public service and an open-source starter project. You can:

- use the calendars already published;
- fork the repository and publish calendars for your area or community;
- contribute data, documentation, tests, parsers, or frontend improvements.

## Start here

👉 **[Access the Opportunity Tracker page](https://lumiis2.github.io/opportunity-tracker/)**

The site displays live counts, upcoming opportunities, public subscription links, `.ics` downloads, and the source CSVs. Calendar cards are generated from the same normalized data used to build the calendar files.

## Available calendars

Copy the calendar URL and paste it into the **From URL** option in your calendar app.

> Clicking an `.ics` link may download the file. For a recurring subscription, copy the URL shown on the site and add it using your calendar application's **From URL** option.

| Category | Calendar URL — copy and paste | Download `.ics` | Download CSV |
| --- | --- | --- | --- |
| 🎓 Undergraduate | `https://lumiis2.github.io/opportunity-tracker/graduation.ics` | [graduation.ics](https://lumiis2.github.io/opportunity-tracker/graduation.ics) | [graduation.csv](https://lumiis2.github.io/opportunity-tracker/data/graduation.csv) |
| 🏫 Master's | `https://lumiis2.github.io/opportunity-tracker/masters.ics` | [masters.ics](https://lumiis2.github.io/opportunity-tracker/masters.ics) | [masters.csv](https://lumiis2.github.io/opportunity-tracker/data/masters.csv) |
| 💼 Industry | `https://lumiis2.github.io/opportunity-tracker/industry.ics` | [industry.ics](https://lumiis2.github.io/opportunity-tracker/industry.ics) | [industry.csv](https://lumiis2.github.io/opportunity-tracker/data/industry.csv) |
| 📚 Conferences | `https://lumiis2.github.io/opportunity-tracker/conferences.ics` | [conferences.ics](https://lumiis2.github.io/opportunity-tracker/conferences.ics) | [conferences.csv](https://lumiis2.github.io/opportunity-tracker/data/conferences.csv) |
| 🤖 AI/ML Research & Fellowships | `https://lumiis2.github.io/opportunity-tracker/ai_ml_research_fellowships.ics` | [ai_ml_research_fellowships.ics](https://lumiis2.github.io/opportunity-tracker/ai_ml_research_fellowships.ics) | [ai_ml_research_fellowships.csv](https://lumiis2.github.io/opportunity-tracker/data/ai_ml_research_fellowships.csv) |
| 🗂️ Personal calendar | `https://lumiis2.github.io/opportunity-tracker/personal.ics` | [personal.ics](https://lumiis2.github.io/opportunity-tracker/personal.ics) | [personal.csv](https://lumiis2.github.io/opportunity-tracker/data/personal.csv) |
| 🌐 All opportunities | `https://lumiis2.github.io/opportunity-tracker/all.ics` | [all.ics](https://lumiis2.github.io/opportunity-tracker/all.ics) | — |

## How to use

### 1. Subscribe via link — recommended

Copy the address of the `.ics` file of the desired category and add it via the **By URL** option in your calendar application.

When subscribing, the application checks the same address periodically. This way, updates published to the calendar can appear for those already using the link, without the need to manually download a new file.

### 2. Download the `.ics` file

Open one of the `.ics` links in the table and save the file to import it into Google Calendar, Apple Calendar, Outlook, or another compatible application.

> **Attention:** importing a downloaded file creates a one-time copy. To receive future updates, prefer subscribing via URL.

### 3. Download the data in CSV

Use the **Download CSV** column to query, filter, or edit the data of a category. These files also serve as a template for creating a personalized calendar.

### 4. Generate a personalized calendar locally

Clone the repository and install the dependencies:

```bash
git clone https://github.com/lumiis2/opportunity-tracker.git
cd opportunity-tracker
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy or download an official CSV, remove or edit the lines you wish, and run:

```bash
python -m src.cli generate-ics \
  --track graduation \
  --input opportunities.csv \
  --output my_calendar.ics
```


Accepted values for `--track`: `graduation`, `masters`, `industry`,
`conferences`, `ai_ml_research_fellowships`, and `personal`.

See the [personal calendar tutorial](tutorials-and-info/COMO-CRIAR-SEU-CALENDARIO.md)
to create your own spreadsheet and optionally publish an updateable URL.

After the dependencies are installed, calendar generation works locally and does not depend on Google Sheets, credentials, or GitHub Pages.
The CSV must maintain the same columns as the official file of the chosen category.
To use a different column format, you will need to implement a new parser.

## How the project works

```text
Google Sheets
    ↓ scripts/sync_sheets.py
CSV files in data/
    ↓ dataset parsers
Opportunity + Milestone models
    ↓ validation and build
ICS calendars + opportunities.json + calendars.json
    ↓ GitHub Actions
Static frontend on GitHub Pages
```

## Technologies (Tecnologias)

The repository intentionally uses a small stack:

- **Python** synchronizes CSVs, normalizes opportunities, validates data, and generates ICS/JSON files.
- **HTML, CSS, and JavaScript** render the static frontend without a framework.
- **GitHub Actions** runs tests on Linux, macOS and Windows for pushes and pull requests. The publication workflow builds and deploys the site on pushes to main, every Monday, or on demand.
- **GitHub Pages** is the canonical host for public calendar subscription URLs.
- **PyYAML and Requests** read the dataset configuration and download public CSV worksheets.
- **pytest** runs the Python tests. **pytest-cov and Coverage.py** measure coverage of the Python modules in `src` and `scripts`.
- **Playwright with pytest-playwright** runs browser end-to-end tests against a temporary site built from controlled CSV data.
- **Codecov** receives the XML coverage report from GitHub Actions.

The normalized JSON files also form a simple public data contract:

- [`calendars.json`](https://lumiis2.github.io/opportunity-tracker/calendars.json) describes the published calendars and counts.
- [`opportunities.json`](https://lumiis2.github.io/opportunity-tracker/opportunities.json) contains the normalized opportunities and milestones.

## AI use (Uso de IA)

Codex (OpenAI) was consulted to interpret the assignment requirements, plan test
scenarios, provide code examples for unit and end-to-end tests, and investigate
CI and deployment failures. The members reviewed the selected examples, ran the
tests, and made the commits. The group is responsible for the final code and
results.

## Run the complete project locally

Install the development dependencies and build the current data:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
python scripts/build.py
```

To preview the website:

```bash
mkdir -p public/data
cp output/*.ics output/*.json public/
cp data/*.csv public/data/
python -m http.server 8000 --directory public
```

Then open `http://localhost:8000`. Public subscription buttons will still point to the canonical GitHub Pages calendars.

## Running tests (Execução dos testes)

The CI uses **Python 3.11**. Run the following commands from the repository root.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Linux or macOS:

```bash
source .venv/bin/activate
```

Or in Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the development dependencies and run the unit tests:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests/unit -q
```

To run the complete Python suite, including the existing component and
integration tests:

```bash
python -m pytest tests -q
```

Measure Python line coverage and generate terminal, XML and HTML reports:

```bash
python -m pytest tests --cov --cov-report=term-missing --cov-report=xml --cov-report=html
```

Coverage includes the Python modules in `src` and `scripts`. The configured
minimum is **80%**; a result below that threshold fails the coverage command.
The generated reports are `coverage.xml` and `htmlcov/index.html`. This
measurement does not include JavaScript executed in the browser.

Install the browser test dependencies and Chromium, then run the e2e suite:

```bash
python -m pip install -r requirements-e2e.txt
python -m playwright install chromium
python -m pytest e2e -q --browser chromium
```

If the Linux browser installation reports missing system libraries:

```bash
python -m playwright install --with-deps chromium
```

To watch the browser:

```bash
python -m pytest e2e -v --browser chromium --headed
```

To stop on the first failure and save evidence:

```bash
python -m pytest e2e -x -v --browser chromium --tracing retain-on-failure --screenshot only-on-failure
```

The e2e fixtures create controlled CSV data in a temporary directory, run the
real build, and start and stop a local HTTP server automatically. They fix the
browser date and timezone for reproducible upcoming dates. Calendar-host
requests are redirected only during tests to the local build outputs; the e2e
suite does not check GitHub Pages availability.

The current unit directory defines **54 test functions**. Parameterization
produces additional executed cases. The e2e directory defines **five browser
tests**. GitHub Actions runs the suites on Linux, macOS and Windows. The
coverage workflow uploads its XML report to Codecov from the Linux job.

Latest verified CI runs, on 19 November 2026:
[Tests and coverage](https://github.com/lumiis2/opportunity-tracker/actions/runs/44594320839)
and [Browser end-to-end tests](https://github.com/lumiis2/opportunity-tracker/actions/runs/44594320642).

Both workflows completed successfully on Linux, macOS and Windows. On
19 November 2026, verification of commit `e7ce307` found **129 passing Python
cases** and **92.98% line coverage** (729 of 784 lines), above the required 80%.
These figures refer to that commit:
[coverage report](https://app.codecov.io/gh/lumiis2/opportunity-tracker/commit/e7ce30792ca817f3cf5253207fa97267a112a3b2) and [Codecov project](https://app.codecov.io/gh/lumiis2/opportunity-tracker).

## Create your own fork

The repository can be reused as a base for a personal, academic, or community calendar:

1. Fork and clone the repository.
2. Replace the spreadsheet settings in `config.yaml` with your public Google Sheets ID and worksheet GIDs.
3. Keep an existing CSV schema, or add a small parser for your own columns.
4. Update calendar names and descriptions.
5. Change `CALENDAR_BASE_URL` in `public/app.js` to your permanent public calendar host.
6. Enable GitHub Pages through GitHub Actions in the fork settings.
7. Run the workflow manually and verify the generated `.ics` and JSON files.

For the simplest personal setup, follow the [personal calendar tutorial](tutorials-and-info/COMO-CRIAR-SEU-CALENDARIO.md). Never commit private credentials: the current synchronization only requires publicly readable worksheets.

## Add to Google Calendar via URL

Perform the first subscription through Google Calendar in a computer browser:

1. Copy the `.ics` link of the desired category.
2. Open [Google Calendar](https://calendar.google.com/).
3. Next to **Other calendars**, click the **+** button.
4. Choose **From URL**.
5. Paste the link and click **Add calendar**.
6. The new calendar will appear under **Other calendars**.

Google Calendar controls the update frequency of external calendars. A newly added calendar or a recent change may take a few minutes — and, in some cases, a few hours — to appear.

## How to contribute

This project does not intend to be a single person's calendar. The more people who share knowledge, the more students will be able to discover and prepare for good opportunities.

You can contribute by:

- adding new opportunities;
- correcting dates or outdated information;
- improving descriptions and links;
- suggesting new categories;
- writing guides and tutorials;
- fixing bugs or improving the code;
- creating a fork for calendars of a specific area or community.

For a direct change, fork the project, create a branch, and open a [Pull Request](https://github.com/lumiis2/opportunity-tracker/pulls). For a suggestion, question, or specific correction, open an [Issue](https://github.com/lumiis2/opportunity-tracker/issues).

When editing a CSV, preserve its headers and the column format so that the calendar continues to be generated correctly.

Before opening a pull request, run:

```bash
pytest -q
python scripts/build.py
```

Keep changes small and descriptive. Generated CSV, ICS, and JSON updates should remain consistent with the source data and build output.

## Future vision

The calendars are just the first step. The long-term vision is to build a collaborative knowledge base about academic and professional opportunities.

In the future, each opportunity could have content explaining the program, who can participate, how the selection works, common documents, timelines, participant experiences, preparation tips, and useful links. The idea also includes space for recurring programs or those without a defined date yet.

<p align="center">
  <strong>Found an opportunity? Share it. See something wrong? Correct it.<br>
  This project gets better whenever someone decides to help.</strong>
</p>

## License

Distributed under the [MIT license](LICENSE).
