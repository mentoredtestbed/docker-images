#!/bin/bash

# Check if $1 and $2 are defined, otherwise abort
if [ -z "$1" ] || [ -z "$2" ]
then
    echo "Usage: $0 <target> <iname> [wait_time]"
    exit 1
fi

target=$1
iname=$2

# if $3 is defined, then use it as the wait time
if [ -z "$3" ]
then
    wait_time=60
else
    wait_time=$3
fi

echo "Executing nmap ping-wait-scan.sh with target=$target, iname=$iname, wait_time=$wait_time"

echo "Running simple ping scan..."
mentored-attack nmap $target $iname -sn --send-ip -v

sleep $wait_time

echo "Running full scan..."
mentored-attack nmap $target $iname -Pn --send-ip -v

tail -f /dev/null