# network-tool
1.cisco_config.py - configuration update and issue show commands for Cisco ,F5　BigIP using netmiko
 cisco_config-thread.py - configuration update and issue show commands for Cisco ,F5　BigIP using netmiko and multithread 
 argument 
 -j <json file name> default target_device_info.json
 -d dryrun bypass config changing process,handling show commands .

 1.1 Input
 target_device_info.json : IP address,user id,password,device-type
 <host>_config.txt:IPADDR shouuld be change to network device
 <host>_show.txt: IPADDR shouuld be change to network device
 or 
 <ipaddr>_config.txt:IPADDR should be change to network device
 <ipaddr>_show.txt: IPADDR should be change to network device
 1.2.Output
 YYYMMDD_result.txt : complition status for each deveice and output from show command or error messages  
 ^\logs\<host>\<ipaddr>_<host>_YYYYMMDD.log : output from show command 
 ~\logs\<host>\<IPADDR>_YYYYMMDD_new.txt : after running-config 
~\logs\<host>\<IPADDR>_YYYYMMDD_org.txt : before  running-config 
~\logs\<host>\<IPADDR>_YYYYMMDD_session_log.txt : before  running-config 
~\logs\<host>\<IPADDR>_YYYYMMDD_diff.html : differnce between  before and after  running-config  with html format

2. Ex2Json.py  : Conver  Excel file to JSON file 
   argument 
-e input Excel file name
 2.1 Input
     Excel file which include IP address,hostname,user id,password,secret password,session_log file name,device_type, do not change colum order
 2.2
    JSON file ,Excel work-sheet name is used by Excel file name,  



