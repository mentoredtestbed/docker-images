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
# STEP 3: MENTORED IP & ENVIRONMENT SOURCE SETUP
# ==============================================================================
if [[ -f "/MENTORED_IP_LIST.json" ]]
then
    python3 /create_env_from_mentored_ip_list.py /MENTORED_IP_LIST.json $SERVER_NA_NAME $MENTORED_EXP_IFNAME SERVER /MENTORED_ENV.source

    if [ -z "$MENTORED_DNS" ] || [ "$MENTORED_DNS" == "/etc/hosts" ]; then
        echo "MENTORED_DNS is not set or set to /etc/hosts, setting up /etc/hosts"
        setup_etc_hosts.py
    elif [ "$MENTORED_DNS" == "pod-dns" ]; then
        echo "MENTORED_DNS is set to pod-dns, using MENTORED_DNS_NA as the DNS server..."
        use_na_as_dns_server.py $MENTORED_DNS_NA
    fi

    if [ ! -f /MENTORED_ENV.source ]; then
        touch /MENTORED_ENV.source
    fi

    source /MENTORED_ENV.source
    echo "source /MENTORED_ENV.source" >> /root/.bashrc

    python3 /ping_other_ips.py /MENTORED_IP_LIST.json $MENTORED_EXP_IFNAME
fi
# ==============================================================================
# STEP 2: CREATE VXLAN OVERLAY NETWORK (Now that DNS & Pods are Ready)
# ==============================================================================
if [ -n "$MENTORED_TOPOLOGY_CONFIG" ]; then
    echo "[VXLAN Setup] All pods ready. Starting VXLAN setup from MENTORED_TOPOLOGY_CONFIG..."
    python3 -c "
import os, json, time, socket, subprocess

config_raw = os.environ.get('MENTORED_TOPOLOGY_CONFIG', '{}')
try:
    config = json.loads(config_raw)
    ifname = config.get('interface', os.environ.get('MENTORED_EXP_IFNAME', 'net1'))
    vni = config.get('vni', 200)
    ip = config.get('ip')
    remote_host = config.get('remote_host') or config.get('remote_ip')
    mtu = config.get('mtu', 1280)
    underlay_dev = 'eth0'
    dstport = '9999'

    if not remote_host:
        print('[VXLAN Setup] Error: remote_host (or remote_ip) is required!', flush=True)
    else:
        remote_ip = None
        # Set a 5-second timeout on socket operations so gethostbyname does not hang indefinitely
        socket.setdefaulttimeout(5.0)

        print(f'[VXLAN Setup] Resolving IP for remote host: {remote_host}...', flush=True)
        for attempt in range(30):
            try:
                remote_ip = socket.gethostbyname(remote_host)
                print(f'[VXLAN Setup] Successfully resolved {remote_host} -> {remote_ip}', flush=True)
                break
            except (socket.gaierror, socket.timeout) as err:
                print(f'[VXLAN Setup] DNS attempt {attempt+1}/30 failed for {remote_host}: {err}', flush=True)
                time.sleep(2)

        if not remote_ip:
            raise RuntimeError(f'Could not resolve DNS for remote host: {remote_host}')

        # Reset timeout back to default
        socket.setdefaulttimeout(None)

        # Check if interface already exists
        res = subprocess.run(['ip', 'link', 'show', ifname], capture_output=True)
        if res.returncode != 0:
            print(f'[VXLAN Setup] Creating VXLAN interface {ifname} (VNI: {vni}, Remote: {remote_ip}, Dev: {underlay_dev}, Port: {dstport})', flush=True)
            cmd_create = [
                'ip', 'link', 'add', ifname,
                'type', 'vxlan',
                'id', str(vni),
                'remote', remote_ip,
                'dev', underlay_dev,
                'dstport', dstport
            ]
            subprocess.run(cmd_create, check=True)

        # Assign overlay IP address
        if ip:
            print(f'[VXLAN Setup] Assigning IP {ip} to interface {ifname}', flush=True)
            subprocess.run(['ip', 'addr', 'add', ip, 'dev', ifname], check=False)

        # Set MTU & Bring Up
        print(f'[VXLAN Setup] Bringing up {ifname} with MTU {mtu}', flush=True)
        subprocess.run(['ip', 'link', 'set', 'dev', ifname, 'mtu', str(mtu)], check=False)
        subprocess.run(['ip', 'link', 'set', 'dev', ifname, 'up'], check=True)

except Exception as e:
    print(f'[VXLAN Setup] ERROR: Failed to configure VXLAN overlay: {e}', flush=True)
"
fi
# ==============================================================================
# STEP 4: TIMED BENCHMARK EXECUTION
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