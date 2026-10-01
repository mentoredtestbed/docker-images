#!/usr/bin/env bash
set -e

RESULTS_DIR="${RESULTS_DIR:-/app/results}"
mkdir -p "$RESULTS_DIR"

# Start ulogd daemon if ulogd2 is installed
if command -v ulogd >/dev/null 2>&1; then
    echo "[MONITORING] Starting ulogd2..."
    ulogd -d
fi

if command -v mentored-registry-action >/dev/null 2>&1; then
    mentored-registry-action -a iptables-config -o "$RESULTS_DIR" -n "Configuring IPTables"
fi

# Evaluate custom rules passed via IPTABLES_RULES environment variable
if [ -n "$IPTABLES_RULES" ]; then
    echo "[MONITORING] Applying custom IPTABLES_RULES..."
    eval "$IPTABLES_RULES"
else
    # Default NFLOG logging rules for unallowed traffic
    echo "[MONITORING] Applying default iptables/NFLOG rules..."
    iptables -A INPUT -p tcp -i net1 -m multiport ! --dports 22,80,443 -j NFLOG --nflog-prefix "[TCP-NOT-HTTP-SSH]:" --nflog-group 1 || true
    iptables -A INPUT -p udp -i net1 -m multiport ! --dports 22,80,443 -j NFLOG --nflog-prefix "[UDP-NOT-HTTP-SSH]:" --nflog-group 1 || true
    iptables -A INPUT -i net1 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT || true
    ip6tables -A INPUT -i net1 -p icmpv6 -j ACCEPT || true
fi