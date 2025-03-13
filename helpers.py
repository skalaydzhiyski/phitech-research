import os
import pandas as pd
import vectorbt as vbt


def load_instruments(base_path="../../phitech-data/01_raw"):
    return {
        fname.split("_")[0]: pd.read_csv(f"{base_path}/{fname}")
        for fname in os.listdir(base_path)
    }


def to_indicator(series):
    return (
        vbt.IndicatorFactory(
            input_names=["series"],
            output_names=["values"],
        )
        .from_apply_func(lambda x: x)
        .run(series)
    )
