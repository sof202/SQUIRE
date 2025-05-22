from pathlib import Path

import pandas as pd


def pvalue_threshold_report(
    hdf_file: Path, threshold_list: list[float], machine_parsable: bool
) -> None:
    """Print number of genomic loci that pass a certain pvalue threshold"""
    with pd.HDFStore(hdf_file, mode="r") as store:
        stats = store["stats"]
        for threshold in threshold_list:
            n_rows = sum(stats["p_value"] < threshold)
            if machine_parsable:
                print(f"{threshold}:{n_rows}")
            else:
                print(
                    f"If you use a threshold of {threshold}: "
                    f"{n_rows} cpgs will remain."
                )
