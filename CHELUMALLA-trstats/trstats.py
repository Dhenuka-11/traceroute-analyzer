import argparse
import subprocess
import matplotlib.pyplot as plt
import os
import time
import json

def do_traceroute(host, runs, wait, hop_limit):
    results = []
    for attempt in range(runs):
        print(f"Running traceroute attempt {attempt + 1} to {host}...")
        output = subprocess.run(
            ['traceroute', '-m', str(hop_limit), host],
            capture_output=True,
            text=True
        ).stdout
        print("Traceroute completed, capturing output:")
        print(output)
        hops = parse_hops(output)
        results.append(hops)
        if wait > 0:
            print(f"Waiting {wait} seconds before next attempt...")
            time.sleep(wait)
    return results

def parse_hops(raw_output):
    hops = []
    for line in raw_output.splitlines():
        if line.strip() and not line.lower().startswith('traceroute'):
            segments = line.split()
            if segments[0].isdigit():
                hop_num = int(segments[0])
                latencies = []
                addresses = []
                if '*' in line:
                    hops.append({
                        'hop': hop_num,
                        'hosts': [],
                        'latency': ["Hop is unresponsive"]
                    })
                else:
                    for i in range(1, len(segments) - 1):
                        value = segments[i]
                        if value.replace('.', '').isdigit() and segments[i + 1] == "ms":
                            latencies.append(float(value))
                        elif "ms" not in value:
                            addresses.append(value)
                    while len(latencies) < 3:
                        latencies.append(0.0)
                    hops.append({
                        'hop': hop_num,
                        'hosts': addresses,
                        'latency': latencies
                    })
    return hops

def calculate_stats(all_runs, hop_limit):
    stats = []
    hop_groups = {}

    for trace in all_runs:
        for hop in trace:
            hop_groups.setdefault(hop['hop'], []).append(hop)

    for hop_num in range(1, hop_limit + 1):
        current_hops = hop_groups.get(hop_num, [])
        latencies_collected = []
        host_list = []

        for hop in current_hops:
            if hop['latency'] != ["Hop is unresponsive"]:
                latencies_collected.extend(hop['latency'])
                host_list = hop['hosts']

        if not latencies_collected: 
            stats.append({
                'hop': hop_num,
                'hosts': [],
                'latency': [],
                'avg': "Hop is unresponsive",
                'max': "Hop is unresponsive",
                'median': "Hop is unresponsive",
                'min': "Hop is unresponsive"
            })
        else:
            stats.append({
                'hop': hop_num,
                'hosts': host_list,
                'latency': latencies_collected,
                'avg': round(sum(latencies_collected)/len(latencies_collected), 3),
                'max': max(latencies_collected),
                'median': sorted(latencies_collected)[len(latencies_collected)//2],
                'min': min(latencies_collected)
            })
    return stats

def draw_plot(stats, file_path, target_host=None):
    hops = []
    latency_data = []

    for hop in stats:
        hops.append(f"Hop {hop['hop']}")
        if hop['latency']:  # non-empty
            latency_data.append(hop['latency'])
        else:
            latency_data.append([0]) 

    import matplotlib.pyplot as plt
    plt.figure(figsize=(12, 6))
    plt.boxplot(latency_data, labels=hops, patch_artist=True, showmeans=True)
    plt.xticks(rotation=90)
    plt.xlabel("Hop Number")
    plt.ylabel("Latency (ms)")
    plt.title(f"Latency Distribution per Hop{f' ({target_host})' if target_host else ''}")
    plt.tight_layout()
    plt.savefig(file_path, format='pdf')
    plt.close()

def load_saved(folder):
    runs = []
    for fname in os.listdir(folder):
        full_path = os.path.join(folder, fname)
        with open(full_path, 'r') as f:
            file_content = f.read()
            runs.append(parse_hops(file_content))
    print(f"Traceroute outputs loaded from {folder}")
    return runs

def save_json(data, fname):
    print(f"Writing metrics to {fname}")
    with open(fname, 'w') as f:
        json.dump(data, f, indent=4)

def main():
    parser = argparse.ArgumentParser(
        description="Traceroute Latency Analyzer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-n', dest='no_runs', type=int, default=1)
    parser.add_argument('-d', dest='run_delay', type=int, default=0)
    parser.add_argument('-m', dest='hop_limit', type=int, default=30)
    parser.add_argument('-o', dest='output', required=True)
    parser.add_argument('-g', dest='graph', required=True)
    parser.add_argument('-t', dest='target', help='Target host or IP')
    parser.add_argument('--test', dest='test_dir', help='folder with precomputed traceroute outputs')
    args = parser.parse_args()

    if args.test_dir:
        print(f"Using existing traceroute files in {args.test_dir}")
        data = load_saved(args.test_dir)
    else:
        if not args.target:
            parser.error("Target host required if --test is not used")
        print(f"Starting traceroute to {args.target}")
        data = do_traceroute(args.target, args.no_runs, args.run_delay, args.hop_limit)

    stats = calculate_stats(data, args.hop_limit)
    save_json(stats, args.output)
    draw_plot(stats, args.graph, args.target)

if __name__ == "__main__":
    main()
