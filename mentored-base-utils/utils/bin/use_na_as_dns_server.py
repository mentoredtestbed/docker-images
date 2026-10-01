#!/usr/bin/env python3

# Use mentored-get-ip.py to get the IP address of the node actor to use as a DNS server
import subprocess
import json
import sys

def get_dns_ip(node_actor_name):
    # Get the IP address of the node actor to use as a DNS server
    result = subprocess.run(["mentored-get-ip.py", "--na-regex", node_actor_name], stdout=subprocess.PIPE)
    ip_data = result.stdout.decode("utf-8").strip().split("\n")
    return ip_data[0]

def update_resolv_conf(dns_ip):
    # Update the /etc/resolv.conf file to use the specified DNS server
    with open("/etc/resolv.conf", "w") as resolv_conf:
        resolv_conf.write(f"nameserver {dns_ip}\n")
        print(f"Updated /etc/resolv.conf to use DNS server {dns_ip}")


# TODO: Check if we are setting ourself as the DNS provider
def are_we_using_ourselves_as_dns(ip_data, na):
    return False

if __name__ == "__main__":

    # Get NA from argument and get the IP address of the node actor to use as a DNS server
    na = sys.argv[1]
    ip_data = get_dns_ip(na)
    are_we_using_ourselves_as_dns = are_we_using_ourselves_as_dns(ip_data, na)
    if are_we_using_ourselves_as_dns:
        print("We are using ourselves as the DNS server... this is probably not what you want.")
    else:
        update_resolv_conf(ip_data)