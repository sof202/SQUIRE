from pathlib import Path

from squire.hdf5store import (
    add_file_to_hdf_store,
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


def create_hdf(args):
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
    """
    hdf5_path = Path(args.hdf5)
    try:
        make_viable_path(hdf5_path, args.overwrite)
        if args.file is not None:
            file_list = read_file_of_files(args.file)
        else:
            file_list = args.bedmethyl_list
        for bedmethyl in file_list:
            bedmethyl = Path(bedmethyl)
            validate_bedmethyl(bedmethyl)
            add_file_to_hdf_store(bedmethyl, hdf5_path)

        generate_coordinate_index(hdf5_path)
        create_merged_dataset(hdf5_path)
        compute_p_values(hdf5_path)

    except (PermissionError, FileExistsError) as e:
        raise SquireError(f"SQUIRE failed to create {hdf5_path}.") from e


def write_reference_matrix(args):
    """Write a reference matrix (for HyLoRD) using a hdf5 file

    This is a wrapper for the `export_reference_matrix` function, it tests
    file viability before writing to the given path
    """
    hdf5_path = Path(args.hdf5)
    ref_path = Path(args.out_path)
    try:
        validate_hdf5(hdf5_path)
        make_viable_path(ref_path, args.overwrite)
        export_reference_matrix(hdf5_path, ref_path)
    except (PermissionError, FileExistsError) as e:
        raise SquireError(f"SQUIRE failed to write to {ref_path}") from e


def write_cpg_list(args):
    """Write a CpG list (for HyLoRD) using a hdf5 file

    This is a wrapper for the `export_cpg_list` function, it tests file
    viability before writing to the given path
    """
    hdf5_path = Path(args.hdf5)
    cpg_list_path = Path(args.out_path)
    try:
        validate_hdf5(hdf5_path)
        make_viable_path(cpg_list_path, args.overwrite)
        export_cpg_list(hdf5_path, cpg_list_path, args.threshold)
    except (PermissionError, FileExistsError) as e:
        raise SquireError(f"SQUIRE failed to write to {cpg_list_path}") from e


def print_threshold_analysis(args):
    """Generate a report for p-value threshold analysis

    This is a wrapper for the pvalue_threshold_report function, it tests for
    hdf5 file viability before running the function
    """
    hdf5_path = Path(args.hdf5)
    try:
        validate_hdf5(hdf5_path)
        pvalue_threshold_report(hdf5_path, args.thresholds)
    except (PermissionError, FileExistsError) as e:
        raise SquireError("SQUIRE failed to report threshold analysis") from e
