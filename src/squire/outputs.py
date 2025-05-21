import pandas as pd


def export_reference_matrix(hdf_path, out_file_path):
    with pd.HDFStore(hdf_path, mode="r") as store:
        merged = store["merged_data"]
        fraction_columns = [col for col in merged.columns if "_fraction" in col]
        merged[fraction_columns].reset_index().to_csv(
            out_file_path, sep="\t", float_format="%.3f", header=False
        )
