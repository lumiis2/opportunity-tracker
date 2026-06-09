from __future__ import annotations

import logging
from pathlib import Path

import typer

from .calendar_generator import build_calendar_report, save_calendar
from .parser import parse_opportunities

app = typer.Typer(help="Convert academic opportunity CSV files into ICS calendar files.")
logger = logging.getLogger("opportunity-calendar")


@app.callback(invoke_without_command=False)
def cli() -> None:
    """Opportunity calendar command group."""

    return None


@app.command()
def generate(
    input_path: Path = typer.Option(
        Path("data/graduation_opportunities.csv"),
        "--input",
        "-i",
        help="Path to the input CSV file.",
        exists=True,
        dir_okay=False,
        readable=True,
        resolve_path=False,
    ),
    output_path: Path = typer.Option(
        Path("output/graduation.ics"),
        "--output",
        "-o",
        help="Path to the output ICS file.",
        exists=False,
        dir_okay=False,
        writable=True,
        resolve_path=False,
    ),
) -> None:
    """Generate an ICS calendar from the input CSV file."""

    try:
        logger.info("Loading opportunities from %s", input_path)
        opportunities = parse_opportunities(input_path)
        logger.info("Loaded %s opportunities", len(opportunities))

        report = build_calendar_report(opportunities)
        logger.info("Created %s deadline events", report.deadline_events)
        logger.info("Created %s check events", report.check_events)

        generated_path = save_calendar(report.calendar, output_path)

        typer.echo(f"Loaded {len(opportunities)} opportunities")
        typer.echo(f"Created {report.deadline_events} deadline events")
        typer.echo(f"Created {report.check_events} check events")
        typer.echo("Saved:")
        typer.echo(str(generated_path))
    except FileNotFoundError as exc:
        logger.exception("Input file could not be found")
        typer.secho(f"Error: {exc}", err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1)
    except Exception as exc:  # pragma: no cover - safety net for CLI errors
        logger.exception("Unexpected error while generating the calendar")
        typer.secho(f"Error: {exc}", err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1)


def main() -> None:
    """Console script entry point."""

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    app()


if __name__ == "__main__":
    main()
