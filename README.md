# network-tool
cisco_config.py - configuration update and issue show commands for Cisco ,F5　BigIP using netmiko

1.Input
target_device=info.json : IP address,userid,password,device-type
<IPADDR>_config.txt:IPADDR shouuld be change to network device
<IPADDR>_show.txt: IPADDR shouuld be change to network device

2.Output
YYYMMDD_result.txt : complition status for each deveice and output from show command or error messages  
^\logs\<IPADDR>\<IPADDR>_YYYYMMDD.log : output from show command 
~\logs\<IPADDR>\<IPADDR>_YYYYMMDD_new.txt : after running-config 
~\logs\<IPADDR>\<IPADDR>_YYYYMMDD_org.txt : before  running-config 
~\logs\<IPADDR>\<IPADDR>_YYYYMMDD_diff.html : differnce between  before and after  running-config  with html format
Note 
follwing file loacation should be chang according to your environment
"F:\\DRScripts\\ScriptLogs\Network日‐月‐年‐時‐分.log　just required for the project readon.
