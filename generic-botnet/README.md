# Generic Botnet Docker Image

A versatile botnet simulation image supporting multiple attack types for testing network security defenses and intrusion detection systems.

## Purpose

This image provides a collection of networking attack tools that can be used to:
- Simulate botnet behavior in controlled test environments
- Test IDS/IPS systems against various attack patterns
- Demonstrate network security vulnerabilities
- Practice incident response and threat hunting techniques

## Available Tools

| Tool | Purpose |
|------|---------|
| `nmap` | Network discovery, port scanning, and service enumeration |
| `nikto` | Web server vulnerability scanner |
| `hping3` | TCP/UDP packet manipulation and crafting |
| `slowloris` | HTTP slow-rate denial-of-service attack |
| `rapidresetclient` | HTTP/3 RapidReset denial-of-service tool |

## Usage

### Via mentored-attack Utility

The image includes the `mentored-attack` utility which provides a standardized interface for launching attacks with registry tracking:

```bash
# Nmap scan
mentored-attack nmap <target> <node_name> <duration> [nmap_args]

# Nikto web scan
mentored-attack nikto <target> <node_name> <duration> [nikto_args]

# Slowloris DoS
mentored-attack slowloris <target> <node_name> <duration> <port> [args]

# hping3 attacks
mentored-attack hping3 <target> <node_name> <duration> <port> [args]

# RapidReset attack
mentored-attack rapidreset <target> <node_name> <duration> <port> [args]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `target` | Target IP, hostname, or CIDR range |
| `node_name` | Name of the attacking node (for IP list lookup) |
| `duration` | Attack duration in seconds |
| `port` | Target port (for port-specific attacks) |
| `[args]` | Additional arguments passed to the specific tool |

### Direct Tool Usage

#### Nmap

```bash
# Quick host discovery
nmap -sn 192.168.1.0/24

# Full port scan
nmap -p- 192.168.1.100

# Service version detection
nmap -sV 192.168.1.100
```

#### Nikto

```bash
# Scan a web server
nikto -host http://192.168.1.100

# Scan with specific options
nikto -host http://192.168.1.100 -e vuln -o /app/results/nikto_report.txt
```

#### hping3

```bash
# SYN flood
hping3 -S -flood -p 80 192.168.1.100

# UDP scan
hping3 -2 -p 53 192.168.1.100

# Land attack
hping3 -S --tcp-land -p 80 192.168.1.100
```

#### Slowloris

```bash
# HTTP slowloris attack
slowloris -p 80 192.168.1.100
```

#### RapidReset

```bash
# HTTP/3 RapidReset DoS
rapidresetclient -url https://192.168.1.100:443
```

## Examples

### Example 1: Network Reconnaissance

```bash
# Use mentored-attack to scan the network
mentored-attack nmap 10.10.0.0/24 botnet-node-1 60 -sV
```

### Example 2: Web Vulnerability Scanning

```bash
# Scan a target web server for vulnerabilities
mentored-attack nikto 10.10.0.50 botnet-node-1 120
```

### Example 3: DoS Attack Simulation

```bash
# HTTP Slowloris attack
mentored-attack slowloris 10.10.0.50 botnet-node-1 30 80

# hping3 SYN flood
mentored-attack hping3 10.10.0.50 botnet-node-1 30 80 --flood
```

### Example 4: Direct Tool Usage in Deployment

```yaml
# In a Kubernetes deployment
containers:
  - name: botnet-node
    image: ghcr.io/mentoredtestbed/generic-botnet:latest
    command: ["bash", "-c", "mentored-attack nmap 10.10.0.0/24 botnet-node-1 60 -sV && mentored-attack slowloris 10.10.0.50 botnet-node-1 30 80"]
```

## File Structure

```
/usr/local/bin/
├── mentored-attack          # Standardized attack launcher
├── mentored-get-ip          # IP address resolution utility
├── mentored-registry-action # Attack registry/tracking tool
├── rapidresetclient         # HTTP/3 RapidReset attack tool
└── ... (other mentored-base-utils)

/app/results/                # Attack output and results directory
```

## Registry Tracking

All attacks launched via `mentored-attack` automatically register with the mentored testbed's registry system:
- Attack start events are logged with `attack-<tool>` actions
- Attack completion events are logged with `attack-stop-<tool>` actions
- All results are saved to `/app/results/`

## Notes

- This image is designed for **controlled testing environments only**
- Always ensure you have proper authorization before running any security tests
- Attack duration is limited by the `timeout` command to prevent indefinite execution
- Results are saved to `/app/results/` for later analysis
