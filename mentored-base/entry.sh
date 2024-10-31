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
    echo "MENTORED_MTU is not set, defaulting to 1280"
    MENTORED_MTU=1280 # Minimum MTU for IPv6
else
    echo "MENTORED_MTU is set to $MENTORED_MTU"
fi
ifconfig net1 mtu $MENTORED_MTU up

while [ ! -f /MENTORED_READY ];
do
sleep 1;
done

sleep 1


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
    tail -f /dev/null
else
    eval "$@ $CMD_SUFFIX"
fi
