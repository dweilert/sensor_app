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
import math
from datetime import datetime
import json
from gpiozero import CPUTemperature
import subprocess

import config
import commonDataArea as cda
import upsHandler
import logger


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
                elif "r1" in line:
                    results = getRegisters("A")    
                elif "r2" in line:
                    results = getRegisters("B")    
                elif "r3" in line:
                    results = getRegisters("C")    
                elif "r4" in line:
                    results = getRegisters("D")    
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
        logger.put_msg("E",f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.put_msg("E",f"monitor.getPumpInfo Exception: {e}")


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
        logger.put_msg("E",f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.put_msg("E",f"monitor.checkForCommandFile Exception: {e}")


def getMonitorStatus():
    info = subprocess.run(["systemctl","status","monitor"], capture_output=True, text=True)
    lines = info.stdout
    return lines


def getRegisters(id):
    try:
        results = ""
        print(len(cda.sensor_A_registers))
        print(len(cda.sensor_B_registers))
        print(len(cda.sensor_C_registers))
        print(len(cda.sensor_D_registers))
        if id == "A":
            if len(cda.sensor_A_registers) > 0:
                results = results + "Sensor 1: \n"
                for r in cda.sensor_A_registers:
                    results = results + formatRegisters(r) + "\n"
                results = results + "\n"

        if id == "B":
            if len(cda.sensor_B_registers) > 0:
                results = results + "Sensor 2: \n"
                for r in cda.sensor_B_registers:
                    results = results + formatRegisters(r) + "\n"
                results = results + "\n"

        if id == "C":
            if len(cda.sensor_C_registers) > 0:
                results = results + "Sensor 3: \n"
                for r in cda.sensor_C_registers:
                    results = results + formatRegisters(r) + "\n"
                results = results + "\n"

        if id == "C":
            if len(cda.sensor_D_registers) > 0:
                results = results + "Sensor 4: \n"
                for r in cda.sensor_D_registers:
                    results = results + formatRegisters(r) + "\n"
                results = results + "\n"

        return results

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.put_msg("E",f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.put_msg("E",f"monitor.checkForCommandFile Exception: {e}")
        return "Error getting sensor register information"


def formatRegisters(registers):
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
    #pwangle=math.acos(pwfac)
    #apparent = power/math.cos(pwangle)
    #reactive = apparent*math.sin(pwangle)
    #impedance= apparent/(amp*amp)
    #rinline = impedance*math.cos(pwangle)
    #xinline = impedance*math.sin(pwangle)
    #data = f"volt: {volt}  amp: {amp}  power {power} energy: {energy} freq: {freq}  pwfac:{pwfac}  reactive: {reactive}  apparent: {apparent}  powerangle: {pwangle}  impedance: {impedance}  rinline: {rinline}  xinline: {xinline}  status: {alarmtran}"
    data = f"volt:{volt}  amp:{amp}  power:{power}  energy:{energy}  freq:{freq}  pwfac:{pwfac}  alarm:{alarmtran}"
       
    return data

