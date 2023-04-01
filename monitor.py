"""
Author: Dave Weilert
Copyright(C) 2023 Freeware
Date: 3/19/2023

REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------
  2023/03/19  DaW             Initial creation 

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

import config
import logger
import commonDataArea as cda
import pzemHandler
import smsHandler
import checkThresholds
import getCmdInfo
import upsHandler


def getPorts():
    try:
        pzemHandler.find_usb_ports()
        cda.getPortsCnt = cda.getPortsCnt + 1
        if cda.getPortsCnt > int(config.get("Limits","no_ports")):
            sms = []
            sms.append(config.get("Limits","no_ports_msg"))
            sms.append(config.get("Limits","no_ports_who"))
            cda.smsMsg.append(sms)
            smsHandler.checkSMS()
            cda.getPortsCnt = 0

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"getPorts() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"getPorts() {e}")


def resetCheck(nowDay):
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
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"resetCheck() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"resetCheck() {e}")


def mainLine():
    try:
        current_hour = 99
        while True:
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

            # check if any ports were located
            if cnt > 0:
                break
            else:	    
                time.sleep(int(config.get("Interval","wait_to_check_for_ports_seconds")))

        rtn = ""
        while True:

            now = datetime.now()
            nowDay = now.strftime("%Y_%m_%d")

            resetCheck(nowDay)
            
            cda.iCnt = cda.iCnt + 1

            rtn = []
            rtn = pzemHandler.monitor(cda.portA,"A")
            #print(f"A rtn {rtn}")
            if rtn[0] != False:
                checkThresholds.checkPump(rtn[1],"A")
                cda.sensor_A_registers.append(rtn[1])
            
            rtn = []
            rtn = pzemHandler.monitor(cda.portB,"B")
            #print(f"B rtn {rtn}")
            if rtn[0] != False:
                checkThresholds.checkPump(rtn[1],"B")
                cda.sensor_B_registers.append(rtn[1])

            rtn = []
            rtn = pzemHandler.monitor(cda.portC,"C")
            #print(f"C rtn {rtn}")
            if rtn[0] != False:
                checkThresholds.checkPump(rtn[1],"C")
                cda.sensor_C_registers.append(rtn[1])
            
            rtn = []
            rtn = pzemHandler.monitor(cda.portD,"D")
            #print(f"D rtn {rtn}")
            if rtn[0] != False:
                checkThresholds.checkPump(rtn[1],"D")
                cda.sensor_D_registers.append(rtn[1])

            # Check for io errors and connection errors
            checkThresholds.checkSensors()

            # get Raspberry Pi temp and save
            cpu = CPUTemperature()
            cda.cpu_temps.append(cpu.temperature)
            checkThresholds.checkTemperature(cpu.temperature)

            # get Raspberry Pi UPS info
            upsI = upsHandler.getUPSInfo(False)
            checkThresholds.checkUPSCharge(upsI[0])
            checkThresholds.checkUPSPercent(upsI[1])

            # get Raspberry Pi memory usage data
            cda.cpu_ram.append(getRAMinfo())


            # Return RAM information (unit=kb) in a list                                        
            if config.get("Debug","status") == "true":
                logger.msg("I",f"Interval count({cda.iCnt})")

            # check if the CLI interface has any requests
            getCmdInfo.checkForCommandFile()

            time.sleep(int(config.get("Interval","wait_to_check_sensors_seconds")))
            
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"mainLine() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"mainLine() {e}")
        time.sleep(5)
        mainLine()

                                                                
def getRAMinfo():
    try:
        # Index 0: total RAM                                                                
        # Index 1: used RAM                                                                 
        # Index 2: free RAM 
        p = os.popen('free')
        i = 0
        while 1:
            i = i + 1
            line = p.readline()
            if i==2:
                return(line.split()[1:4])
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"getRAMinfo() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"getRAMinfo() {e}")
 

# Main section 
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
        mainLine()
