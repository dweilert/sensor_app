"""
Author: Dave Weilert
Copyright(C) 2023 Freeware
Date: 3/19/2023

REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------
  2023/03/19  DaW             Initial creation 
  2023/06/21  DaW             Added messages at startup about number of sensors
                              and if the default values are in use.
  2023/06/26  DaW             Removed three def's checkDiag, diagInfo, and 
                              getRAMinfo and moved them to a new util.py file.

OVERVIEW:
    <to be updated>

LICENSE:
    This program is free for you to inspect, study, and modify for your 
    personal or commerical use. 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 3 of the License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
 
"""

import os
import time
import sys
from datetime import datetime
from gpiozero import CPUTemperature
import requests

import config
import logger
import util
import commonDataArea as cda
import pzemHandler
import smsHandler
import awsHandler
import checkThresholds
import getCmdInfo
import upsHandler
import endOfDay


def getPorts():
    try:
        pzemHandler.find_usb_ports()
        cda.getPortsCnt = cda.getPortsCnt + 1

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"getPorts() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"getPorts() {e}")


def resetCheck(nowDay, nowHour):
    try:
        # Check if it is a new day, if so reset memory 
        if cda.current_date != nowDay:
            cda.current_date = nowDay
            cda.iCnt = 0
            cda.error_cnt = 0
            cda.pumpB_cycle_cnt = 0
            cda.pumpA_cycle_cnt = 0
            cda.sensor_A_registers = []
            cda.sensor_B_registers = []
            cda.sensor_C_registers = []
            cda.sensor_D_registers = []
            cda.cpu_temps = []
            cda.cpu_ram = []
            cda.upsData = []
            cda.high_temp_cnt = 0
            cda.ups_charge_cnt = 0
            cda.ups_percent_cnt = 0
            cda.errno71_cnt = 0
            # End of day message and stats
            endOfDay.sendDailyInfo()
            cda.daily_pump_A_cnt = 0
            cda.daily_pump_B_cnt = 0
            cda.daily_pump_A_high_amp = 0
            cda.daily_pump_B_high_amp = 0
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"resetCheck() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"resetCheck() {e}")


def mainLine():
    diagCnt = 0
    find_cnt = 0
    """
    Get the USB ports that are connected to the PZEM sensors.  At startup of the
    Raspberry Pi there are messages that are accessable via the linux command
    dmesg.  The pzemHandler will try and find these messages.  If the dmesg 
    output is not located the system will retry 10 times then default to:
        portA = "/dev/ttyUSB0"
        portB = "/dev/ttyUSB1"
        portC = "/dev/ttyUSB2"
        portD = "/dev/ttyUSB3"

    Once tttyUSB* ports are set the system will begin polling the sensors on 
    each USB port.
    """    
    try:
        current_hour = 99
        while True:    
            find_cnt = find_cnt + 1
            getPorts()
            cnt = 0   
            if (cda.portA != "na"):
                cnt = cnt + 1
            if (cda.portB != "na"):
                cnt = cnt + 1
            if (cda.portC != "na"):
                cnt = cnt + 1
            if (cda.portD != "na"):
                cnt = cnt + 1    

            # Circut breaker to stop looking for USB definitions
            if find_cnt > 10:
                cda.portA = "/dev/ttyUSB0"
                cda.portB = "/dev/ttyUSB1"
                cda.portC = "/dev/ttyUSB2"
                cda.portD = "/dev/ttyUSB3"
                logger.msg("I",f"Attempted to read USB ports 10 times, forced use of default USB ports")
                sms = []
                sms.append(config.get("Messages","sensors_default_msg"))
                sms.append(config.get("Messages","sensors_default_who"))
                cda.smsMsg.append(sms)
                smsHandler.sendSMS()    
                break

            # check if any ports were located
            if cnt > 0:
                sms = []
                sms.append(config.get("Messages","sensors_at_startup_msg")+" "+str(cnt))
                sms.append(config.get("Messages","sensors_at_startup_who"))
                cda.smsMsg.append(sms)
                smsHandler.sendSMS() 
                break
            else:	    
                time.sleep(int(config.get("Interval","wait_to_check_for_ports_seconds")))



        rtn = ""
        while True:

            now = datetime.now()
            nowDay = now.strftime("%Y_%m_%d")
            nowHour = now.strftime("%H")
            resetCheck(nowDay, nowHour)
            
            cda.iCnt = cda.iCnt + 1

            rtn = []
            rtn = pzemHandler.monitor(cda.portA,config.get("USBPortSignatures","mapAto"))
            #print(f"A rtn {rtn}")
            if rtn[0] == False:
                rtn[1] = []
            checkThresholds.checkData(rtn[1],config.get("USBPortSignatures","mapAto"))
            cda.sensor_A_registers.append(rtn[1])
            
            rtn = []
            rtn = pzemHandler.monitor(cda.portB,config.get("USBPortSignatures","mapBto"))
            #print(f"B rtn {rtn}")
            if rtn[0] == False:
                rtn[1] = []
            checkThresholds.checkData(rtn[1],config.get("USBPortSignatures","mapBto"))
            cda.sensor_B_registers.append(rtn[1])

            rtn = []
            rtn = pzemHandler.monitor(cda.portC,config.get("USBPortSignatures","mapCto"))
            #print(f"C rtn {rtn}")
            if rtn[0] == False:
                rtn[1] = []
            checkThresholds.checkData(rtn[1],config.get("USBPortSignatures","mapCto"))
            cda.sensor_C_registers.append(rtn[1])
            
            rtn = []
            rtn = pzemHandler.monitor(cda.portD,config.get("USBPortSignatures","mapDto"))
            #print(f"D rtn {rtn}")
            if rtn[0] == False:
                rtn[1] = []
            checkThresholds.checkData(rtn[1],config.get("USBPortSignatures","mapDto"))
            cda.sensor_D_registers.append(rtn[1])

            # Check for io errors and connection errors
            checkThresholds.checkSensors()

            # get Raspberry Pi temp and save if it is a new hour
            cpu = CPUTemperature()
            if nowHour != cda.cpu_temp_hour:
                cda.cpu_temps.append(nowHour + ":" + str(cpu.temperature))
                cda.cpu_temp_hour = nowHour

            # check temperature for out of threshoold ranges
            checkThresholds.checkTemperature(cpu.temperature)

            # get Raspberry Pi UPS info
            upsI = upsHandler.getUPSInfo(False)
            checkThresholds.checkUPSCharge(upsI[0])
            checkThresholds.checkUPSPercent(upsI[1])

            # get Raspberry Pi memory usage data
            cda.cpu_ram.append(util.getRAMinfo())

            # Return RAM information (unit=kb) in a list                                        
            if config.get("Debug","interval_count") == "true":
                logger.msg("I",f"Interval count({cda.iCnt})")

            # check if the CLI interface has any requests
            getCmdInfo.checkForCommandFile()

            time.sleep(int(config.get("Interval","wait_to_check_sensors_seconds")))

            # if diagCnt == 5:
            #     util.checkDiag()
            #     diagCnt = 0
            # else:
            #     diagCnt = diagCnt + 1
            
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"mainLine() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"mainLine() {e}")
        time.sleep(5)
        mainLine()


 

""" 
===============================================================================
Main section 

This application may have been started as a system service.  If defined as a 
service it will be in the directory:

/lib/systemd/system/

Default service name is monitor.service with the following.  Ensure the User 
parameter is defined of the sensor_app files will not be located.

-------- File contents --------
[Unit]
Description=MMPOAII Monitor

[Service]
User=bob
WorkingDirectory=/home/bob
ExecStart=/usr/bin/python /home/bob/sensor_app/monitor.py
Restart=on-abort
#Environment=PYTHONPATH=/home/bob/sensor_app

[Install]
WantedBy=multi-user.target

-------- End of file --------

Work with the service by using these commands:

  -- What --         ---- command ----
Check status    : systemctl status monitor
Start service   : systemctl start monitor
Stop service    : systemctl stop monitor
Restart service : systemctl restart monitor

===============================================================================
"""
if __name__ == "__main__":
    # reset_usb()
    try:
        # Read config.ini file for parameters
        config.readConfig()
        # set current date
        now = datetime.now()
        cda.current_date = now.strftime("%Y_%m_%d")
        # initialize values
        cda.cmdI = ""
        cda.iCnt = 0
        cda.error_cnt = 0

        # Check if old CLI command.txt file exists and delete if found
        if os.path.exists(config.get("CommandInterface","cmd_file")):
            os.remove(config.get("CommandInterface","cmd_file"))

        mainLine()

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"__main__ Exception type: {exception_type} File name: {filename} Line number: {line_number}")               
        logger.msg("E",f"__main__ {e}")
        time.sleep(5)

        # Invoke mainLine even if an error occurs
        mainLine()
