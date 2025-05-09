from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import json
import os

# TIMESTAMPS = [60, 3600, 21600, 86400, 604800, 31622400] # 1 min, 1 hour, 12 hours, 1 day, 1 week, 1 year
TIMESTAMPS = [60, 43200, 604800, 31622400] # 1 min, 12 hours, 7 days, 1 year

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

def percent_plot(data: dict, title: str, baseline_label='baseline', improve_label='improve'):
    """
    Plot the data points as percentages.
    """
    offset = 0.125
    width = 0.25
    
    x = np.arange(len(TIMESTAMPS))
    fig, ax = plt.subplots(layout='constrained')
    fig.set_figwidth(10)

    baseline = ax.bar(x - offset, data[baseline_label], width, label=baseline_label)
    ax.bar_label(baseline, padding=3)
    improve = ax.bar(x + offset, data[improve_label], width, label=improve_label)
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

def load_common_sites_from_json(old_file: str, new_file: str):
    """
    Load common sites from a JSON file.
    """
    # Load data points from the specified directory
    with open(old_file, 'r') as f:
        datapoints = json.load(f)
    with open(new_file, 'r') as f:
        new_datapoints = json.load(f)

    return intersect(datapoints, new_datapoints)

def compare_sites(baseline_file: str, improve_file: str, baseline_label='baseline', improve_label='improve'):
    same_sites = load_common_sites_from_json(baseline_file, improve_file)
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
        baseline_label: o,
        improve_label: n
    }, "Average of all sites", baseline_label=baseline_label, improve_label=improve_label)

def plot_site(file: str):
    with open(file, 'r') as f:
        datapoints = json.load(f)
        latencies = defaultdict(list)
        for site, data in datapoints.items():
            # print(f"Site: {site}")
            for key, value in data.items():
                # print(f"Key: {key}")
                baseline = datapoint_to_array(value['ClassicLoadTester'])
                improve = datapoint_to_array(value['CacheV2LoadTester'])
                diff = (baseline - improve) / baseline * 100
                latencies[key].append(diff)
        
        plt.figure(figsize=(10, 8))
        for key, value in latencies.items():
            # Plot the mean of all sites
            marker = 'o' if '60Mbps' in key else 'x'
            marker = ',' if '1Mbps' in key else marker
            color = 'blue' if '200' in key else 'orange'
            color = 'green' if '100' in key else color
            plt.plot(np.mean(np.stack(value), axis=0), label=key, marker=marker, color=color)
        plt.title(f"(cloudlab) Average page load time enhanced vs boarderline")
        # plt.xticks(range(6), ['1 min', '1hr', '6hrs', '1 day', '1 week', '366 days'])
        plt.xticks(range(len(TIMESTAMPS)), ['1 min', '12 hr', '1 week', '1 year'])
        plt.xlabel("Time")
        plt.ylabel("Improvement (%)")
        plt.legend()
        plt.show()
       


if __name__ == "__main__":
    # compare_sites('aggregated-cloudlab-old.json', 'aggregated-cloudlab-new.json')
    # compare_sites('aggregated-ubuntu-old.json', 'aggregated-ubuntu-old-initial-attempt.json', baseline_label='recent', improve_label='initial')
    # compare_sites('aggregated-ubuntu-old.json', 'aggregated-cloudlab-old.json', baseline_label='local', improve_label='cloud-lab')
    # plot_site('aggregated-ubuntu-old.json')
    # plot_site('aggregated-ubuntu-old-initial-attempt.json')
    plot_site('aggregated-cloudlab-new.json')
    # compare_sites('aggregated-cloudlab-old.json', 'aggregated-cloudlab-new.json', baseline_label='original', improve_label='enhanced')
    # with open('aggregated-ubuntu-old-initial-attempt.json', 'r') as f:
    #     data =  json.load(f)
    #     print(len(data.keys()))