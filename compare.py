import os
import json
import matplotlib.pyplot as plt
from collections import defaultdict

log_dir = "log"
data = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

# Step 1: Read all JSON files
for filename in os.listdir(log_dir):
    if filename.endswith(".json") or filename.startswith("http"):  # assuming your logs are named like in the image
        filepath = os.path.join(log_dir, filename)
        try:
            with open(filepath) as f:
                content = json.load(f)
                for net_cond, testers in content.items():
                    for tester, results in testers.items():
                        for ttl, value in results.items():
                            data[net_cond][tester][int(ttl)] = value
        except Exception as e:
            print(f"Error reading {filename}: {e}")

# Step 2: Plot each network condition
for net_cond, testers in data.items():
    plt.figure(figsize=(10, 5))
    for tester, ttl_data in testers.items():
        ttl_sorted = sorted(ttl_data.items())
        ttls, values = zip(*ttl_sorted)
        plt.plot(ttls, values, marker='o', label=tester)

    plt.title(f"Performance under {net_cond}")
    plt.xlabel("TTL (seconds)")
    plt.ylabel("the median load time at that age (ms)")
    plt.legend()
    plt.grid(True)
    plt.xscale('log')
    plt.tight_layout()
    plt.savefig(f"plot_{net_cond.replace(' ', '_').replace('(', '').replace(')', '').replace(':', '-')}.png")
    plt.close()

print("Analysis complete. Plots saved.")
