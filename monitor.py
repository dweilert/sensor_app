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
import logging
from gpiozero import CPUTemperature
import subprocess

import config
import commonDataArea as cda
import pzemHandler
import smsHandler
import checkThresholds
import upsHandler
import logger


def getPorts():
    try:
        pzemHandler.find_usb_ports()
        cda.getPortsCnt = cda.getPortsCnt + 1
        if cda.getPortsCnt > int(config.get("Limits","no_ports")):
            smsHandler.sendSMS(config.get("Limits","no_ports_number"), config.get("Limits","no_ports_msg"), config.get("Limits","no_ports_who"))
            cda.getPortsCnt = 0
    except Exception as e:
        logger.put_msg("E","monitor.getPorts ERROR: " + e)

def checkForCommandFile():
    try:
        filename = config.get("CommandInterface","cmd_file")
        if os.path.exists(filename):
            f = open(config.get("CommandInterface","cmd_file"),"r")  
            results = ""      
            for line in f:
                if "monitor" in line:
                    results = getMonitorStatus()
                elif "pumps" in line:
                    results = getPumpInfo()
                elif "sensor" in line:
                    results = getSensorInfo()
                elif "ups" in line:
                    results = upsHandler.getUPSInfo()    
                elif "temp" in line:
                    results = getTempInfo()    
                elif "logs" in line:
                    for m in cda.log_messages:
                        results = results + m + "\n"
                else:
                    results = results + "INVALID request, cannot be processed" + "\n"

            if results == "":
                results = "Failed to get requested data"
            f = open(config.get("CommandInterface","results_file"), "w")
            f.write(results) 
            f.close()               
            
            os.remove(filename)

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.put_msg("E",f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.put_msg("E",f"monitor.checkForCommandFile Exception: {e}")

def getTempInfo():
    try:
        high = 0
        low = 999
        total = 0
        cnt = 0
        for t in cda.cpu_temps:
            if t > high:
                high = t
            if t < low:
                low = t
            total = total + t
            cnt = cnt + 1
        
        avg = total / cnt
        results = "Temperature information" + "\n"
        results = results + ("  Average temp : {:6.3f}".format(avg)) + "\n"
        results = results + "  High temp    : " + str(high) + "\n"
        results = results + "  Low temp     : " + str(low) + "\n"
        return results
    
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.put_msg("E",f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.put_msg("E",f"monitor.getTempInfo Exception: {e}")




def getPumpInfo():
    try:

        print(cda.pumpA_cycles)

        result = "\nPump 1: \n"
        result = result + "  On/Off status: " + cda.pumpA_status + "\n"
        result = result + "  ---- Latest information ----" + "\n"
        result = result + "  Cycle count     : " + str(cda.pumpA_cycle_cnt) + "\n"
        result = result + "  Start date/time : " + str(cda.pumpA_start) + "\n"
        result = result + "  End date/time   : " + str(cda.pumpA_stop) + "\n"
        result = result + "  Start energy    : " + str(cda.pumpA_energy_start) + "\n"
        result = result + "  End energy      : " + str(cda.pumpA_energy_latest) + "\n"
        result = result + "  Amps high       : " + str(cda.pumpA_amp_high) + "\n"
        result = result + "  Amps low        : " + str(cda.pumpA_amp_low) + "\n"
        result = result + ("  Amps avg        :{:6.3f}".format(cda.pumpA_amp_avg)) + "\n"
        result = result + "  ---- Current cycle information ----" + "\n"


        result = result + "\n"
        result = result + "Pump 2: \n"
        result = result + "  On/Off status: " + cda.pumpB_status + "\n"
        result = result + "  ---- Latest information ----" + "\n"
        result = result + "  Cycle count     : " + str(cda.pumpB_cycle_cnt) + "\n"
        result = result + "  Start date/time : " + str(cda.pumpB_start) + "\n"
        result = result + "  End date/time   : " + str(cda.pumpB_stop) + "\n"
        result = result + "  Start energy    : " + str(cda.pumpB_energy_start) + "\n"
        result = result + "  End energy      : " + str(cda.pumpB_energy_latest) + "\n"
        result = result + "  Amps high       : " + str(cda.pumpB_amp_high) + "\n"
        result = result + "  Amps low        : " + str(cda.pumpB_amp_low) + "\n"
        result = result + ("  Amps avg        :{:6.3f}".format(cda.pumpB_amp_avg)) + "\n"
        result = result + "  ---- Current cycle information ----" + "\n"

        print(cda.pumpA_cycles)

        return result
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.put_msg("E",f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.put_msg("E",f"monitor.getPumpInfo Exception: {e}")

def printList():
    try:

        return 
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.put_msg("E",f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.put_msg("E",f"monitor.printList Exception: {e}")



def getSensorInfo():
    try:
        result = "\nSensor 1: \n"
        result = result + "  USB port       : " + cda.portA + "\n"
        result = result + "  I/O Error      : " + str(cda.sensor_A_io_error) + "\n"
        result = result + "  Connect Error  : " + str(cda.sensor_A_connect_error) + "\n"
        result = result + "Sensor 2: \n"
        result = result + "  USB port       : " + cda.portB + "\n"
        result = result + "  I/O Error      : " + str(cda.sensor_B_io_error) + "\n"
        result = result + "  Connect Error  : " + str(cda.sensor_B_connect_error) + "\n"
        result = result + "Sensor 3: \n"
        result = result + "  USB port       : " + cda.portC + "\n"
        result = result + "  I/O Error      : " + str(cda.sensor_C_io_error) + "\n"
        result = result + "  Connect Error  : " + str(cda.sensor_C_connect_error) + "\n"
        result = result + "Sensor 4: \n"
        result = result + "  USB port       : " + cda.portD + "\n"
        result = result + "  I/O Error      : " + str(cda.sensor_D_io_error) + "\n"
        result = result + "  Connect Error  : " + str(cda.sensor_D_connect_error) + "\n"
        result = result + "\n"
        return result
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.put_msg("E",f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.put_msg("E",f"monitor.checkForCommandFile Exception: {e}")

def getMonitorStatus():
    info = subprocess.run(["systemctl","status","monitor"], capture_output=True, text=True)
    lines = info.stdout
    return lines


def getMonitorStatus():
    info = subprocess.run(["systemctl","status","monitor"], capture_output=True, text=True)
    lines = info.stdout
    return lines



def resetCheck():
    now = datetime.now()
    new = now.strftime("%Y_%m_%d")

    # Check if it is a new day if so swap to new file
    if cda.current_date != new:
        cda.current_date = new
        cda.iCnt = 0
        cda.error_cnt = 0
        pumpB_cycle_cnt = 0
        pumpA_cycle_cnt = 0

def mainLine():
    try:
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
                time.sleep(int(config.get("Interval","wait_to_check_for_ports")))

        rtn = ""
        while True:
            # if new date reset counters
            resetCheck()

            cda.iCnt = cda.iCnt + 1
            rtn = pzemHandler.monitor(cda.portA,"A")
            if config.get("Debug","show_regs") == "true":
                logger.put_msg("D",f"Port A Regs: {rtn}")
            checkThresholds.check(rtn,"A")
            
            rtn = pzemHandler.monitor(cda.portB,"B")
            if config.get("Debug","show_regs") == "true":
                logger.put_msg("D",f"Port B Regs: {rtn}")
            checkThresholds.check(rtn,"B")
            
            rtn = pzemHandler.monitor(cda.portC,"C") 
            if config.get("Debug","show_regs") == "true":
                logger.put_msg("D",f"Port C Regs: {rtn}")
            checkThresholds.check(rtn,"C")
            
            rtn = pzemHandler.monitor(cda.portD,"D")          
            if config.get("Debug","show_regs") == "true":
                logger.put_msg("D",f"Port D Regs: {rtn}")
            checkThresholds.check(rtn,"D")

            # Check for io errors and connection errors
            checkThresholds.checkSensors()

            ups = upsHandler.getUPSInfo()

            # Log iteration and wait

            #print(f"Interval count: {iCnt}", end="")
            now = datetime.now()
            ts = now.strftime("%Y-%m-%d %H:%M:%S.%f")
            
            # get cpu temperature and save
            cpu = CPUTemperature()
            cda.cpu_temps.append(cpu.temperature)

            logger.put_msg("I",f"Interval count({cda.iCnt})")

            # check if the CLI interface has any requests
            checkForCommandFile()

            time.sleep(int(config.get("Interval","wait_to_check_sensors")))
            
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.put_msg("E",f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.put_msg("E",f"monitor.mainLine Exception: {e}")
        time.sleep(15)
        mainLine()

	

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
        logger.put_msg("E",f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")               
        logger.put_msg("E",f"monitor.__main__ Exception: {e}")    
        time.sleep(5)
        mainLine()
