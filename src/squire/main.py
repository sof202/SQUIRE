from pathlib import Path

from squire.hdf5store import (
    add_file_to_hdf_store,
    create_merged_dataset,
    generate_coordinate_index,
)
from squire.io import (
    export_cpg_list,
    is_viable_bedmethyl,
    is_viable_hdf5,
    make_viable_path,
    read_file_of_files,
    export_reference_matrix,
)
from squire.reports import pvalue_threshold_report
from squire.squire_exceptions import BedMethylReadError, HDFReadError, SquireError
from squire.stats import compute_p_values


def create_hdf(args):
    hdf5_path = Path(args.hdf5)
    try:
        make_viable_path(hdf5_path, args.overwrite)
        if args.file is not None:
            file_list = read_file_of_files(args.file)
        else:
            file_list = args.bedmethyl_list
        for bedmethyl in file_list:
            bedmethyl = Path(bedmethyl)
            if not is_viable_bedmethyl(bedmethyl):
                raise BedMethylReadError(f"{bedmethyl} is not a viable bedmethyl file")
            add_file_to_hdf_store(bedmethyl, hdf5_path)
        generate_coordinate_index(hdf5_path)
        create_merged_dataset(hdf5_path)
        compute_p_values(hdf5_path)

    except (PermissionError, FileExistsError) as e:
        raise SquireError(f"SQUIRE failed to create {hdf5_path}.") from e


def write_reference_matrix(args):
    hdf5_path = Path(args.hdf5)
    ref_path = Path(args.out_path)
    try:
        if not is_viable_hdf5(hdf5_path):
            raise HDFReadError(f"{hdf5_path} is not a viable hdf5 file")
        make_viable_path(ref_path, args.overwrite)
        export_reference_matrix(hdf5_path, ref_path)
    except (PermissionError, FileExistsError) as e:
        raise SquireError(f"SQUIRE failed to write to {ref_path}") from e


def write_cpg_list(args):
    hdf5_path = Path(args.hdf5)
    cpg_list_path = Path(args.out_path)
    try:
        if not is_viable_hdf5(hdf5_path):
            raise HDFReadError(f"{hdf5_path} is not a viable hdf5 file")
        make_viable_path(cpg_list_path, args.overwrite)
        export_cpg_list(hdf5_path, cpg_list_path, args.threshold)
    except (PermissionError, FileExistsError) as e:
        raise SquireError(f"SQUIRE failed to write to {cpg_list_path}") from e
        exit(1)


def print_threshold_analysis(args):
    hdf5_path = Path(args.hdf5)
    try:
        if not is_viable_hdf5(hdf5_path):
            raise HDFReadError(f"{hdf5_path} is not a viable hdf5 file")
        pvalue_threshold_report(hdf5_path, args.thresholds)
    except (PermissionError, FileExistsError) as e:
        raise SquireError("SQUIRE failed to report threshold analysis") from e
        exit(1)
