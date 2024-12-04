from datetime import datetime
from netmiko.exceptions import  NetMikoTimeoutException
import os
import netmiko
import json
import threading
import time
import difflib
import sys
import signal
import re
import os
import argparse
import msvcrt
import queue
"""
History
  2023/04/19 adding save_config for cisco_xe or cisco_nxos
  2023/04/25 adding print success 
  2023/04/26 adding excption and output each module result to file 
  2023/04/29 adding excption msg  result to file 
  2024/07/27 adding print command name to showlog file
  2024/08/05 adding -D option for dry run and change log file name
  2024/08/07 delete unnecessary comments
  2024/08/09 adding follwing function
             (1) change comment and TOD expression to western style
             (2) in the befgging wait for 5 second to proceed the processFA value handling and job caller log file name
                 in any char input , process has exited.
             (3) FA value handling and job caller log file name
             sys.exit call sooner thay expected
  2024/08/20  adding error handling for send_config_set()
  2024/09/06 adding "ip" key  to JSON file and support cli file name both IP and host
  2024/11/11 adding "session_log" keyword in Jason
 
"""

###############################################################
# get running-configurtaion
# @param conn netmiko class 
# @param dir  output directory 
# @param file output file
###############################################################
def getconf(conn,dir,file):
  text = conn.send_command('show running-config')
  text_list = text.splitlines()
  text_list = text_list[3:-1]
  text =  '\n'.join(text_list)
    
  with  open(f'{dir}/{file}','w') as fd:
    fd.write(text)

###############################################################
# compare old configurarion with new configurati\on and create diff 
# 
# @param old configuration file for before change
# @param new configurarion file for latese
# @param dir directiory for output
# @param html file name for output
###############################################################
def compconf(old,new,dir,html):
  with open(f'{dir}/{old}', 'r') as oldfile:
    with open(f'{dir}/{new}', 'r') as newfile:
      # Make diff
      diff = difflib.HtmlDiff()
      with open(f'{dir}/{html}','w') as difffile:
        output = difffile 
        output.writelines(diff.make_file(oldfile,newfile))
###############################################################
# connect target network device and issuing commands
# @param jason file for network device information 
###############################################################
def cisco(device,q):
  try:
    global rc
    rc=0
    msg=''
    ip_key="None"
    now = datetime.now()
    timestr = now.strftime('%m-%d-%Y-%H-%M')
    if  "ip" in device  and "host" in device:
       print(f'Connect with IP {device["ip"]}')
       backup_dir = f'logs_{timestr}/{device["host"]}'
       bk_file_name_org = f'{device["ip"]}_{device["host"]}_{now.year}{now.month}{now.day}_org.conf'
       bk_file_name_new = f'{device["ip"]}_{device["host"]}_{now.year}{now.month}{now.day}_new.conf'
       cli_file_name = f'{device["ip"]}_config.txt'
       html_file_name = f'{device["ip"]}_{device["host"]}_{now.year}{now.month}{now.day}_diff.html'
       ip_key="Both"
    elif "ip" in device and "host" not in device :
      backup_dir = f'logs_{timestr}/{device["ip"]}'
      bk_file_name_org = f'{device["ip"]}_{now.year}{now.month}{now.day}_org.conf'
      bk_file_name_new = f'{device["ip"]}_{now.year}{now.month}{now.day}_new.conf'
      cli_file_name = f'{device["ip"]}_config.txt'
      html_file_name = f'{device["ip"]}_{now.year}{now.month}{now.day}_diff.html'
      ip_key="ip"
      print(f'Connect with IP {device["ip"]}')
    elif "host" in device : 
      backup_dir = f'logs_{timestr}/{device["host"]}'
      bk_file_name_org = f'{device["host"]}_{now.year}{now.month}{now.day}_org.conf'
      bk_file_name_new = f'{device["host"]}_{now.year}{now.month}{now.day}_new.conf'
      cli_file_name = f'{device["host"]}_config.txt'
      html_file_name = f'{device["host"]}_{now.year}{now.month}{now.day}_diff.html'
      ip_key="host"
      print(f'Connect with Host {device["host"]}')

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    if "session_log" in device :
      sesslog=device["session_log"]
      sesslog=f'{backup_dir}/{sesslog}'
      device["session_log"]=sesslog

    connection = netmiko.ConnectHandler(**device)
    connection.enable()
    print(f'Connected')
#
#08/20
    err_char_nx="Invalid command"
    err_char_ios="^% Invalid"
    err_char_f5="[0-9a-zA-Z ]*[:]"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # get current config 
    getconf(connection,backup_dir,bk_file_name_org)
      
    # excuting conf t and adding configuration text from the file
    #
    ### 09/09
#
    is_file=os.path.exists(cli_file_name)
    if is_file :
      print(f'Config file name : {cli_file_name}')
    else :
      print("conf file not exist")
###
    with open(f'{cli_file_name}','r') as conf:
      commands =[]
      DEVTYPE=device["device_type"]
      # process for  cisco fire-power
 
      for cli in conf:
        text = cli.strip("\n")
        commands.append(text)      
#
### 08/20
      if deb=="Off" :
          if DEVTYPE =="f5_tmsh" :
            output = connection.send_config_set(commands,error_pattern=err_char_f5)
          elif DEVTYPE =="cisco_nxos" :
            output = connection.send_config_set(commands,error_pattern=err_char_nx)
          else :
            output = connection.send_config_set(commands,error_pattern=err_char_ios)
#          print(output)

    # excutiong show commannd to get current status
#
### 09/06
      if ip_key == "Both" or ip_key == "ip" :
        cli_file_name = f'{device["ip"]}_show.txt'
      elif  ip_key == "host" :
        cli_file_name = f'{device["host"]}_show.txt'
#
      is_file=os.path.exists(cli_file_name)

      if is_file :
        print(f'show file name : {cli_file_name}')
        if ip_key == "Both" :
          log_file_name = f'{device["ip"]}_{device["host"]}_{now.year}{now.month}{now.day}_log.txt'
          
        elif ip_key == "host" :  
          log_file_name = f'{device["host"]}_{now.year}{now.month}{now.day}_log.txt' 
        else :
         log_file_name = f'{device["ip"]}_{now.year}{now.month}{now.day}_log.txt'
###
      else :
        print("show  file not exist")

    with open(f'{backup_dir}/{log_file_name}', 'w') as logfd:
      with open(f'{cli_file_name}','r') as show:     
        for cli in show:
          commands = cli
          output = connection.send_command_timing(
                    command_string=commands,
                    strip_command=False,
                    strip_prompt=False,
                    read_timeout=20)

          logfd.write(output)
          msg = output
             
    # get lateset configuration
 
    getconf(connection,backup_dir,bk_file_name_new)

    DEVTYPE=device["device_type"]   
    # issued copy run startup in case of cisco devies
    if deb == "Off":
      if DEVTYPE=="cisco_xe" or DEVTYPE=="cisco_nxos"  or DEVTYPE=="cisco_ios" :
        connection.save_config()

    # close  connection to device 
    connection.disconnect() 
#
### 09/06
    if ip_key=="Both" or ip_key=="ip" :
        print(f'Disconnect {device["ip"]}')
        host=device["ip"]
    else : 
        print(f'Disconnect {device["host"]}')
        host=device["host"]
###
    rc=0
    

    # write diff file in html format
    compconf(bk_file_name_org,bk_file_name_new,backup_dir,html_file_name)
    q.put(0)
    
    q.put(host)
    
  
  # exception handling
  except Exception as e:
    print("** fail **",e)
    errmsg=(str(e.args))
    q.put(99)
    q.put(errmsg)
    
    


###############################################################
# Main
###############################################################

if __name__ == "__main__":
#
# prologue
#
  # if -d option specifed, only run show txt file record
  parser = argparse.ArgumentParser(description='Get dry_run option exist or not')
  parser.add_argument('-d','--dryrun',help='show command only',action="store_true")
  parser.add_argument('-j','--json', help='name of json file',default='target_device_info.json')
#  parser.add_argument('-l','--logs', help='name of logs file',default='backup')
  args = parser.parse_args()
  if args.dryrun:
    deb = 'On'
    print("*** Note dryrun specified ***")
    print("*** show command only execution ***")
  else :
    deb = 'Off'
#
## 09/04
    
  json_fn=args.json
  print(f'json file name: {json_fn}')
  # get current dir name
  script_dir = os.path.dirname(__file__) + "\\"
  path = script_dir.split("\\")
#print(path,len(path))
  
  # move to path direcorty confirm running env
  os.chdir(script_dir)
  #
  FLG=0
  now = datetime.now()
  valid_file_name =f'{now.strftime("%Y-%m-%d")}_result.txt'
  print("running dir:",script_dir)
  if FLG !=0 :
    with open(f'{valid_file_name}', 'a+') as resultfile:
      WORD="Stopped by operator"
      resultfile.write(WORD+"\n")
      sys.exit(1)
      
  # issue commands accroding to json file record order
  with open(f'{json_fn}', "r") as f:
    device_info_list = json.load(f)
    threads = list()
    q1=queue.Queue()
    for info in device_info_list:
      rc=0
      thread = threading.Thread(target=cisco, args=([info,q1]))
      threads.append(thread)
      sta=list()

  if "host" in info  and "ip" in info :
    HOST=f'host : {info["ip"]}_{info["host"]}'
  elif "ip" in info and "host" not in info :
    HOST=f'host : {info["ip"]}'
  else : 
    HOST=f'host : {info["host"]}'
    
  for th in threads:
    print("start process",HOST)
    th.start()

  q1.join()
  for th in threads:
    th.join()
#   
#  q1.join()
#  
  while not q1.empty():
    RC=q1.get()
    print("RC :",RC)
    MSG=q1.get()
    Module_type="Network"
    timestr = now.strftime('%m-%d-%Y-%H-%M')
# write process compliton status
    with open(f'{valid_file_name}', 'a+') as resultfile:
      if RC==0:
        WORD="success"
        WORD1=timestr+" "+MSG
        resultfile.write(WORD1 + '\n')
      else:
        WORD="failed"
        resultfile.write(WORD + '\n')
        WORD2=timestr+"last command: "+MSG
        resultfile.write(WORD2 + '\n')
        FLG=1

      resultfile.write(now.strftime("%b %d %H:%M:%S") + " Session has ended \n")
#


