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
