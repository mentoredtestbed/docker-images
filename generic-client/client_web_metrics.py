#!/usr/bin/python3
import time
import numpy as np
import argparse
import os
import random
import httpx  # Add httpx for HTTP/2 support
import sys
import netifaces as ni
import json

agents = [
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko)',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)',
    'Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)',

    # Linux users
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) AppleWebKit/537.36 (KHTML, like Gecko)',
    'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:61.0) AppleWebKit/537.36 (KHTML, like Gecko)',
    'Mozilla/5.0 (X11; Gentoo; Linux x86_64; rv:61.0) AppleWebKit/537.36 (KHTML, like Gecko)',
]

headers = {"User-Agent":random.choice(agents)}

route_list = [
    '/',
    '/index',
    '/about',
    '/home',
    '/dashboard',
    '/profile',
    '/settings',
    '/api/v1',
    '/api/v1/data',
]

def get_env_var(name, default):
    return os.environ[name] if name in os.environ else default

def my_ip():
    # Get IP for interface name net1
    return ni.ifaddresses('net1')[ni.AF_INET][0]['addr']
    
def get_replica_id():
    my_name=os.environ.get('HOSTNAME', None)
    # Open /MENTORED_IP_LIST.json file
    with open('/MENTORED_IP_LIST.json') as f:
        ip_list = json.load(f)

        for actor in ip_list:
            for replica_id, ip, mask, iname in enumerate(actor['ips']):
                if ip == my_ip():
                    return replica_id

    return 0

def create_random_route():
    # 15% chance of returning a static media file
    if random.random() < 0.15:
        if random.random() > 0.8:
            fname = random.choice([
                "logo.png",
                "background.jpg",
                "icon.ico",
                "style.css",
                "script.js",
            ])
            expected_size = np.random.exponential(2**14) # Average close to 16kb
        else:
            fname = f"file_{random.randint(1, 1000)}" + random.choice([
                ".mp4",
                ".pdf",
                ".zip",
                ".tar",
                ".gz",
                ".csv",
            ])
            expected_size = np.random.exponential(2**20) # Average close to 1MB

        return f'/static/{fname}', expected_size

    r = random.choice(route_list)
    expected_size = np.random.exponential(2**15) # Average close to 30kb
    if r == '/api/v1/data':
        r += random.choice([
            "/users",
            "/products",
            "/orders",
            "/invoices",
            "/payments",
            "/transactions",
        ])

        expected_size = np.random.exponential(2**17) # Average close to 130kb

        if random.random() > 0.5:
            r += f"/{random.randint(1, 1000)}"
            expected_size = np.random.exponential(2**18) # Average close to 260kb


    return r, expected_size

def start_requests(
        sleep_time_min,
        sleep_time_max,
        server_ip,
        output,
        silent,
        static_behavior,
        http2=False,
        ignore_tls=False
        ):
    # Ensure that directory exists (recursive)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    # if the output is a directory, append the file name
    if os.path.isdir(output):
        output = os.path.join(output, "client_delay.csv")

    with open(output, 'a') as f:
        f.write("time,delay (seconds)")
        f.write("\n")

    t_init_server = time.time()

    client = httpx.Client(http2=http2, verify=not ignore_tls)
    print(f"{time.time() - t_init_server:.3f} seconds to create client")
    schema = "http://"

    if http2: # Most servers use HTTPS for HTTP/2
        schema = "https://"

    while True:
        t_init = time.time()
        get_params = {}
        
        t_init_step = time.time()
        if not static_behavior:
            random_route, expected_size = create_random_route()
            route = f'{schema}{server_ip}' + random_route
            if random.random() > 0.5:
                get_params['min_words'] = 1
                # Exponential probability considering max = 2**30 (1 GB)
                get_params['max_words'] = int(expected_size)
                route += "?" + "&".join([f"{k}={v}" for k, v in get_params.items()])
        else:
            route = f'{schema}{server_ip}/'
        print(f"{time.time() - t_init_step:.3f} seconds to generate route")

        # if not silent:
        print(f"GET {route}")

        try:
            t_init_step = time.time()
            response = client.get(route, headers=headers)
            print(f"{time.time() - t_init_step:.3f} seconds to make request")
            sys.stdout.flush()
            data = response.text

            time_delay = time.time() - t_init

            stat = "{},{:.3f},{}".format(
                time.time() - t_init_server,
                time_delay,
                t_init)

            if not silent:
                print(stat)

            with open(output, 'a') as f:
                f.write(stat)
                f.write("\n")
                f.flush()

        except Exception as e:
            if not silent:
                print(f"An error occurred: {e}")
                with open(output, 'a') as f:
                    f.write("{},ERROR:{}".format(time.time() - t_init_server, str(e)))
                    f.write("\n")
                    f.flush()
        # Flush stdout
        sys.stdout.flush()
        time.sleep(np.random.uniform(sleep_time_min, sleep_time_max))

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("-smin", "--sleep_time_min", help="Minimum sleep time", default=0.1, type=float)
    args.add_argument("-smax", "--sleep_time_max", help="Maximum sleep time", default=0.5, type=float)
    args.add_argument("-ip", "--server_ip", help="Server IP", default="localhost", type=str)
    args.add_argument("-o", "--output", help="Output file", default="/client_delay.csv")
    args.add_argument("-s", "--silent", help="Silent mode", action="store_true")
    args.add_argument('--static_behavior', action='store_true', help='Static behavior (no randomization)')
    args.add_argument("--http2", action="store_true", help="Enable HTTP/2 support", default=False)
    args.add_argument("--ignore-tls", action="store_true", help="Ignore TLS certificate validation")

    args = args.parse_args()

    start_requests(
        args.sleep_time_min,
        args.sleep_time_max,
        args.server_ip,
        args.output,
        args.silent,
        args.static_behavior,
        args.http2,
        args.ignore_tls
    )
