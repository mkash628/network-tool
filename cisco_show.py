from datetime import datetime
import logging
import netmiko
from logging import getLogger, StreamHandler, Formatter
from netmiko.exceptions import  NetMikoTimeoutException
from netmiko.exceptions import  AuthenticationException
import os
import json
import threading
import time
import sys
import argparse
import re

#
#  History
#  2023/04/19 adding save_config for cisco_xe or cisco_nxos
#  2023/04/25 adding print success 
#  2023/04/26 adding excption and output each module result to file 
#  2023/04/29 adding excption msg  result to file 
#  2023/11/14 adding threading , removing config change and compare
#  2024/01/25 adding json file name as arg1 and change to send_command_timing
#  2024/02/14 change to send_command_timing and delete if statement

#
# log output function
#
def log_debug(logmsg,devName,host):
  logger = getLogger("scriptLog")
  logger.debug(f'[{devName}:{host}] {logmsg}')
  
def log_info(logmsg,devName,host):
  logger = getLogger("scriptLog")
  logger.info(f'[{devName}:{host}] {logmsg}')

#
# access and issue cli command 
#
def cisco(device,log_dir):
  try:
    
    HOST = device["host"]
    DEVTYPE = device["device_type"]
    IP = device["ip"]
    
    # Create devicename directory
    log_debug("create host directory",HOST,IP)
    device_dir = f'{log_dir}/{IP}_{HOST}'
    os.makedirs(device_dir)
    
    
    log_debug("connect",HOST,IP)
    connection = netmiko.ConnectHandler(**device)
    connection.enable()
    log_info("connected",HOST,IP)
#       
#    cli_file_name = f'{IP}_{HOST}_show.txt'
#
    cli_file_name = f'{IP}_show.txt'
 
    with open(f'{cli_file_name}','r') as show:
      for cli in show:
        commands = cli.strip("\n")
        commands_fn=commands
        pattern = "[^0-9a-zA-Z_\s\-]+"
        commands_fn=re.sub(pattern,"",commands_fn)
        print(commands_fn)
        log_file_name = f'{IP}_{HOST}({commands_fn}).log'
        with open(f'{device_dir}/{log_file_name}', 'w') as logfd:
          output = connection.send_command_timing(
                    command_string=commands,
                    strip_command=False,
                    strip_prompt=False,
                    read_timeout=20)
                 
          log_debug("command executed " + commands,HOST,IP)
          logfd.write(output)
    
    connection.disconnect()
    log_info("Disconnected",HOST,IP)

  except Exception as e:
    log_info("error",HOST,IP)
    log_debug(e,HOST,IP)
    sys.exit(1)


if __name__ == "__main__":
#
### get json file name as arg
#
  parser = argparse.ArgumentParser(description='Get informations from network device')

  parser.add_argument('-j','--json', help='name of json file',default='target_device_info.json')
  
  args = parser.parse_args()
  json_fn=args.json
  print(f'json file name: {json_fn}')
#
###
#
  logger = getLogger("scriptLog")
  # console log setting
  ch = StreamHandler()
  logger.setLevel(logging.DEBUG) # log level
  ch_formatter = Formatter('%(asctime)s:%(levelname)s:%(message)s')
  ch.setFormatter(ch_formatter)
  logger.addHandler(ch)
  
  
  script_dir = os.path.dirname(__file__) +"/" 
#
#  print(f'cuurent dir : {script_dir}')
  os.chdir(f"{script_dir}")

  print(f'cuurent dir : {script_dir}')
  
  now = datetime.now()
  currenttime = now.strftime('%Y%m%d_%H-%M-%S')
  log_dir = f'log_{currenttime}'
  
  #create log directory
  if not os.path.exists(log_dir):
    os.makedirs(log_dir)
  
  # log file setting
  path = log_dir + '/console.log'
  f = open(path, 'w')
  fh = logging.FileHandler(path)
  fh_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
  fh.setFormatter(fh_formatter)
  logger.addHandler(fh)
  
  
  
  with open(json_fn, "r") as f:
    device_info_list = json.load(f)
    logger.debug("json read finished")
  
  threads = list()
  for info in device_info_list:
    rc=0
    msg=''
    thread = threading.Thread(target=cisco, args=(info,log_dir))
    sta=list()
    threads.append(thread)

  for th in threads:
    th.start()

  for th in threads:
    th.join()
      
  print("cisco_show.py finished")
  sys.exit(0)