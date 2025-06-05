#!/bin/bash
set -x
# Set MENTORED_EXP_IFNAME env variable default value as net1
MENTORED_EXP_IFNAME="${MENTORED_EXP_IFNAME:-net1}"

# Default = 0
TIMEOUT_CMD="${TIMEOUT_CMD:-0}"

# Default = 0
TIME_WAIT_START="${TIME_WAIT_START:-0}"

# Default = 99999999
INGRESS_KBS="${INGRESS_KBS:-99999999}"

# Default = 99999999
EGRESS_KBS="${EGRESS_KBS:-99999999}"

ADD_SERVER_IP_TO_COMMAND="${ADD_SERVER_IP_TO_COMMAND:-no}"

if [ -z "$SERVER_NA_NAME" ]; then
    echo "SERVER_NA_NAME is not set, defaulting to na-server for compatibility"
    SERVER_NA_NAME="na-server"
else
    SERVER_NA_NAME="${SERVER_NA_NAME}"
    echo "SERVER_NA_NAME is set to $SERVER_NA_NAME"
fi

# wondershaper $NET_INTERFACE $INGRESS_KBS $EGRESS_KBS

# Macvlan mtu configuration
if [ -z "$MENTORED_MTU" ]; then
    echo "MENTORED_MTU is not set, defaulting to 1000"
    MENTORED_MTU=1000
else
    echo "MENTORED_MTU is set to $MENTORED_MTU"
fi
ifconfig net1 mtu $MENTORED_MTU up


# if MENTORED_PRE_CMD is set, then execute it in the background
if [ -n "$MENTORED_PRE_CMD" ]; then
    echo "MENTORED_PRE_CMD is set, executing it in the background"
    eval "$MENTORED_PRE_CMD" &
fi


while [ ! -f /MENTORED_READY ];
do
sleep 1;
done
sync
sleep 1

mkdir -p /app/results
cp /MENTORED_READY /app/results/MENTORED_READY
cp /MENTORED_IP_LIST.json /app/results/MENTORED_IP_LIST.json
cp /MENTORED_IP_LIST.yaml /app/results/MENTORED_IP_LIST.yaml
cp /MENTORED_ENV.source /app/results/MENTORED_ENV.source

if [[ -f "/MENTORED_IP_LIST.json" ]]
then
    #TODO: Dynamic Node Actor name, interface name, and var NAME
    python3 /create_env_from_mentored_ip_list.py /MENTORED_IP_LIST.json $SERVER_NA_NAME $MENTORED_EXP_IFNAME SERVER /MENTORED_ENV.source

    # if "MENTORED_DNS" is unset, or set to "/etc/hosts" then setup /etc/hosts
    if [ -z "$MENTORED_DNS" ] || [ "$MENTORED_DNS" == "/etc/hosts" ]; then
        echo "MENTORED_DNS is not set or set to /etc/hosts, setting up /etc/hosts"
        setup_etc_hosts.py
    elif [ "$MENTORED_DNS" == "pod-dns" ]; then
        echo "MENTORED_DNS is set to pod-dns, using MENTORED_DNS_NA as the DNS server..."
        use_na_as_dns_server.py $MENTORED_DNS_NA
    else
        echo "MENTORED_DNS is set to $MENTORED_DNS, which is not implemented yet, skipping..."
    fi

    # If MENTORED_ENV was not created, then create it
    if [ ! -f /MENTORED_ENV.source ]; then
        touch /MENTORED_ENV.source
    fi

    source /MENTORED_ENV.source
    echo "source /MENTORED_ENV.source" >> /root/.bashrc

    python3 /ping_other_ips.py /MENTORED_IP_LIST.json $MENTORED_EXP_IFNAME
fi

# WAIT_FOR_TIME is the content of /MENTORED_READY
WAIT_FOR_TIME=$(cat /MENTORED_READY)

# While the current date time is smaller than WAIT_FOR_TIME (timestamp)
while [ $(date +%s) -lt $WAIT_FOR_TIME ]; do
    sleep 1
done

sleep $TIME_WAIT_START

CMD_SUFFIX=$SERVER
if [ "$ADD_SERVER_IP_TO_COMMAND" == "no" ]; then
    CMD_SUFFIX=""
fi

if [ "$TIMEOUT_CMD" -gt 0 ]; then
    
    CMD="$@ $CMD_SUFFIX"
    echo "$CMD"
    timeout $TIMEOUT_CMD $CMD
else
    eval "$@ $CMD_SUFFIX"
fi

# if KILL_POD_AFTER_COMMAND is not set or set to false then sleep infinity
if [ -z "$KILL_POD_AFTER_COMMAND" ] || [ "$KILL_POD_AFTER_COMMAND" == "false" ]; then
    echo "KILL_POD_AFTER_COMMAND is not set or set to false, sleeping forever to keep container alive"
    sleep infinity
else
    echo "KILL_POD_AFTER_COMMAND is set to true, exiting"
    exit 0
fi