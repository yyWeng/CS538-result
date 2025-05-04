import json
import os

# data -> aggregated-ubuntu-old-initial-attempt.json
# log -> aggregated-ubuntu-new-with-logging-enabled.json
if __name__ == '__main__':
    dir = 'data'
    aggreagate = {}

    for file in os.listdir(dir):
        if file.endswith('.json'):
            with open(os.path.join(dir, file), 'r') as f:
                site = file.replace('http:__localhost:8080_', '').replace('.json', '')
                data = json.load(f)
                aggreagate[site] = data
                # for site, datapoints in data.items():
                #     if site not in aggreagate:
                #         aggreagate[site] = {}
                #     for key, datapoint in datapoints.items():
                #         if key not in aggreagate[site]:
                #             aggreagate[site][key] = {}
                #         aggreagate[site][key].update(datapoint)
    # with open('aggregated-cloudlab.json', 'w') as f:
    # print(json.dumps(aggreagate, indent=4))
    with open('aggregated-ubuntu-old-initial-attempt.json', 'w') as f:
        json.dump(aggreagate, f, indent=4)