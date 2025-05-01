#!/usr/bin/env python3

import os
import glob
import json
import argparse

import matplotlib
matplotlib.use('Agg')  # use non-interactive backend to avoid macOS IME warnings
import matplotlib.pyplot as plt
import pandas as pd

def load_logs(log_dir: str) -> pd.DataFrame:
    """
    Reads all .json files in `log_dir`, and returns a DataFrame with columns:
      website, network_condition, tester, time_seconds, load_time_ms
    """
    pattern = os.path.join(log_dir, "*.json")
    files = glob.glob(pattern)
    print(f">>> Found JSON files: {files}")
    
    records = []
    for path in files:
        fname = os.path.splitext(os.path.basename(path))[0]
        website = fname.replace("_", "/")
        with open(path, "r") as f:
            stats = json.load(f)
        for cond, testers in stats.items():
            for tester_name, times in testers.items():
                for delta_str, ms in times.items():
                    records.append({
                        "website": website,
                        "network_condition": cond,
                        "tester": tester_name,
                        "time_seconds": int(delta_str),
                        "load_time_ms": ms
                    })
    df = pd.DataFrame.from_records(records)
    print(f">>> Loaded {len(df)} records into DataFrame")
    return df

def summarize(df: pd.DataFrame):
    """
    Summarize raw averages and compute per-site enhancement.
    Returns the avg DataFrame and the pivot (enhancement) DataFrame.
    """
    # 1) Average load time per condition/tester/age
    avg = (
        df
        .groupby(["network_condition", "tester", "time_seconds"], as_index=False)
        .load_time_ms.mean()
        .rename(columns={"load_time_ms": "avg_load_time_ms"})
    )
    print("\n=== Average load times ===")
    print(avg.to_string(index=False))
    
    # 2) Per-website enhancement: Classic vs CacheV2
    pivot = df.pivot_table(
        index=["network_condition", "website", "time_seconds"],
        columns="tester",
        values="load_time_ms"
    ).reset_index()
    pivot["enhancement"] = (
        pivot["ClassicLoadTester"] - pivot["CacheV2LoadTester"]
    ) / pivot["ClassicLoadTester"]
    
    print("\n=== Per-website CacheV2 enhancement over Classic ===")
    print(
        pivot
        .loc[:, ["network_condition", "website", "time_seconds", "enhancement"]]
        .to_string(index=False)
    )
    return avg, pivot

def plot_enhancement(pivot: pd.DataFrame, out_path: str):
    """
    Draw and save a per-website enhancement plot.
    """
    plt.figure(figsize=(12, 8))
    for (cond, site), grp in pivot.groupby(["network_condition", "website"]):
        plt.plot(
            grp["time_seconds"], grp["enhancement"],
            marker="o", label=f"{site} @ {cond}"
        )
    plt.xlabel("Cache-age (s)")
    plt.ylabel("Enhancement (CacheV2 vs Classic)")
    plt.title("Per-website CacheV2 Enhancement over ClassicLoadTester")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f">>> Saved enhancement plot to: {out_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Analyze load-test JSON logs"
    )
    parser.add_argument(
        "log_dir", help="Folder containing your .json log files"
    )
    parser.add_argument(
        "--no-plot", action="store_true",
        help="Skip the enhancement plot and just print tables"
    )
    args = parser.parse_args()

    log_dir = args.log_dir
    print(f">>> Using log_dir: {os.path.abspath(log_dir)}")

    # Load and process
    df = load_logs(log_dir)
    avg, pivot = summarize(df)

    # Export to CSV
    avg_csv = os.path.join(log_dir, "avg_load_times.csv")
    enh_csv = os.path.join(log_dir, "per_site_enhancement.csv")
    try:
        avg.to_csv(avg_csv, index=False)
        pivot.to_csv(enh_csv, index=False)
        print(f">>> Exported average load times to: {avg_csv}")
        print(f">>> Exported per-site enhancement to: {enh_csv}")
    except Exception as e:
        print(f"Warning: failed to write CSV files: {e}")

    # Plot (unless skipped)
    if not args.no_plot:
        plot_path = os.path.join(log_dir, "enhancement_curve.png")
        plot_enhancement(pivot, plot_path)

if __name__ == "__main__":
    main()
