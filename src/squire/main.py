import os

from squire.hdf5store import (
    add_file_to_hdf_store,
    add_to_merged_dataset,
    create_merged_dataset,
    generate_coordinate_index,
)
from squire.io import (
    export_cpg_list,
    export_reference_matrix,
    make_viable_path,
    read_file_of_files,
    validate_bedmethyl,
    validate_hdf5,
)
from squire.reports import pvalue_threshold_report
from squire.squire_exceptions import SquireError
from squire.stats import compute_p_values
from squire.types import CpGListArgs, CreateArgs, ReferenceArgs, ReportArgs


def add_bedmethyl_list_to_hdf_data(args: CreateArgs) -> None:
    """Adds bedmethyl files to a hdf5 file"""
    file_list = (
        read_file_of_files(args.file)
        if args.file is not None
        else args.bedmethyl_list
    )
    assert file_list is not None

    for bedmethyl in file_list:
        validate_bedmethyl(bedmethyl)
        add_file_to_hdf_store(bedmethyl, args.hdf5)


def create_hdf(args: CreateArgs) -> None:
    """Intialise hdf5 file for other commands to read from

    Uses a list of bedmethyl files (list can be generated from a file of files)
    to create a hdf5 file that contains the following information:
      - A merged pandas dataframe of each input bedmethyl file, keeping the
        columns:
          - chromosome
          - start
          - end
          - name(m/h)
          - read depth
          - number of modifications
          - raction of reads with modifications
      - A pandas dataframe containing the p-values for each position,
        describing how different the underlying distributions of each cell
        type is for that genomic locus.

    Timing
    ---
    With 2 9GB files, this takes ~40 minutes to add and merge the files and
    another hour to compute all of the p-values (~2.5 million).
        - File reading and merging is single threaded and so should be mainly
          dependent on the number and size of the files being used.
        - pvalue calculations are processed in parallel. This timing was taken
          from a 'Intel(R) Xeon(R) CPU E5-2640 v3 @ 2.60GHz' processor
    """
    try:
        make_viable_path(args.hdf5, args.overwrite)
        if args.overwrite and os.path.exists(args.hdf5):
            os.remove(args.hdf5)
        add_bedmethyl_list_to_hdf_data(args)
        generate_coordinate_index(args.hdf5)
        create_merged_dataset(args.hdf5)
        compute_p_values(args.hdf5)

    except (PermissionError, FileExistsError) as e:
        raise SquireError(f"SQUIRE failed to create {args.hdf5}.") from e


def add_to_hdf(args: CreateArgs) -> None:
    """Add to the hdf5 file and recalculate statistics"""
    try:
        validate_hdf5(args.hdf5)
        add_bedmethyl_list_to_hdf_data(args)
        add_to_merged_dataset(args.hdf5)
        compute_p_values(args.hdf5)
    except (PermissionError, FileExistsError) as e:
        raise SquireError(f"SQUIRE failed to update {args.hdf5}") from e


def write_reference_matrix(args: ReferenceArgs) -> None:
    """Write a reference matrix (for HyLoRD) using a hdf5 file

    This is a wrapper for the `export_reference_matrix` function, it tests
    file viability before writing to the given path
    """
    try:
        validate_hdf5(args.hdf5)
        make_viable_path(args.out_path, args.overwrite)
        export_reference_matrix(args.hdf5, args.out_path)
    except (PermissionError, FileExistsError) as e:
        raise SquireError(f"SQUIRE failed to write to {args.out_path}") from e


def write_cpg_list(args: CpGListArgs) -> None:
    """Write a CpG list (for HyLoRD) using a hdf5 file

    This is a wrapper for the `export_cpg_list` function, it tests file
    viability before writing to the given path
    """
    try:
        validate_hdf5(args.hdf5)
        make_viable_path(args.out_path, args.overwrite)
        export_cpg_list(args.hdf5, args.out_path, args.threshold)
    except (PermissionError, FileExistsError) as e:
        raise SquireError(f"SQUIRE failed to write to {args.out_path}") from e


def print_threshold_analysis(args: ReportArgs) -> None:
    """Generate a report for p-value threshold analysis

    This is a wrapper for the pvalue_threshold_report function, it tests for
    hdf5 file viability before running the function
    """
    try:
        validate_hdf5(args.hdf5)
        pvalue_threshold_report(
            args.hdf5, args.thresholds, args.machine_parsable
        )
    except (PermissionError, FileExistsError) as e:
        raise SquireError("SQUIRE failed to report threshold analysis") from e
