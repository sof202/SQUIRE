import os
import pandas as pd


def get_file_basename(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]


def add_file_to_hdf_store(file_path, hdf_path, chunk_size=100_000):
    mode_to_use = "w" if not os.path.exists(hdf_path) else "a"
    with pd.HDFStore(hdf_path, mode=mode_to_use) as store:
        columns_to_keep = [0, 1, 2, 3, 4, 11]
        basename = get_file_basename(file_path)
        column_names = [
            "chr",
            "start",
            "end",
            "name",
            f"{basename}_read_depth",
            f"{basename}_modifications",
        ]
        column_dtypes = {
            "chr": str,
            "start": int,
            "end": int,
            "name": str,
            f"{basename}_read_depth": int,
            f"{basename}_modifications": int,
        }
        for chunk in pd.read_csv(
            file_path,
            sep=r"\s+",  # bedmethyl has mix of tabs and spaces for separators
            header=None,
            usecols=columns_to_keep,  # type: ignore[arg-type]
            names=column_names,
            dtype=column_dtypes,  # type: ignore[arg-type]
            chunksize=chunk_size,
        ):
            chunk[f"{basename}_fraction"] = (
                chunk[f"{basename}_modifications"]
                / chunk[f"{basename}_read_depth"]
                * 100
            )
            if mode_to_use == "w":
                store.append(
                    f"data/{basename}", chunk, format="table", data_columns=True
                )
            else:
                store.append(f"data/{basename}", chunk)


def generate_coordinate_index(hdf_path, chunk_size=100_000):
    with pd.HDFStore(hdf_path, mode="a") as store:
        all_coordinates = []
        data_paths = [key for key in store.keys() if key.startswith("/data/")]
        for path in data_paths:
            for chunk in store.select(
                path, columns=["chr", "start", "end", "name"], chunksize=chunk_size
            ):
                all_coordinates.append(chunk)

        coordinates = (
            pd.concat(all_coordinates, ignore_index=True)
            .drop_duplicates()
            .sort_values(by=["chr", "start", "end", "name"])
            .reset_index(drop=True)
            .astype(
                {
                    "chr": "category",
                    "start": "uint32",
                    "end": "uint32",
                    "name": "category",
                }
            )
        )
        store.put("coordinates", coordinates, format="table", data_columns=True)
        store.create_table_index(
            "coordinates", columns=["chr", "start", "end"], kind="full"
        )


def create_merged_dataset(hdf_path):
    with pd.HDFStore(hdf_path, mode="a") as store:
        coords = store["coordinates"]
        merged = coords.set_index(["chr", "start", "end", "name"]).copy()
        bedmethyl_paths = [k for k in store.keys() if k.startswith("/data/")]

        for path in bedmethyl_paths:
            bedmethyl = store[path].set_index(["chr", "start", "end", "name"])
            merged = merged.join(bedmethyl, how="left")
        merged = merged.fillna(0)
        store.put("merged_data", merged, format="table", data_columns=True)
        for path in bedmethyl_paths:
            store.remove(path)

        store.remove("coordinates")


def export_reference_matrix(hdf_path, out_file_path):
    with pd.HDFStore(hdf_path, mode="r") as store:
        merged = store["merged_data"]
        fraction_columns = [col for col in merged.columns if "_fraction" in col]
        merged[fraction_columns].reset_index().to_csv(
            out_file_path, sep="\t", float_format="%.3f", header=False
        )
