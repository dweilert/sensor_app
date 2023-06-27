"""
Author: Dave Weilert
Copyright(C) 2023 Freeware
Date: 3/19/2023

REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------
  2023/03/19  DaW             Initial creation 
  2023/06/23  DaW             Added C option, interval count

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
# import time
import sys
import math
from datetime import datetime
# import json
from gpiozero import CPUTemperature
import subprocess
import math

import config
import commonDataArea as cda
import upsHandler
import logger
import smsHandler
import endOfDay


def checkForCommandFile():
    try:
        filename = config.get("CommandInterface","cmd_file")
        if os.path.exists(filename):
            f = open(config.get("CommandInterface","cmd_file"),"r")  
            results = ""      
            for line in f:
                if line.strip() == "":
                    results = "Failed to read command request, please retry"
                    break                
                elif "monitorStatus" in line:
                    results = callMonitorInterface("status")
                elif "count" in line:
                    results = intervalCounts()
                elif "count" in line:
                    results = intervalCounts()
                elif "daily" in line:
                    results = getDaily()
                elif "sensor" in line:
                    results = getSensorInfo()
                elif "ups" in line:
                    results = upsHandler.getUPSInfo(True)    
                elif "temp" in line:
                    results = getTempInfo()  
                elif "memory" in line:
                    results = getMemory()    
                elif "regs" in line:
                    results = getRegisters("A")    
                    results = results + "\n";
                    results = results + getRegisters("B")    
                    results = results + "\n";
                    results = results + getRegisters("C")    
                    results = results + "\n";
                    results = results + getRegisters("D")           
                elif "get_all" in line:
                    results = getAllData() 
      
                elif "sms_dev" in line:
                    sms = []
                    sms.append(config.get("Messages","test_msg_dev_msg"))
                    sms.append(config.get("Messages","test_msg_dev_who"))
                    cda.smsMsg.append(sms)
                    smsHandler.checkSMS("other")
                    results = "Test SMS sent to developer"     
                elif "sms_man" in line:
                    sms = []
                    sms.append(config.get("Messages","test_msg_maint_msg"))
                    sms.append(config.get("Messages","test_msg_maint_who"))
                    cda.smsMsg.append(sms)
                    smsHandler.checkSMS("other")
                    results = "Test SMS sent to maintenace"     
                elif "sms_own" in line:
                    sms = []
                    sms.append(config.get("Messages","test_msg_owners_msg"))
                    sms.append(config.get("Messages","test_msg_owners_who"))
                    cda.smsMsg.append(sms)
                    smsHandler.checkSMS("other")
                    results = "Test SMS sent to owners" 
                elif "sms_daily" in line:
                    sms = []
                    sms.append(config.get("Messages","end_of_day_msg") + endOfDay.getDailyData())
                    sms.append(config.get("Messages","end_of_day_who"))
                    cda.smsMsg.append(sms)
                    smsHandler.checkSMS("other")
                    results = "Test End-of-Day SMS sent to developer"                         
                elif "wrap" in line:
                    results = wrapLog()                     
                elif "all_clear" in line:
                    sms = []
                    sms.append(config.get("Messages","all_clear_msg"))
                    sms.append(config.get("Messages","all_clear_who"))
                    cda.smsMsg.append(sms)
                    smsHandler.checkSMS("other")
                    results = "All clear SMS sent to owners"     
                elif "logs" in line:
                    parts = line.split("_")
                    qty = 0
                    if parts[1] != "all":
                        qty = int(parts[1])
                    else:
                        qty = 999999
                    results = getLogInfo(qty)
                elif "stop" in line:
                    results = wrapLog() 
                elif "start" in line:
                    results = wrapLog() 
                elif "restart" in line:
                    results = wrapLog()                        
                else:
                    results = "Request " + line + " cannot be processed" + "\n"

            if results == "":
                results = "Failed to get requested data"
            f = open(config.get("CommandInterface","results_file"), "w")
            f.write(results) 
            f.close()               
            
            os.remove(filename)

    except Exception as e:
        errorLine = f"Exception: {e}"

        if "[Errno " in errorLine:
            f = open(config.get("CommandInterface","results_file"), "w")
            f.write("Error: " + errorLine) 
            f.close()

        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"checkForCommandFile() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"checkForCommandFile() {e}")

def getLogInfo(qty):
    qty = int(qty)
    results = "\n---- Log information ----\n"
    max = len(cda.log_messages)
    ptr = 0
    if qty == "all":
        qty = max
        ptr = 0
    elif qty < max:
        ptr = max - qty
    elif qty > max:
        qty = max
        ptr = 0    
    try:
        for x in range(qty):
            results = results + cda.log_messages[ptr] + "\n"
            ptr = ptr + 1

        return results + "\n"

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"getAllData() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"getAllData() Exception: {e}")
        return "Error getting all diag information"        

def getAllData():
    results = ""
    try:
        results = results + getDaily()
        results = results + "\n";        
        results = results + intervalCounts()
        results = results + "\n";        
        results = results + getRegisters("A")    
        results = results + "\n";
        results = results + getRegisters("B")    
        results = results + "\n";
        results = results + getRegisters("C")    
        results = results + "\n";
        results = results + getRegisters("D") 

        results = results + callMonitorInterface("status")
        results = results + getPumpInfo()
        results = results + getSensorInfo()
        results = results + upsHandler.getUPSInfo(True)    
        results = results + getTempInfo()  
        results = results + getMemory() 
        results = results + getLogInfo(100)       # get last 100 lines of logs
        results = results + "\n"
        return results
    
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"getAllData() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"getAllData() Exception: {e}")
        return "Error getting all diag information"


def intervalCounts():
    results = ""
    try:
        results = "Interval count for the day: " + str(cda.iCnt) + "\n"
        return results
    
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"intervalCounts() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"intervalCounts() Exception: {e}")
        return "Error getting interval counts information"


def wrapLog():
    try:
        status = logger.wrapLogs()
        if status == True:
            return "Logs wrapped"
        else:
            return "Status of log wrap unknown"
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"wrapLog() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"wrapLog() Exception: {e}")
        return "Error wrapping logs"

def getTempInfo():
    try:
        high = 0
        low = 999
        total = 0
        cnt = 0
        for t in cda.cpu_temps:
            parts = t.split(":")
            temp = float(parts[1])
            if temp > high:
                high = temp
            if temp < low:
                low = temp
            total = total + temp
            cnt = cnt + 1
        
        if total > 0:
            avg = total / cnt
        else:
            avg = 0
        avg = "{:6.3f}".format(avg)

        results = "Temperature information" + "\n"
        results = results + "  Average temp : " + str(avg) + "\n"
        results = results + "  High temp    : " + str(high) + "\n"
        results = results + "  Low temp     : " + str(low) + "\n"

        high = math.floor(high)
        low = math.floor(low)
        if high > low:
            diff = high - low
        else:
            diff = 0

        results = results + "  -- Hourly graph --\n"
        for t in cda.cpu_temps:
            parts = t.split(":")
            fT = float(parts[1])
            temp = math.floor(fT)
            dots = temp - diff
            prtD = ""
            # Create a string of *'s for the temperature graph
            for x in range(dots):
                prtD = prtD + "*"

            oT = "{:6.3f}".format(fT)
            results = results + f"  At hour: {parts[0]} temp is: {oT} : {prtD}" + "\n"

        return results
    
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"getTempInfo() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"getTempInfo() Exception: {e}")
        return "Error getting temperature information"

def getDaily():
    try:
        result = "  ---- Daily information ----\n" + endOfDay.getDailyData() + "\n"
        return result
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"getDaily() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"getDaily()  {e}")
        return "Error getting daily information"


def getPumpInfo():
    try:
        # print(cda.pumpA_cycles)
        result = "Pump 1: \n"
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

        return result
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"getPumpInfo() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"getPumpInfo()  {e}")
        return "Error getting pump information"


def getSensorInfo():
    try:
        result = "Sensor 1: \n"
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
        logger.msg("E",f"getSensorInfo() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"getSensorInfo() {e}")
        return "Error getting sensor information"
    

def callMonitorInterface(cmd):
    try:
        info = subprocess.run(["systemctl",cmd,"monitor"], capture_output=True, text=True)
        lines = info.stdout
        return lines
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"getMonitorStatus() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"getMonitorStatus() {e}")
        return "Error getting monitor.service status"


def getMemory():
    # Return RAM information (unit=kb) in a list                                        
    # Index 0: total RAM                                                                
    # Index 1: used RAM                                                                 
    # Index 2: free RAM
    try:
        t_mem = 0

        u_high = 0
        u_low = 999

        f_high = 0
        f_low = 999

        cnt = 0
        for m in cda.cpu_ram:
            if int(m[1]) > u_high:
                u_high = int(m[1])
            if int(m[1]) < u_low:
                u_low = int(m[1])
            t_mem = int(m[0])

        u_high = u_high / 1000
        u_high = "{:5.3f}".format(u_high)
        u_low = u_low / 1000
        u_low = "{:5.3f}".format(u_low)
        t_mem = t_mem / 1000
        t_mem = "{:5.3f}".format(t_mem)

        results = "Memory information" + "\n"
        results = results + "  Total (MB)    : " + str(t_mem) + "\n"
        results = results + "  High used (MB): " + str(u_high) + "\n"
        results = results + "  Low used (MB) : " + str(u_low) + "\n"

        return results
    
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"getMemory() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"getMemory() Exception: {e}")
        return "Error getting memory data"


def getRegisters(id):
    try:
        results = ""
        a_len = len(cda.sensor_A_registers)
        a_len = a_len - 1
        if a_len > 10:
            a_start = a_len - 9
        else:
            a_start = 0

        b_len = len(cda.sensor_B_registers)
        b_len = b_len - 1
        if b_len > 10:
            b_start = b_len - 9
        else:
            b_start = 0
        
        c_len = len(cda.sensor_C_registers)
        c_len = c_len - 1
        if c_len > 10:
            c_start = c_len - 9
        else:
            c_start = 0
        
        d_len = len(cda.sensor_D_registers)
        d_len = d_len - 1
        if d_len > 10:
            d_start = d_len - 9
        else:
            d_start = 0

        if id == "A":
            if a_len > 0:
                results = results + "Sensor 1: \n"
                p = a_start
                while p <= a_len:
                    results = results + "(" + str(p) + ") " + formatRegisters(cda.sensor_A_registers[p]) + "\n"
                    p = p + 1
                results = results + "\n"
            else:
                results = "No data for reqister" + "\n"

        if id == "B":
            if b_len > 0:
                results = results + "Sensor 2: \n"
                p = b_start
                while p <= b_len:
                    results = results + "(" + str(p) + ") " + formatRegisters(cda.sensor_B_registers[p]) + "\n"
                    p = p + 1
                results = results + "\n"
            else:
                results = "No data for reqister" + "\n"

        if id == "C":
            if c_len > 0:
                results = results + "Sensor 3: \n"
                p = c_start
                while p <= c_len:
                    results = results + "(" + str(p) + ") " + formatRegisters(cda.sensor_C_registers[p]) + "\n"
                    p = p + 1
                results = results + "\n"
            else:
                results = "No data for reqister" + "\n"

        if id == "D":
            if d_len > 0:
                results = results + "Sensor 4: \n"
                p = d_start
                while p <= d_len:
                    results = results + "(" + str(p) + ") " + formatRegisters(cda.sensor_D_registers[p]) + "\n"
                    p = p + 1
                results = results + "\n"
            else:
                results = "No data for reqister" + "\n"

        return results

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"getRegisters() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"getRegisters() {e}")
        return "Error getting sensor register information"


def formatRegisters(registers):
    try:
        if len(registers) < 8:
            return "No data for register"
        volt = registers[0]*0.1
        volt = "{:5.2f}".format(volt)
        amp = registers[1]*0.001
        amp = "{:5.3f}".format(amp)
        power = registers[3]*0.1
        power = "{:6.2f}".format(power)
        energy = registers[5]*0.001
        energy = "{:4.2f}".format(energy)
        freq = registers[7]*0.1
        freq = "{:4.2f}".format(freq)
        pwfac = registers[8]*0.01
        pwfac = "{:3.2f}".format(pwfac)

        alarm = registers[9]
        if alarm == 0x0000:
            alarmtran = 'OFF'
        elif alarm == 0xFFFF:
            alarmtran = 'ON'
        else:
            alarmtran = 'N/A'
        data = f"volt: {volt}  amp: {amp}  power: {power}  energy: {energy}  freq: {freq}  pwfac: {pwfac}  alarm: {alarmtran}"
        
        return data
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"formatRegisters() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"formatRegisters() {e}")
        return "Error formatting register information"

