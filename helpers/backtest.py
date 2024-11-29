import pandas as pd
import random
import holidays
from progiter import ProgIter
from dotted_dict import DottedDict as dotdict
import json
import datetime
import os

bt_base_path = "/mnt/c/trading/backtest"
base_data_path = "/mnt/c/SierraChart/Data"
base_depth_path = f"{base_data_path}/MarketDepthData"
history_path = "/mnt/h/trading/history"
bt_output_base_path = "/mnt/c/trading/backtest/output"
bt_default_files = ['trades.csv', 'trades_f2f.csv', 'trade_statistics.csv']


def get_run_names_for_backtest(bt_name, instrument):
    return os.listdir(f"{bt_output_base_path}/{bt_name}/{instrument}")

def get_instruments_for_backtest(bt_name):
    return [x.split('/')[-1] for x in os.listdir(f"{bt_output_base_path}/{bt_name}")]

def get_backtest_results_for_instrument(bt_name, instrument):
    run_names = get_run_names_for_backtest(bt_name, instrument)
    bt = {"runs": [{} for _ in range(len(run_names))]}
    for idx, run_name in enumerate(run_names):
        print(f"processing bt run -> {run_name}")
        current_run_path = f"{bt_output_base_path}/{bt_name}/{instrument}/{run_name}"
        files = os.listdir(current_run_path)
        
        bt["runs"][idx] = {}
        start, end = run_name.split('_')[1:]
        bt["runs"][idx]["range"] = {
            "start": datetime.datetime.strptime(start, '%Y%m%d%H%M%S'),
            "end": datetime.datetime.strptime(end, '%Y%m%d%H%M%S')
        }
        
        for fname in bt_default_files:
            bt["runs"][idx][fname.split('.')[0]] = pd.read_csv(f"{current_run_path}/{fname}")
    
        bt["runs"][idx]["subgraphs"] = {}
        bt["runs"][idx]["vectors"] = {}
        for fname in [fn for fn in files if fn not in bt_default_files]:
            name = fname.split(".")[0]
            try:
                if name.startswith('sg_'):
                    bt["runs"][idx]["subgraphs"][name.replace("sg_", "")] = pd.read_csv(f"{current_run_path}/{fname}")
                elif name.startswith("v_"):
                    bt["runs"][idx]["vectors"][name.replace("v_", "")] = pd.read_csv(f"{current_run_path}/{fname}")
                elif name == "persistent_values.csv":
                    bt["runs"][idx]["persistent_values"] = pd.read_csv(f"{current_run_path}/persistent_values.csv")
            except Exception as e:
                print(e)
                continue
            
        print("-"*25)

    print('done.')
    bt = dotdict(bt)
    return bt

def get_backtest_results(bt_name):
    instruments = get_instruments_for_backtest(bt_name)
    return {
        instr: get_backtest_results_for_instrument(bt_name, instr)
        for instr in instruments
    }

def remove_depth_files():
    os.system(f'rm -rf {base_depth_path}/*.depth')

def generate_backtest(name, year, instruments, sample_size, start, end, start_time, end_time, pvars, sg_arrays):
    year_path = f"{history_path}/{year}"
    data_path = f"{year_path}/Data"
    depth_path = f"{data_path}/MarketDepthData"
    depth_files = os.listdir(depth_path)
    idict = {
        instr: {d.split('.')[1]: d for d in depth_files if instr in d}
        for instr in instruments
    }
    main = pd.DataFrame({"day": pd.date_range(start=start, end=end, freq='D')})
    # remove weekends
    main = main[~main.day.dt.day_name().isin(['Sunday', 'Saturday'])]
    # remove bank holidays in major countries
    to_remove_holidays = (
        list(holidays.UnitedKingdom(years=[year]).keys()) +
        list(holidays.UnitedStates(years=[year]).keys()) +
        list(holidays.NewYorkStockExchange(years=[year]).keys()) +
        list(holidays.EuropeanCentralBank(years=[year]).keys())
    )
    main = main[~main.day.isin(pd.to_datetime(to_remove_holidays))]
    date_strings = main.day.apply(lambda x: str(x).split(' ')[0]).tolist()
    if sample_size > 0:
        date_strings = sorted(random.sample(date_strings, k=sample_size))
    print(f'n days -> {len(date_strings)}')

    contracts = []
    for instrument in instruments:
        for date_string in date_strings:
            if date_string in idict[instrument]:
                contracts.append(idict[instrument][date_string].split('.')[0])

    contracts = set(contracts)
    print(f'contracts -> {contracts}')

    print("copy depth files..")
    depth_files_copied = []
    for instrument in instruments:
        print(f'current instrument -> {instrument}')
        for date_string in ProgIter(date_strings):
            if not date_string in idict[instrument].keys():
                print(f'date string missing from files, skip -> {date_string}')
                continue

            depth_file = idict[instrument][date_string]
            if not os.path.exists(f'{base_depth_path}/{depth_file}'):
                os.system(f'cp {depth_path}/{depth_file} {base_depth_path}/{depth_file}')
                depth_files_copied.append(f"{base_depth_path}/{depth_file}")

    date_ranges = []
    for instrument in instruments:
        for date_string in date_strings:
            if not date_string in idict[instrument].keys():
                continue

            current = {
                "data_file": f"{idict[instrument][date_string].split('.')[0]}.scid",
                "start": f"{date_string} {start_time}",
                "end": f"{date_string} {end_time}"
            }
            date_ranges.append(current)

    res = {
        "name": name,
        "date_ranges": date_ranges,
        "sg_arrays": sg_arrays,
        "pvars": pvars
    }
    with open(f"{bt_base_path}/{res['name']}.json", 'w') as f:
        json.dump(res, f, indent=4, sort_keys=False)
    print('done.')
    return depth_files_copied
