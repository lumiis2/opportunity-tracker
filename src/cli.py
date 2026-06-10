from __future__ import annotations

import logging
from pathlib import Path

import typer

from .calendar_generator import build_calendar_report, save_calendar, process_all, process_dataset
from .datasets import get_registry
from .parser import parse_opportunities

app = typer.Typer(help="Convert academic opportunity CSV files into ICS calendar files.")
logger = logging.getLogger("opportunity-calendar")


@app.callback(invoke_without_command=False)
def cli() -> None:
    """Opportunity calendar command group."""

    return None


@app.command()
def generate(
    all: bool = typer.Option(
        True,
        "--all/--no-all",
        help="Generate calendars for all registered datasets (default: --all).",
    ),
    lead_months: int = typer.Option(
        1,
        "--lead-months",
        "-l",
        help="Number of months before an expected deadline to create a check reminder (default: 1).",
    ),
    input_path: Path = typer.Option(
        None,
        "--input",
        "-i",
        help="Path to a single input CSV file to process (overrides --all).",
        exists=False,
        dir_okay=False,
        readable=True,
        resolve_path=False,
    ),
    output_path: Path = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to a single output ICS file to write when using --input.",
        exists=False,
        dir_okay=False,
        writable=True,
        resolve_path=False,
    ),
) -> None:
    """Generate ICS calendars.

    By default (no flags) this generates calendars for every dataset in the
    dataset registry. Use `--no-all --input <csv> --output <ics>` to process a
    single file and preserve backward compatibility.
    """

    try:
        if input_path and output_path:
            # single-file mode
            logger.info("Processing single dataset %s", input_path)
            loaded, dl, ch = process_dataset(input_path, output_path, lead_months=lead_months)
            typer.echo(f"Loaded {loaded} opportunities")
            typer.echo(f"Generated {output_path.name}")
            return

        # default: process all registered datasets
        registry = get_registry()
        results = process_all(registry, lead_months=lead_months)

        total_loaded = sum(loaded for (loaded, _, _) in results.values())
        typer.echo(f"Loaded {total_loaded} opportunities")

        for output_path, stats in results.items():
            typer.echo(f"Generated {output_path.name}")

    except Exception as exc:  # pragma: no cover - safety net for CLI errors
        logger.exception("Unexpected error while generating the calendar(s)")
        typer.secho(f"Error: {exc}", err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1)


def main() -> None:
    """Console script entry point."""

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    app()


if __name__ == "__main__":
    main()
