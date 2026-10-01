#!/bin/bash
set -x

MENTORED_EXP_IFNAME="${MENTORED_EXP_IFNAME:-net1}"
TIMEOUT_CMD="${TIMEOUT_CMD:-0}"
TIME_WAIT_START="${TIME_WAIT_START:-0}"
INGRESS_KBS="${INGRESS_KBS:-99999999}"
EGRESS_KBS="${EGRESS_KBS:-99999999}"
ADD_SERVER_IP_TO_COMMAND="${ADD_SERVER_IP_TO_COMMAND:-no}"

if [ -z "$SERVER_NA_NAME" ]; then
    echo "SERVER_NA_NAME is not set, defaulting to na-server for compatibility"
    SERVER_NA_NAME="na-server"
else
    SERVER_NA_NAME="${SERVER_NA_NAME}"
    echo "SERVER_NA_NAME is set to $SERVER_NA_NAME"
fi

if [ -z "$MENTORED_MTU" ]; then
    MENTORED_MTU=1000
fi

# Executed pre-command if specified
if [ -n "$MENTORED_PRE_CMD" ]; then
    echo "MENTORED_PRE_CMD is set, executing it in the background"
    eval "$MENTORED_PRE_CMD" &
fi

# 1. Modular Packet Capture Trigger
if [ "${ENABLE_CAPTURE:-false}" = "true" ]; then
    /usr/local/bin/start-capture.sh
fi

# 2. Modular Firewall / IPTables Logging Trigger
if [ "${ENABLE_IPTABLES_LOGGING:-false}" = "true" ]; then
    /usr/local/bin/configure-iptables.sh
fi

# ==============================================================================
# STEP 1: WAIT FOR ALL PODS TO BE READY
# ==============================================================================
while [ ! -f /MENTORED_READY ]; do
    sleep 1
done
sync
sleep 1

mkdir -p /app/results
cp /MENTORED_READY /app/results/MENTORED_READY
[ -f /MENTORED_IP_LIST.json ] && cp /MENTORED_IP_LIST.json /app/results/MENTORED_IP_LIST.json
[ -f /MENTORED_IP_LIST.yaml ] && cp /MENTORED_IP_LIST.yaml /app/results/MENTORED_IP_LIST.yaml
[ -f /MENTORED_ENV.source ] && cp /MENTORED_ENV.source /app/results/MENTORED_ENV.source

# ==============================================================================
# STEP 2: MENTORED IP & ENVIRONMENT SOURCE SETUP
# ==============================================================================
if [[ -f "/MENTORED_IP_LIST.json" ]]
then
    python3 /usr/local/bin/create_env_from_mentored_ip_list.py /MENTORED_IP_LIST.json $SERVER_NA_NAME $MENTORED_EXP_IFNAME SERVER /MENTORED_ENV.source

    if [ -z "$MENTORED_DNS" ] || [ "$MENTORED_DNS" == "/etc/hosts" ]; then
        echo "MENTORED_DNS is not set or set to /etc/hosts, setting up /etc/hosts"
        /usr/local/bin/setup_etc_hosts.py
    elif [ "$MENTORED_DNS" == "pod-dns" ]; then
        echo "MENTORED_DNS is set to pod-dns, using MENTORED_DNS_NA as the DNS server..."
        /usr/local/bin/use_na_as_dns_server.py $MENTORED_DNS_NA
    fi

    if [ ! -f /MENTORED_ENV.source ]; then
        touch /MENTORED_ENV.source
    fi

    source /MENTORED_ENV.source
    echo "source /MENTORED_ENV.source" >> /root/.bashrc

    python3 /usr/local/bin/ping_other_ips.py /MENTORED_IP_LIST.json $MENTORED_EXP_IFNAME
fi
# ==============================================================================
# STEP 3: CREATE VXLAN OVERLAY NETWORK (Now that DNS & Pods are Ready)
# ==============================================================================
if [ -n "$MENTORED_TOPOLOGY_CONFIG" ]; then
    echo "[Topology Setup] Executing setup-topology.py..."
    python3 /usr/local/bin/setup-topology.py
fi

# ==============================================================================
# STEP 4: CONFIGURE & BOOTSTRAP FRR ROUTING DAEMONS
# ==============================================================================
if [ -n "$FRR_CONF_CONTENT" ]; then
    echo "[FRR Setup] Enabling daemons..."
    sed -i 's/bgpd=no/bgpd=yes/' /etc/frr/daemons
    sed -i 's/zebra=no/zebra=yes/' /etc/frr/daemons

    echo "[FRR Setup] Writing /etc/frr/frr.conf..."
    echo "$FRR_CONF_CONTENT" > /etc/frr/frr.conf

    # Fix ownership and socket directory permissions
    mkdir -p /var/run/frr /var/log/frr
    chown -R frr:frr /etc/frr /var/run/frr /var/log/frr
    chmod 640 /etc/frr/frr.conf

    # Clean up lingering lockfiles if present
    rm -f /run/frr/*.pid /var/run/frr/*.pid

    echo "[FRR Setup] Starting FRR daemon service..."
    /usr/lib/frr/frrinit.sh start
fi

# ==============================================================================
# STEP 5: TIMED BENCHMARK EXECUTION
# ==============================================================================
WAIT_FOR_TIME=$(cat /MENTORED_READY)

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

if [ -z "$KILL_POD_AFTER_COMMAND" ] || [ "$KILL_POD_AFTER_COMMAND" == "false" ]; then
    echo "KILL_POD_AFTER_COMMAND is not set or set to false, sleeping forever to keep container alive"
    sleep infinity
else
    echo "KILL_POD_AFTER_COMMAND is set to true, exiting"
    exit 0
fi