from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, TypeAlias

from .domain.conference import Conference
from .domain.graduation_opportunity import GraduationOpportunity
from .domain.master_program import MasterProgram
from .parsers.conferences_parser import parse_conferences
from .parsers.graduation_parser import parse_graduation_opportunities
from .parsers.master_programs_parser import parse_master_programs

DomainRecord: TypeAlias = MasterProgram | GraduationOpportunity | Conference


@dataclass(frozen=True)
class DatasetConfig:
    csv_path: Path
    output_path: Path
    parser: Callable[[Path], list[DomainRecord]]


DATASET_REGISTRY: Dict[Path, Path] = {
    Path("data/graduation_opportunities.csv"): Path("public/graduation.ics"),
    Path("data/master_programs.csv"): Path("public/masters.ics"),
    Path("data/conferences.csv"): Path("public/conferences.ics"),
}

DATASET_CONFIGS: Dict[Path, DatasetConfig] = {
    Path("data/graduation_opportunities.csv"): DatasetConfig(
        csv_path=Path("data/graduation_opportunities.csv"),
        output_path=Path("public/graduation.ics"),
        parser=parse_graduation_opportunities,
    ),
    Path("data/master_programs.csv"): DatasetConfig(
        csv_path=Path("data/master_programs.csv"),
        output_path=Path("public/masters.ics"),
        parser=parse_master_programs,
    ),
    Path("data/conferences.csv"): DatasetConfig(
        csv_path=Path("data/conferences.csv"),
        output_path=Path("public/conferences.ics"),
        parser=parse_conferences,
    ),
}


def get_registry() -> Dict[Path, Path]:
    return dict(DATASET_REGISTRY)


def get_dataset_config(dataset_path: Path) -> DatasetConfig | None:
    return DATASET_CONFIGS.get(dataset_path)
