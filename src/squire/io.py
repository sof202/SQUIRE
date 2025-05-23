from pathlib import Path

import pandas as pd

from squire.squire_exceptions import BedMethylReadError, HDFReadError


def read_file_of_files(path: Path) -> list[Path]:
    """Read and parse a fof into a list of paths"""
    file_list = []
    with open(path) as fof:
        for file in fof:
            file_list.append(Path(file.replace("\n", "")))
    return file_list


def make_parents(path: Path) -> None:
    """Makes parent directories for a file path"""
    parent_dir = path.parent
    if not parent_dir.exists():
        parent_dir.mkdir(parents=True, exist_ok=True)


def make_viable_path(path: Path, exists_ok: bool = True) -> None:
    """Ensures a path is viable to use by squire

    Parameters
    ---
    exists_ok: bool
        squire overwrites files, so if this isn't desired (user specified)
        file existance will raise an error.
    """
    try:
        if (not exists_ok) and (path.exists()):
            raise FileExistsError(
                f"{path} already exists. "
                "If this is expected rerun with -o/--overwrite"
            )
        make_parents(path)
    except PermissionError as e:
        raise PermissionError(
            f"You do not have permissions to create {path}."
        ) from e


def validate_bedmethyl(
    bedmethyl_path: Path, number_of_rows_to_check: int = 5
) -> None:
    """Validates the format of a bedmethyl file

    Bedmethyl files have a specific format outlined by ONT's modkit. This
    will attempt to verify whether a file fits said format.

    Parameters
    ---
    number_of_rows_to_check: int
        The number of rows to use when validating the file format. If the file
        is malformed beyond these lines, this function will not report it.
    """
    if not bedmethyl_path.exists():
        raise BedMethylReadError(f"{bedmethyl_path} does not exist.")
    if not bedmethyl_path.is_file():
        raise BedMethylReadError(f"{bedmethyl_path} is not a regular file.")
    if bedmethyl_path.stat().st_size == 0:
        raise BedMethylReadError(f"{bedmethyl_path} is empty.")

    expected_dtypes = {
        0: "str",  # chrom
        1: "int64",  # start position
        2: "int64",  # end position
        3: "str",  # modified base code
        4: "int64",  # score
        5: "str",  # strand
        6: "int64",  # start position
        7: "int64",  # end position
        8: "str",  # color
        9: "int64",  # Nvalid_cov
        10: "float64",  # fraction modified
        11: "int64",  # Nmod
        12: "int64",  # Ncanonical
        13: "int64",  # Nother_mod
        14: "int64",  # Ndelete
        15: "int64",  # Nfail
        16: "int64",  # Ndiff
        17: "int64",  # Nnocall
    }

    try:
        top_rows = pd.read_csv(
            bedmethyl_path,
            sep=r"\s+",
            header=None,
            nrows=number_of_rows_to_check,
            dtype=expected_dtypes,  # type: ignore[arg-type]
        )

        if top_rows.shape[1] != 18:
            raise BedMethylReadError(
                f"{bedmethyl_path} does not have 18 fields.\n"
                "Ensure that it was created by ONT's modkit"
            )
    except (ValueError, pd.errors.ParserError) as e:
        raise BedMethylReadError(
            f"Type conversion failed in {bedmethyl_path}. "
            f"File may contain invalid values for expected types.\n"
            f"Error: {str(e)}"
        ) from e
    except TypeError as e:
        raise BedMethylReadError(
            f"Invalid type specification while reading {bedmethyl_path}\n"
            f"Error: {str(e)}"
        ) from e
    except Exception as e:
        raise BedMethylReadError(
            f"Unexpected error reading {bedmethyl_path}"
        ) from e


def validate_hdf5(hdf_path: Path) -> bool:
    """Validates the format of a hdf5 file"""
    if not hdf_path.exists():
        raise HDFReadError(f"{hdf_path} does not exist.")
    if not hdf_path.is_file():
        raise HDFReadError(f"{hdf_path} is not a regular file.")
    try:
        with pd.HDFStore(hdf_path, mode="r"):
            return True
    except OSError as e:
        raise HDFReadError(f"{hdf_path} is non-viable") from e


def export_reference_matrix(hdf_path: Path, out_file_path: Path) -> None:
    """Writes reference matrix to file from hdf5 file

    Reference matrix is a tab separated file with the columns:
        - chromosome
        - start
        - end
        - name(m/h)
        - fraction modified cell type 1
        - fraction modified cell type 2
        - ...
        - fraction modified cell type n
    """
    with pd.HDFStore(hdf_path, mode="r") as store:
        merged = store["merged_data"]
        fraction_columns = [
            col for col in merged.columns if "_fraction" in col
        ]
        merged[fraction_columns].reset_index().to_csv(
            out_file_path,
            sep="\t",
            float_format="%.3f",
            header=False,
            index=False,
        )


def export_cpg_list(
    hdf_path: Path, out_file_path: Path, significance_threshold: float
) -> None:
    """Writes a list of genomic loci that pass a significance theshold

    CpG list is a tab separated file with the columns:
        - chromosome
        - start
        - end
        - name(m/h)

    Parameters
    ---
    significance_threshold: float
        The threshold by which the genomic loci are filtered on
    """
    with pd.HDFStore(hdf_path, mode="r") as store:
        cpg_list = store["stats"]
        cpg_list = cpg_list[cpg_list["p_value"] < significance_threshold]
        cpg_list[["chr", "start", "end", "name"]].to_csv(
            out_file_path, sep="\t", header=False, index=False
        )
