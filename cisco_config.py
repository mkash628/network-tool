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
#
#  History
#  2023/04/19 adding save_config for cisco_xe or cisco_nxos
#  2023/04/25 adding print success 
#  2023/04/26 adding excption and output to  result to the log file for notice to caller 
#  2023/04/29 adding excption msg  result to file 
#
def getconf(conn,dir,file):
#    print(f'Dir :{dir} File name :{file}')
    text = conn.send_command('show running-config')
    text_list = text.splitlines()
    text_list = text_list[3:-1]
    text =  '\n'.join(text_list)
    
    with  open(f'{dir}/{file}','w') as fd :
      fd.write(text)

def compconf(old,new,dir,html):
    with open(f'{dir}/{old}', 'r') as file1:
      with open(f'{dir}/{new}', 'r') as file2:
  
        diff = difflib.HtmlDiff()
#
        with open(f'{dir}/{html}','w') as file3:
          output = file3 
          output.writelines(diff.make_file(file1,file2))
#
    
def cisco(device):
  try:
  
    result=0
    msg=''
    print(f'Connect {device["host"]}')
    connection = netmiko.ConnectHandler(**device)
    connection.enable()

#

    now = datetime.now()
    backup_dir = f'backup/{device["host"]}'
    bk_file_name = f'{device["host"]}_{now.year}{now.month}{now.day}_org.conf'
#    print(f'File name :{bk_file_name}')
#
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
#
# Take current Config
#
    getconf(connection,backup_dir,bk_file_name)
#
          
# config change 
    cli_file_name = f'{device["host"]}_config.txt'
#    print (cli_file_name)
    with open(f'{cli_file_name}','r') as conf:

     commands =[]
     
     DEVTYPE=device["device_type"]

#     print(DEVTYPE)

     if DEVTYPE=="cisco_ftd" :
       for cli in conf:
         commands = cli
#         print(f'{device["host"]} {commands}') 
#        output = connection.send_command(commands)
         output = connection.send_command(command_string=commands,expect_string=r"#")
#         print (output)
     else :
       for cli in conf:
         text = cli.strip("\n")
         commands.append(text)
      
#       print(f'{device["host"]} {commands}')     
       output = connection.send_config_set(commands)
#       print (output)

    
# confirm configuration chage
    cli_file_name = f'{device["host"]}_show.txt'
#    print (cli_file_name)
    log_file_name = f'{device["host"]}_{now.year}{now.month}{now.day}_log.txt'
 
#    print (log_file_name)
    
    with open(f'{backup_dir}/{log_file_name}', 'w') as logfd: 
      with open(f'{cli_file_name}','r') as show:
#       DEVTYPE=device["device_type"]
#       if DEVTYPE=="cisco_ftd" :
        
         for cli in show:
           commands = cli

#        output = connection.send_command(commands)
#          print({commands},DEVTYPE) 
           if DEVTYPE=="cisco_ftd" and commands=="exit" :
#            print(commands,DEVTYPE) 
             output = connection.send_command(command_string=commands,expect_string=r">")
           else :
#             print(f'{device["host"]} {commands}') 
             output = connection.send_command(command_string=commands,expect_string=r"#")
#           print (output)
           logfd.write(output)
           msg=output
             
#
        
# Take new configuration 

    bk_file_name_new = f'{device["host"]}_{now.year}{now.month}{now.day}_new.conf'
#    print(f'File name :{bk_file_name_new}')
#

    getconf(connection,backup_dir,bk_file_name_new)
#
#    with open(f'{backup_dir}/{bk_file_name_new}', 'w') as f:
#        f.write(output)

    DEV=device["device_type"]
    

    if DEV=="cisco_xe"  or DEV=="cisco_nxos" :
        connection.save_config()
#
#     
#   
    connection.disconnect() 
    print(f'Disconnect {device["host"]}')

#
    html_file_name = f'{device["host"]}_{now.year}{now.month}{now.day}_diff.html'
    compconf(bk_file_name,bk_file_name_new,backup_dir,html_file_name)
    errmsg=msg
    return 0,errmsg
#
  except   Exception as e:
    print("** fail **",e)


    errmsg=(str(e.args))
#   print(e.message)
    return 99,errmsg

#   sys.exit


if __name__ == "__main__":


     now = datetime.now()
     valid_file_name =f'{now.year}{now.month}{now.day}_result.txt'
     TIME=f' {now.hour}:{now.minute}:{now.second} '
     Module_type="Network"
     timestr = time.strftime("%d-%m-%Y-%H-%M")
     log_file_name= "F:\\DRScripts\\ScriptLogs\\1\\"+Module_type + timestr+".log"
#     log_file_name= Module_type + timestr+".log"
# 
     with open(r"target_device_info.json", "r") as f:
         device_info_list = json.load(f)
       
     threads = list()
     for info in device_info_list:
        HOST=f'host : {info["host"]}'
        rc=0
        msg=""

        sta=list()
        sta, msg = cisco(info)

        FLG=0

#        print("return coode:",sta)
#        print("meesage:",msg)
#
        with open(f'{valid_file_name}', 'a+') as file3:
          if sta==0:
            WORD=" success "
            WORD=TIME+HOST+WORD+msg
            file3.write(WORD+'\n')
          else:
            WORD=" failed"
            WORD=TIME+HOST+WORD+msg
            file3.write(WORD+'\n')
            FLG=1
            print("fail")
            sys.exit(1)
 
     if FLG==0:
       print("success")
       f = open(log_file_name, "w")
       f.write("success"+'\n')
       f.write(time.strftime("%b %d %H:%M:%S") + " Session has ended \n")
       f.close()
       sys.exit(0)
     else:
       print("fail")
       f = open(log_file_name, "w")
       f.write("fail"+'\n')
       f.write(time.strftime("%b %d %H:%M:%S") + " Session has ended \n")
       f.close()
       sys.exit(1)

