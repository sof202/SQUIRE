import os
from pathlib import Path

import pandas as pd


def get_file_basename(file_path: Path) -> str:
    """Get the basename of a file for organisational purposes"""
    return os.path.splitext(os.path.basename(file_path))[0]


def add_file_to_hdf_store(
    file_path: Path, hdf_path: Path, chunk_size: int = 100_000
) -> None:
    """Add bedmethyl data to a hdf5 store

    Only 6 columns are extracted from bedmethyl files:
        - chromosome
        - start
        - end
        - name(m/h)
        - read depth
        - number of modifications observed

    For each genomic loci, the fraction modified is calculated as well.
    Although this value exists in the bedmethyl file, calculating this value
    instead of reading (and parsing) the field will be as fast if not faster.

    Files are read and parsed in chunks to save on memory.
    """
    mode_to_use = "w" if not os.path.exists(hdf_path) else "a"
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
    with pd.HDFStore(hdf_path, mode=mode_to_use) as store:
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
                    f"data/{basename}",
                    chunk,
                    format="table",
                    data_columns=True,
                )
            else:
                store.append(f"data/{basename}", chunk)


def generate_coordinate_index(
    hdf_path: Path, chunk_size: int = 100_000
) -> None:
    """Generates a full index of genomic loci coordinates from hdf5 store"""
    with pd.HDFStore(hdf_path, mode="a") as store:
        all_coordinates = []
        data_paths = [key for key in store if key.startswith("/data/")]
        for path in data_paths:
            for chunk in store.select(
                path,
                columns=["chr", "start", "end", "name"],
                chunksize=chunk_size,
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
        store.put(
            "coordinates", coordinates, format="table", data_columns=True
        )
        store.create_table_index(
            "coordinates", columns=["chr", "start", "end"], kind="full"
        )


def add_bedmethyls_to_merged_data(
    store: pd.HDFStore, merged: pd.DataFrame
) -> None:
    """Add bedmethyl files to the combined merged data"""
    bedmethyl_paths = [k for k in store if k.startswith("/data/")]

    for path in bedmethyl_paths:
        bedmethyl = store[path].set_index(["chr", "start", "end", "name"])
        merged = merged.join(bedmethyl, how="left")
    merged = merged.fillna(0)
    store.put("merged_data", merged, format="table", data_columns=True)
    for path in bedmethyl_paths:
        store.remove(path)


def create_merged_dataset(hdf_path: Path) -> None:
    """Merges all parsed bedmethyl files into a single dataframe

    Using a hdf5 store and the coordinate index created from
    `generate_coordinate_index`, each stored pandas dataframe will be merged
    into a single dataframe (aligned on the coordinate index).

    All NaN entries will be converted to 0 so as to avoid differening line
    lengths when exporting the data to a reference matrix.

    Also removes coordinate index and individually stored bedmethyl files so as
    to avoid file bloat.
    """
    with pd.HDFStore(hdf_path, mode="a") as store:
        coords = store["coordinates"]
        merged = coords.set_index(["chr", "start", "end", "name"]).copy()
        add_bedmethyls_to_merged_data(store, merged)
        store.remove("coordinates")


def add_to_merged_dataset(hdf_path: Path) -> None:
    """Add newly parsed files in /data/ to merged_data in hdf5 file"""
    with pd.HDFStore(hdf_path, mode="a") as store:
        add_bedmethyls_to_merged_data(store, store["merged_data"])
