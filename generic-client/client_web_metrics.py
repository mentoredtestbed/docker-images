#!/usr/bin/python3
#
# read the data from the URL and print it
#
import urllib.request
import time
import numpy as np
import argparse
import os

def start_requests(sleep_time_min, sleep_time_max, server_ip, output):
    # Ensure that directory exists (recursive)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    # if the output is a directory, append the file name
    if os.path.isdir(output):
        output = os.path.join(output, "client_delay.csv")

    with open(output, 'a') as f:
        f.write("time,delay (seconds)")
        f.write("\n")

    t_init_server = time.time()

    while True:
        t_init = time.time()
        webUrl  = urllib.request.urlopen(f'http://{server_ip}')

        data = webUrl.read()
        time_delay = time.time() - t_init

        stat = "{},{:.3f}".format(
                time.time() - t_init_server,
                time_delay)

        with open(output, 'a') as f:
            f.write(stat)
            f.write("\n")

        time.sleep(np.random.uniform(sleep_time_min, sleep_time_max))


if __name__ == "__main__":

    args = argparse.ArgumentParser()
    args.add_argument("-smin", "--sleep_time_min", help="Minimum sleep time", default=0.1, type=float)
    args.add_argument("-smax", "--sleep_time_max", help="Maximum sleep time", default=0.5, type=float)
    args.add_argument("-ip", "--server_ip", help="Server IP", default="localhost", type=str)
    args.add_argument("-o", "--output", help="Output file", default="/client_delay.csv")

    args = args.parse_args()

    sleep_time_min = args.sleep_time_min
    sleep_time_max = args.sleep_time_max
    server_ip = args.server_ip
    output = args.output

    start_requests(sleep_time_min, sleep_time_max, server_ip, output)
