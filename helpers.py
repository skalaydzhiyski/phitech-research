import os
import pandas as pd
import vectorbtpro as vbt


def make_backtest_universe(instruments, col='close', dropna=False):
    series = [i[col] for i in instruments.values()]
    res = pd.concat(series, keys=instruments.keys(), names=["ticker"], axis=1)
    res.ffill(inplace=True)
    return res


def load_instruments(base_path="../../phitech-data/01_raw"):
    res = {}
    for fname in os.listdir(base_path):
        df = pd.read_csv(f"{base_path}/{fname}")
        df['timestamp'] = df['date'] + " " + df['time']
        df = df.drop(columns=['date', 'time'])
        df = df.set_index('timestamp')
        res[fname.split("_")[0]] = df
    return res


def to_indicator(series):
    return (
        vbt.IndicatorFactory(
            input_names=["series"],
            output_names=["values"],
        )
        .from_apply_func(lambda x: x)
        .run(series)
    )
