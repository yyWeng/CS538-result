import numpy as np
import matplotlib.pyplot as plt
import json
import os

TIMESTAMPS = [60, 3600, 21600, 86400, 604800, 31622400]

def load_datapoints(dir: str):
    """
    Load data points from a directory containing JSON files.
    Each JSON file should contain a list of data points.
    """
    datapoints = {}
    for filename in os.listdir(dir):
        if filename.endswith('.json'):
            site = filename.replace('http:__localhost:8080_', '').replace('.json', '')
            with open(os.path.join(dir, filename), 'r') as f:
                data = json.load(f)
                datapoints[site] = data
    return datapoints


def intersect(a: dict, b: dict):
    """
    Find the intersection by keys of two dictionary.
    """
    c = {}
    for key in a:
        if key not in b:
            continue

        c[key] = [a[key], b[key]]
    return c

def datapoint_to_array(data: dict):
    """
    Convert a dictionary of data points to a numpy array.
    """
    keys = sorted(list(data.keys()), key=int)
    values = [data[key] for key in keys]
    return np.array(values)

def linear_plot(data: dict, site: str):
    """
    Plot the data points.
    """
    plt.figure(figsize=(10, 6))
    for key, value in data.items():
        plt.plot(value, label=key)
    plt.title(f"Data points for {site}")
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.legend()
    plt.show()

def percent_plot(data: dict, title: str):
    """
    Plot the data points as percentages.
    """

    offset = 0.125
    width = 0.25
    
    x = np.arange(len(TIMESTAMPS))
    fig, ax = plt.subplots(layout='constrained')
    fig.set_figwidth(10)

    baseline = ax.bar(x - offset, data['baseline'], width, label='baseline')
    ax.bar_label(baseline, padding=3)
    improve = ax.bar(x + offset, data['improve'], width, label='improve')
    ax.bar_label(improve, padding=3)

    ax.set_title(f"{title} (in %)")
    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('Percentage')
    ax.legend(loc='best')
    ax.set_xticks(range(len(TIMESTAMPS)))
    ax.set_xticklabels(TIMESTAMPS)

    plt.show()


def load_common_sites(old_dir: str, new_dir: str):
    """
    Load common sites from a JSON file.
    """
    # Load data points from the specified directory
    datapoints = load_datapoints(old_dir)
    new_datapoints = load_datapoints(new_dir)

    return intersect(datapoints, new_datapoints)

def main():
    same_sites = load_common_sites('data', 'log')
    old_improves, new_improves = [], []
    for site, data in same_sites.items():
        print(f"Site: {site}")
        old, new = data

        for key in old.keys():
            # print(f"Key: {key}")
            boarderline_old = datapoint_to_array(old[key]['ClassicLoadTester'])
            boarderline_new = datapoint_to_array(new[key]['ClassicLoadTester'])
            # boarderline = np.mean(np.stack((boarderline_old, boarderline_new)), axis=0)
            baseline = datapoint_to_array(old[key]['CacheV2LoadTester'])
            improve = datapoint_to_array(new[key]['CacheV2LoadTester'])

            baseline_percent = (boarderline_old - baseline) / boarderline_old * 100
            improve_percent = (boarderline_new - improve) / boarderline_new * 100
            # percent_plot({
            #     'baseline': baseline_percent,
            #     'improve': improve_percent
            # }, f"{site} {key}")
            old_improves.append(baseline_percent)
            new_improves.append(improve_percent)
    # Plot the average of all sites
    o = np.mean(np.stack(old_improves), axis=0)
    n = np.mean(np.stack(new_improves), axis=0)
    percent_plot({
        'baseline': o,
        'improve': n
    }, "Average of all sites")


if __name__ == "__main__":
    main()