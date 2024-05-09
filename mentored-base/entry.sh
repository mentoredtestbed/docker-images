#!/bin/bash

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

wondershaper $NET_INTERFACE $INGRESS_KBS $EGRESS_KBS

while [ ! -f /MENTORED_READY ];
do
sleep 1;
done

sleep 1


if [[ -f "/MENTORED_IP_LIST.json" ]]
then
    #TODO: Dynamic Node Actor name, interface name, and var NAME
    python3 /create_env_from_mentored_ip_list.py /MENTORED_IP_LIST.json na-server $MENTORED_EXP_IFNAME SERVER /MENTORED_ENV.source
    source /MENTORED_ENV.source
fi

if [ "$ADD_SERVER_IP_TO_COMMAND" == "no" ]; then
    SERVER=""
fi

# WAIT_FOR_TIME is the content of /MENTORED_READY
WAIT_FOR_TIME=$(cat /MENTORED_READY)

# While the current date time is smaller than WAIT_FOR_TIME (timestamp)
while [ $(date +%s) -lt $WAIT_FOR_TIME ]; do
    sleep 1
done

sleep $TIME_WAIT_START

if [ "$TIMEOUT_CMD" -gt 0 ]; then
    CMD="$@ $SERVER"
    echo "$CMD"
    timeout $TIMEOUT_CMD $CMD
    tail -f /dev/null
else
    eval "$@ $SERVER"
fi
