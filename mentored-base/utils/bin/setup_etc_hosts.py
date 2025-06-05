#!/usr/bin/env python3

import json

def update_hosts(json_path, hosts_path="/etc/hosts"):
    try:
        with open(json_path, 'r') as f:
            ip_data = json.load(f)

        with open(hosts_path, 'a') as hosts_file:
            for hostname, entries in ip_data.items():
                # Get the number of the current iteration
                replica=0
                for entry in entries:
                    ip_address = entry[0][0]
                    if replica == 0:
                        hosts_file.write(f"{ip_address} {hostname}\n")
                        print(f"Added {ip_address} {hostname} to {hosts_path}")    
                    hosts_file.write(f"{ip_address} {hostname}-{replica}\n")
                    print(f"Added {ip_address} {hostname}-{replica} to {hosts_path}")
                    replica+=1

    except PermissionError:
        print("Permission denied. Run the script with superuser privileges.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    update_hosts("/MENTORED_IP_LIST.json")
