import os
import pandas as pd


base_data_path = "/mnt/s/SierraChart/Data"
history_data_path = "/mnt/h/phitech-data/01_raw"


# read all .txt files in the base_data_path directory one by one and save them to the history_data_path directory
def export_data_to_history():
    print("export data to history..")
    for file in os.listdir(base_data_path):
        if not file.endswith(".txt"):
            continue

        filepath = os.path.join(base_data_path, file)
        print(f"current file -> {filepath}")

        df = pd.read_csv(filepath)
        df.columns = [
            c.strip().replace("#", "N").replace(" ", "_").lower() for c in df.columns
        ]
        df.columns = [c if c != "last" else "close" for c in df.columns]
        df["timestamp"] = df["date"] + " " + df["time"]
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.drop(columns=["time"])
        df["date"] = pd.to_datetime(df["date"])
        df = df[
            [
                "timestamp",
                "date",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "bidvolume",
                "askvolume",
                "numberoftrades",
            ]
        ]
        target_path = os.path.join(history_data_path, file.replace(".txt", ".parquet"))
        df.to_parquet(target_path, partition_cols=["date"], index=False)
        print(f"saved to -> {target_path}")
        print(f"delete old file -> {filepath}")
        os.remove(filepath)
    print("done.")


export_data_to_history()
