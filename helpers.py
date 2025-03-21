import os
import pandas as pd
import vectorbtpro as vbt
import platform


class SierraChartData(vbt.Data):
    @classmethod
    def _load_from_local(
        cls,
        symbol,
        interval,
        start=None,
        end=None,
    ):
        # I fully understand there are better ways of doing this :)
        if platform.system().strip().lower() == 'windows':
            base_data_path = "H:\\phitech-data\\01_raw"
            separator = "\\"
        else:
            base_data_path = "../../phitech-data/01_raw"
            separator = "/"

        res = pd.read_csv(f"{base_data_path}{separator}{symbol}_{interval}.csv")
        res["timestamp"] = res["date"] + " " + res["time"]
        res["timestamp"] = pd.to_datetime(res.timestamp)
        res = res.reset_index(drop=True).set_index("timestamp")
        res = res.drop(columns=["date", "time"])
        return res[start:end]

    @classmethod
    def fetch_symbol(cls, symbol, interval, **kwargs):
        return SierraChartData._load_from_local(symbol, interval, **kwargs)


def to_indicator(series):
    return (
        vbt.IndicatorFactory(
            input_names=["series"],
            output_names=["values"],
        )
        .from_apply_func(lambda x: x)
        .run(series)
    )
