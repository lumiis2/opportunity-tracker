<p align="center">
  <img src="banner.png" alt="Opportunity Tracker Banner" width="100%">
</p>

---

Opportunity Tracker is an open-source project designed to help students organize, monitor, and plan applications for academic and professional opportunities throughout their careers.

The platform aims to centralize and track:

* Research internships
* Scholarships
* Academic exchange programs
* Summer schools
* Conferences
* Master's programs
* PhD opportunities
* Industry internships

While the project is primarily focused on Computer Science, AI, and research-oriented careers, its structure is flexible enough to support virtually any academic field.

---

## Why?

Finding high-quality opportunities is often harder than it should be.

Many scholarship databases, internship websites, and opportunity aggregators are cluttered with advertisements, affiliate links, sponsored content, or paid services. Others are incomplete, outdated, or heavily biased toward specific institutions and programs.

As a result, students frequently:

* Discover opportunities too late
* Miss application deadlines
* Lose track of recurring annual programs
* Spend countless hours manually searching websites
* Repeatedly research the same opportunities every year

For students interested in research, international experiences, and graduate studies, manually tracking dozens of programs quickly becomes exhausting.

Opportunity Tracker was created to solve this problem by transforming curated opportunity databases into actionable calendars, reminders, and eventually automated monitoring systems.

Instead of constantly searching for opportunities, students can focus on preparing stronger applications.

---

## Open Source First

Opportunity Tracker is built as a community-driven open-source project.

The goal is not only to create a tool, but also to build a shared database of opportunities that anyone can benefit from.

Everyone is encouraged to contribute:

* New opportunities
* Missing deadlines
* Updated application cycles
* Scholarship information
* Conference dates
* Graduate programs
* Corrections and improvements

The more people contribute, the more useful the platform becomes for students worldwide.

---

## Current Status

🚧 **Early Development (MVP)**

The first version intentionally focuses on solving a single problem well:

1. Maintain a structured database of opportunities.
2. Generate calendar events from that database.
3. Export calendars that can be imported into Google Calendar and other calendar applications.

Future versions will gradually add automation, monitoring, and recommendation features.

---

## Opportunity Categories

### Research

Examples:

* Mitacs Globalink Research Internship
* ETH SSRF
* Summer@EPFL
* DAAD RISE
* CERN Openlab
* Mila Research Internship

### Academic Exchange

Examples:

* Erasmus+
* AULP Mobility Program
* University exchange programs

### Scholarships

Examples:

* MEXT
* Fulbright
* DAAD Scholarships
* Chevening

### Industry

Examples:

* Google Research
* DeepMind
* Microsoft Research
* NVIDIA Research
* Meta AI
* Amazon Science

### Summer Schools

Examples:

* MLSS
* EEML
* Research schools and workshops

### Graduate Programs

Examples:

* MSc programs
* PhD programs
* Visiting graduate opportunities

### Conferences

Examples:

* NeurIPS
* ICML
* ICLR
* CVPR
* ACL
* ISMIR

---

## How It Works

The project is centered around curated datasets.

```text
data/
├── graduation_opportunities.csv
├── masters_programs.csv
├── conferences.csv
```

These datasets act as the single source of truth.

The application transforms them into calendars, reminders, and future recommendation systems.

```text
Opportunity Database
        ↓
Calendar Generator
        ↓
ICS Calendar
        ↓
Google Calendar
```

For opportunities with confirmed deadlines:

```text
ETH SSRF Deadline
December 15, 2026
```

For opportunities without confirmed dates:

```text
Check Mitacs

Expected application cycle:
September

Verify official dates
```

---

## MVP Roadmap

### Phase 1 — Calendar Generation

* Structured opportunity database
* CSV support
* Calendar generation
* ICS export
* Google Calendar integration

### Phase 2 — Smart Reminders

* Deadline reminders
* Estimated deadline tracking
* Automatic "check opportunity" events
* Recurring cycle monitoring

### Phase 3 — Dashboard

* Web dashboard
* Search and filtering
* Opportunity categorization
* Status tracking

### Phase 4 — Automated Monitoring

* Website monitoring
* Deadline change detection
* Opportunity updates
* Automated notifications

### Phase 5 — Intelligent Recommendations

* AI-assisted opportunity discovery
* Personalized ranking
* Career-stage planning
* Application strategy recommendations

---

## Long-Term Vision

Opportunity Tracker aims to become a centralized platform for discovering, tracking, and planning academic opportunities worldwide.

The goal is to help students move from a reactive process:

```text
Find opportunity
↓
Realize deadline is next week
↓
Rush application
```

to a proactive one:

```text
Track opportunity
↓
Plan ahead
↓
Prepare application
↓
Apply strategically
```

Ultimately, the project aims to become a personal opportunity management system for students, researchers, and early-career professionals.

---

## Project Structure

```text
opportunity-tracker/

├── data/
│   └── graduation_opportunities.csv
│
├── src/
│   ├── models.py
│   ├── parser.py
│   ├── calendar_generator.py
│   └── cli.py
│
├── output/
│
├── pyproject.toml
│
└── README.md
```

---

## Setup

Install dependencies:

```bash
uv sync
```

---

## Usage

Generate a calendar from your opportunity database:

```bash
uv run opportunity-calendar generate
```

Output:

```text
output/graduation.ics
```

The generated calendar can be imported into Google Calendar, Apple Calendar, Outlook, and other calendar applications.

---

## Contributing

Contributions, suggestions, opportunity submissions, and feedback are welcome.

Whether you want to add a scholarship, update a deadline, report outdated information, improve the codebase, or suggest new features, your contribution helps make the platform more useful for students everywhere.

---

## License

MIT License
