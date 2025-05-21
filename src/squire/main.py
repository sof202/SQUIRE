from pathlib import Path
from sys import stderr

from squire.hdf5store import (
    add_file_to_hdf_store,
    create_merged_dataset,
    generate_coordinate_index,
)
from squire.io import make_viable_path, read_file_of_files
from squire.outputs import export_reference_matrix
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
            add_file_to_hdf_store(bedmethyl, hdf5_path)
        generate_coordinate_index(hdf5_path)
        create_merged_dataset(hdf5_path)
        compute_p_values(hdf5_path)

    except (PermissionError, FileExistsError):
        print(f"SQUIRE failed to create {hdf5_path}. Exiting...", file=stderr)
        exit(1)


def write_reference_matrix(args):
    hdf5_path = Path(args.hdf5)
    ref_path = Path(args.out_path)
    try:
        make_viable_path(hdf5_path)
        make_viable_path(ref_path, args.overwrite)
        export_reference_matrix(hdf5_path, ref_path)
    except (PermissionError, FileExistsError):
        print(f"SQUIRE failed to write to {ref_path}", file=stderr)
        exit(1)
