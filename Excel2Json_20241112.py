from datetime import datetime
from netmiko.exceptions import  NetMikoTimeoutException
import os
import json
import time
import sys
import re
import os
import argparse
import xlwings
"""
History
  2024/10/06 1st adding "ip" key  to JSON file and support cli file name both IP and host
 
"""

###############################################################
# Main
###############################################################

if __name__ == "__main__":
#
# prologue
#
  # if -d option specifed, only run show txt file record
  parser = argparse.ArgumentParser(description='Get excel file name')
# parser.add_argument('-j','--json', help='name of json file',default='target_device_info.json')
  parser.add_argument('-e','--excel', help='name of Excel file',default='device_info.xlsx')
  args = parser.parse_args()

#  json_fn=args.json
  excel_fn=args.excel
  print(f'excel file name: {excel_fn}')
  # get current dir name
  script_dir = os.path.dirname(__file__) + "\\"
  path = script_dir.split("\\")
 
  bk = xlwings.Book(excel_fn,read_only=True)
  sht = bk.sheets[0]
  sht.activate()
  for sht in bk.sheets:
    json_fn=f'{sht.name}_info.json'
#print(f'excel file name: {excel_fn}')
#   last_row = sht.range('A' + str(sht.cells.last_cell.row)).end('up').row
    last_row = sht.used_range.last_cell.row
    print(f'Num of rows: {last_row}')
#last_col = sht.used_range.last_cell.column
    body=[]
    Start=2
    End=last_low+1
    for row in range(Start,End) :
      ip       = sht.range(row,1).value
      host     = sht.range(row,2).value
      user     = sht.range(row,3).value
      password = sht.range(row,4).value
      secret   = sht.range(row,5).value
      devtype  = sht.range(row,6).value
      sesslog  = sht.range(row,7).value
      entry = {
               "ip":f'{ip}',
               "host":f'{host}',
               "username":f'{user}',
               "password":f'{password}',
               "4secret":f'{secret}',
               "device_type":f'{devtype}',
               "session.log":f'{sesslog}'
               }
      print(entry)
      body.append(entry)
        
    with open(json_fn,"w") as info :
      json.dump(body,info,indent=4,separators=(',', ': '))
    print("done")

