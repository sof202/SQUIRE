import pandas as pd


def pvalue_threshold_report(hdf_store, threshold_list):
    with pd.HDFStore(hdf_store, mode="r") as store:
        stats = store["stats"]
        for threshold in threshold_list:
            n_rows = sum(stats["p_value"] < threshold)
            print(f"for {threshold}: {n_rows} cpgs will remain.")
