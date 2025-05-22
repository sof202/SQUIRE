import argparse
from collections.abc import Callable, Generator
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import cast

import numpy as np
import numpy.typing as npt


# ------------------------
# ARGUMENT PARSING CLASSES
# ------------------------
@dataclass
class SharedArgs:
    """Arguments shared by all subcommands"""

    hdf5: Path
    overwrite: bool
    command: str


@dataclass
class CreateArgs(SharedArgs):
    """Arguments for the 'create' subcommand"""

    bedmethyl_list: list[Path] | None = None
    file: Path | None = None


@dataclass
class ReferenceArgs(SharedArgs):
    """Arguments for the 'reference' subcommand"""

    out_path: Path


@dataclass
class CpGListArgs(SharedArgs):
    """Arguments for the 'cpglist' subcommand"""

    out_path: Path
    threshold: float = 1e-10


@dataclass
class ReportArgs(SharedArgs):
    """Arguments for the 'report' subcommand"""

    thresholds: list[float] = field(
        default_factory=lambda: [1e-1, 1e-2, 1e-5, 1e-10, 1e-20]
    )


SquireArgs = CreateArgs | ReferenceArgs | CpGListArgs | ReportArgs


def convert_to_squire_args(args: argparse.Namespace) -> SquireArgs:
    """Convert argparse Namespace to the appropriate dataclass"""
    args_dict = vars(args)

    command_map = {
        "create": CreateArgs,
        "add": CreateArgs,
        "reference": ReferenceArgs,
        "cpglist": CpGListArgs,
        "report": ReportArgs,
    }

    dataclass_type = command_map[args.command]
    valid_fields = {f.name for f in fields(dataclass_type)}
    filtered_args = {k: v for k, v in args_dict.items() if k in valid_fields}

    return cast(SquireArgs, dataclass_type(**filtered_args))


# ------------------------
# STATISTICS TYPES
# ------------------------
GenomicLocus = tuple[
    tuple[str, np.uint32, np.uint32, str],
    npt.NDArray[np.int64],
    npt.NDArray[np.int64],
]
GenomicLociGenerator = Generator[
    list[GenomicLocus],
    None,
    None,
]

CountArray = npt.NDArray[np.int64]
PValue = npt.NDArray[np.float64] | float | int
StatsFunction = Callable[[CountArray, CountArray], PValue]
GenomicLocusWithPValue = tuple[str, np.uint32, np.uint32, str, PValue]
