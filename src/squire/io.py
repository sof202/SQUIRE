from pathlib import Path
import pandas as pd


def read_file_of_files(path: Path):
    file_list = []
    with open(path, mode="r") as fof:
        for file in fof:
            file_list.append(Path(file))
    return file_list


def make_parents(path: Path):
    parent_dir = path.parent
    if not parent_dir.exists():
        parent_dir.mkdir(parents=True, exist_ok=True)


def make_viable_path(path: Path, exists_ok=True):
    try:
        if (not exists_ok) and (path.exists()):
            raise FileExistsError(
                f"{path} already exists, if this is expected rerun with -o/--overwrite"
            )
        make_parents(path)
    except PermissionError:
        raise PermissionError(f"You do not have permissions to create {path}.")


def is_viable_bedmethyl(bedmethyl_path: Path, number_of_rows_to_check=5):
    if not bedmethyl_path.exists():
        return False
    if not bedmethyl_path.is_file():
        return False
    if bedmethyl_path.stat().st_size == 0:
        return False

    expected_dtypes = [
        "str",  # chrom
        "int64",  # start position
        "int64",  # end position
        "str",  # modified base code
        "int64",  # score
        "str",  # strand
        "int64",  # start position (compat)
        "int64",  # end position (compat)
        "str",  # color
        "int64",  # Nvalid_cov
        "float64",  # fraction modified
        "int64",  # Nmod
        "int64",  # Ncanonical
        "int64",  # Nother_mod
        "int64",  # Ndelete
        "int64",  # Nfail
        "int64",  # Ndiff
        "int64",  # Nnocall
    ]

    try:
        top_rows = pd.read_csv(
            bedmethyl_path,
            sep=r"\s+",
            header=None,
            nrows=number_of_rows_to_check,
            dtype={9: "str"},  # force color column to be string
        )

        if top_rows.shape[1] != 18:
            return False

        for i, (expected, actual) in enumerate(zip(expected_dtypes, top_rows.dtypes)):
            if str(actual) != expected:
                return False

        return True

    except Exception:
        return False


def is_viable_hdf5(hdf_path: Path):
    if not hdf_path.exists() or not hdf_path.is_file():
        return False
    try:
        with pd.HDFStore(hdf_path, mode="r"):
            return True
    except (OSError, IOError):
        return False


def export_reference_matrix(hdf_path, out_file_path):
    with pd.HDFStore(hdf_path, mode="r") as store:
        merged = store["merged_data"]
        fraction_columns = [col for col in merged.columns if "_fraction" in col]
        merged[fraction_columns].reset_index().to_csv(
            out_file_path, sep="\t", float_format="%.3f", header=False, index=False
        )


def export_cpg_list(hdf_path, out_file_path, significance_threshold):
    with pd.HDFStore(hdf_path, mode="r") as store:
        cpg_list = store["stats"]
        cpg_list = cpg_list[cpg_list["p_value"] < significance_threshold]
        cpg_list[["chr", "start", "end", "name"]].to_csv(
            out_file_path, sep="\t", header=False, index=False
        )
