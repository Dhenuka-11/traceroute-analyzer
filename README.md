Traceroute Analyzer

Description
Traceroute Analyzer is a Python tool that performs multiple traceroute runs to a target host, collects per-hop latency data, and generates statistical metrics and visualizations. It’s designed to help analyze network paths, measure latency variations, and detect unresponsive hops.

Features

Perform multiple traceroute attempts with configurable delays

Parse traceroute output and calculate per-hop statistics (min, max, median, average)

Generate JSON reports of latency metrics

Produce latency boxplots for visual analysis

Optionally load precomputed traceroute outputs

Dependencies
Install dependencies using pip:

pip install -r requirements.txt


Usage

Perform a traceroute and save results:

python trstats.py -t <target_host> -n <number_of_runs> -d <delay_between_runs> -m <hop_limit> -o results.json -g plot.pdf


Example:

python trstats.py -t example.com -n 3 -d 2 -m 30 -o results.json -g latency_plot.pdf


Load precomputed traceroute files:

python trstats.py --test <folder_with_outputs> -o results.json -g latency_plot.pdf


Outputs

results.json: Contains structured per-hop latency data and statistics

latency_plot.pdf: Boxplot visualization of latency per hop

