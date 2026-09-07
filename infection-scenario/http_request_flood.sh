#!/bin/bash

mode=$1
target=$2
iname=$3
total_time=$4
attack_args=${@:5}

registry_base=(-a "attack-$mode"
               -o "/app/results/"
               -n "Starting attack $mode on $target using $attack_args")

registry_base_end=(-a "attack-stop-$mode"
               -o "/app/results/"
               -n "Stopping attack $mode on $target using $attack_args")


target_list=$(mentored-get-ip --na-regex $target --iname $iname)

port=80
for ip in $target_list
do
    mentored-registry-action "${registry_base[@]}" --destination_ports $port -t $ip
    # timeout $total_time hping3 $attack_args $ip
    timeout $total_time python3 /http_request_flood.py --server_ip $ip $attack_args
    mentored-registry-action "${registry_base_end[@]}" -t $ip
done