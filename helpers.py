import os
import pandas as pd
import vectorbtpro as vbt
import platform


class SierraChartData(vbt.Data):
    @classmethod
    def _load_from_local(
        cls,
        symbol,
        start=None,
        end=None,
    ):
        # I fully understand there are better ways of doing this :)
        if platform.system().strip().lower() == "windows":
            base_data_path = "H:\\phitech-data\\01_raw"
            separator = "\\"
        else:
            base_data_path = "../../phitech-data/01_raw"
            separator = "/"

        filters = None
        if start is not None:
            filters = filters or []
            filters.append(("date", ">=", start))
        if end is not None:
            filters = filters or []
            filters.append(("date", "<=", end))

        symbol_path = f"{base_data_path}{separator}{symbol}_1000d.parquet"
        res = pd.read_parquet(symbol_path, filters=filters)
        res["timestamp"] = pd.to_datetime(res.timestamp)
        res = res.reset_index(drop=True).set_index("timestamp")
        return res

    @classmethod
    def fetch_symbol(cls, symbol, **kwargs):
        return SierraChartData._load_from_local(symbol, **kwargs)

    @classmethod
    def ffill(cls, df):
        for symbol in df.data.keys():
            df.data[symbol] = df.data[symbol].ffill()
        return df


def to_indicator(series):
    return (
        vbt.IndicatorFactory(
            input_names=["series"],
            output_names=["values"],
        )
        .from_apply_func(lambda x: x)
        .run(series)
    )
