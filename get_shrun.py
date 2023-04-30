from datetime import datetime
from netmiko.exceptions import  NetMikoTimeoutException
import os
import netmiko
import json
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
def getconf(conn,file):
#    print(f'File name :{file}')
    text = conn.send_command('show running-config')
    text_list = text.splitlines()
    text_list = text_list[3:-1]
    text =  '\n'.join(text_list)
    
    with  open(f'{file}','w') as fd :
      fd.write(text)

    
def cisco(device):
  try:
  
    result=0
    msg=''
    print(f'Connect {device["host"]}')
    connection = netmiko.ConnectHandler(**device)
    connection.enable()

#

    now = datetime.now()
    shrun_file_name = f'{device["host"]}_{now.year}{now.month}{now.day}_shrun.conf'
#    print(f'File name :{bk_file_name}')
#

# Take current Config
#
    getconf(connection,bk_file_name)
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
     result_file_name =f'{now.year}{now.month}{now.day}_result.txt'
 
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
        with open(f'{result_file_name}', 'a+') as f1:
          if sta==0:
            WORD=" success "
            WORD=TIME+HOST+WORD+msg
            f1.write(WORD+'\n')
          else:
            WORD=" failed"
            WORD=TIME+HOST+WORD+msg
            f1.write(WORD+'\n')
            FLG=1
            print("failed")
            sys.exit(1)
 

