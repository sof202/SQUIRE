import multiprocessing
import pandas as pd
from multiprocessing import Pool
import numpy as np
from scipy.stats import chi2_contingency
from statsmodels.stats.proportion import proportions_ztest


def generate_batch(store, chunk_size):
    bedmethyls = sorted(
        {
            col.split("_")[0]
            for col in store["merged_data"].columns
            if "_modifications" in col
        }
    )

    for chunk in store.select("merged_data", chunksize=chunk_size):
        batch = []
        for _, row in chunk.iterrows():
            counts = np.array(
                [row[f"{bedmethyl}_modifications"] for bedmethyl in bedmethyls]
            )
            read_depths = np.array(
                [row[f"{bedmethyl}_read_depth"] for bedmethyl in bedmethyls]
            )

            batch.append(
                (
                    row.name,
                    counts,
                    read_depths,
                )
            )
        yield batch


def two_proportion_z_test(counts, read_depths):
    valid_indexes = read_depths > 0
    if sum(valid_indexes) < 2:
        return 1
    _, p_value = proportions_ztest(counts, read_depths)
    if np.isnan(p_value):
        return 1
    return p_value


def chi_squared_contingency(counts, read_depths):
    valid_indexes = read_depths > 0
    if sum(valid_indexes) < 2:
        return 1
    contingency_table = np.vstack(
        [counts[valid_indexes], read_depths[valid_indexes] - counts[valid_indexes]]
    )
    try:
        _, p_value, _, _ = chi2_contingency(contingency_table)
        return p_value
    except ValueError:
        return 1


def process_row(row, stats_function):
    id, counts, read_depths = row
    p_value = stats_function(counts, read_depths)
    return (*id, p_value)


def compute_p_values(hdf_path, n_processes=None, chunk_size=100_000):
    if n_processes is None:
        n_processes = multiprocessing.cpu_count() - 1 or 1

    with pd.HDFStore(hdf_path, mode="r") as store:
        sample_count = sum(
            1 for col in store["merged_data"].columns if "_modifications" in col
        )

        if sample_count == 1:
            raise ValueError("Not enough samples, no need to run SQUIRE")
        elif sample_count == 2:
            stats_function = two_proportion_z_test
        else:
            stats_function = chi_squared_contingency

    with pd.HDFStore(hdf_path, mode="r+") as store:
        for batch in generate_batch(store, chunk_size):
            with Pool(n_processes) as pool:
                from functools import partial

                process_function = partial(process_row, stats_function=stats_function)
                results = pool.map(
                    process_function,
                    batch,
                    chunksize=max(1, len(batch) // (n_processes * 4)),
                )

            stats_chunk = pd.DataFrame(
                results,
                columns=["chr", "start", "end", "name", "p_value"],  # type: ignore[arg-type]
            ).sort_values(["chr", "start", "end", "name"])

            store.append("stats", stats_chunk, format="table", data_columns=True)
