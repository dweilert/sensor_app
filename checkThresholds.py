#!/usr/bin/env python3

"""
Author: Dave Weilert
Copyright(C) 2023 Freeware
Date: 3/19/2023

REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------
  2023/03/19  DaW             Initial creation

OVERVIEW:
    Module to determine if monitor thresholds have been exceeded.  If the
    data exceeds send an SMS to the appropriate group.  

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

import sys
import config
import commonDataArea as cda
import smsHandler
import logger

# Voltage
cda.aNoV = 0
cda.bNoV = 0
cda.cNoV = 0
cda.dNoV = 0

# Power
cda.aNoP = 0
cda.bNoP = 0
cda.cNoP = 0
cda.dNoP = 0

# Data
cda.aNoD = 0
cda.bNoD = 0
cda.cNoD = 0
cda.dNoD = 0

cda.overall_msg_sent = False
cda.overall_msg_cnt = 0
cda.alarm_msg_sent = False
cda.alarm_msg_cnt = 0

# SMS message array
cda.smsMsg = []
	
	
def check(pzem_data,id):
    try:
        # print(type(pzem_data))
        # if type(pzem_data) != "list":
        #     logger.put_msg("E",f"checkThresholds.check: No valid data from sensor {id}")
        #     return
        # Clear SMS messages
        cda.smsMsg = []
        # Increment counters and check against thresholds.

        # pumpA,
        if id == "A": 
            if (pzem_data[0] == "nodata"):
                cda.aNoD = cda.aNoD + 1
                if cda.aNoD > int(config.get("Limits","no_data")):
                    cda.smsMsg.append("Pump A" + " " + config.get("Limits","no_data_msg"))
                    cda.aNoD = 0
            else:
                msg = voltage(pzem_data,"A")
                if msg != "noMsg":
                    cda.smsMsg.append(msg)                 
                    cda.aNoV = 0

                msg = power(pzem_data,"A")
                if msg != "noMsg":
                    cda.smsMsg.append(msg)                 
                    cda.aNoP = 0
       
        # pumpB
        if id == "B":        
            if (pzem_data[0] == "nodata"):
                cda.bNoD = cda.bNoD + 1
                if cda.bNoD > int(config.get("Limits","no_data")):
                    cda.smsMsg.append("Pump B" + " " + config.get("Limits","no_data_msg"))
                    cda.bNoD = 0
            else:
                msg = voltage(pzem_data,"B")
                if msg != "noMsg":
                    cda.smsMsg.append(msg)                 
                    cda.bNoV = 0
                msg = power(pzem_data,"B")
                if msg != "noMsg":
                    cda.smsMsg.append(msg)                 
                    cda.bNoP = 0

        # alarm
        if id == "C": 
            if (pzem_data[0] == "nodata"):
                cda.cNoD = cda.cNoD + 1
                if cda.cNoD > int(config.get("Limits","no_data")):
                    cda.smsMsg.append("Alarm" + " " + config.get("Limits","no_data_msg"))
                    cda.cNoD = 0
                    cda.alarm_msg_cnt = 0
            else:
                if (pzem_data[1] > 0):
                    if cda.alarm_msg_sent == False:
                        cda.smsMsg.append(config.get("Messages","alarm_msg"))
                        cda.alarm_msg_sent = True
                    else:
                        cda.alarm_msg_cnt = cda.alarm_msg_cnt + 1
                        # If problem is not resolved within an hour reset
                        if cda.alarm_msg_cnt > int(config.get("Limits","reset_alarm_msg_sent")):
                            cda.alarm_msg_sent = False
                            cda.alarm_msg_cnt = 0

        # overall power
        if id == "D": 
            if (pzem_data[0] == "nodata"):
                cda.dNoD = cda.dNoD + 1
                if cda.dNoD > int(config.get("Limits","no_data")):
                    cda.smsMsg.append("Sensor D (power monitor) " + config.get("Limits","no_data_msg"))
                    cda.cNoD = 0
            else:
                if (pzem_data[1] == 0):
                    if cda.overall_msg_sent == False:
                        cda.smsMsg.append(config.get("Messages","overall_power_msg"))
                        cda.overall_msg_sent = True
                    else:
                        cda.overall_msg_cnt = cda.overall_msg_cnt + 1
                        # If problem is not resolved within an hour reset
                        if cda.overall_msg_cnt > int(config.get("Limits","reset_overall_msg_sent")):
                            cda.overall_msg_sent = False
                            cda.overall_msg_cnt = 0


        checkSMS()
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.put_msg("E",f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.put_msg("E",f"checkThresholds.check ERROR for sensor{id}: {e}")
    
def checkSensors():
    # Check if sensors are not connected
    connErr = ""
    if cda.sensor_A_connect_error == True:
        connErr = connErr + " A "
    if cda.sensor_B_connect_error == True:
        connErr = connErr + " B "
    if cda.sensor_C_connect_error == True:
        connErr = connErr + " C "
    if cda.sensor_D_connect_error == True:
        connErr = connErr + " D "
    if connErr != "":
        if cda.sensor_connect_error_msg_cnt == 0:
            msg = config.get("Pzem","connect_error_msg")
            msg = msg + " " + connErr
            msgOut = []
            msgOut.append(msg)
            smsHandler.sendSMS(config.get("Developer","phones"), msgOut, "Developer")
            cda.sensor_connect_error_msg_cnt = cda.sensor_connect_error_msg_cnt + 1
        else:
            print(f"cda.sensor_connect_error_msg_cnt {cda.sensor_connect_error_msg_cnt}")
            val = config.get("Pzem","connect_error_reset_count")
            print(f"connect_error_reset_count {val}")
            if cda.sensor_connect_error_msg_cnt > int(config.get("Pzem","connect_error_reset_count")):
                cda.sensor_connect_error_msg_cnt = 0
    
    # Check if sensors have read error
    ioCnt = 0
    ioErr = ""
    if cda.sensor_A_io_error == True:
        ioErr = ioErr + " A "
        ioCnt = ioCnt + 1
    if cda.sensor_B_io_error == True:
        ioErr = ioErr + " B "
        ioCnt = ioCnt + 1
    if cda.sensor_C_io_error == True:
        ioErr = ioErr + " C "
        ioCnt = ioCnt + 1
    if cda.sensor_D_io_error == True:
        ioErr = ioErr + " D "
        ioCnt = ioCnt + 1

    if ioCnt > 0:
        if ioCnt == 4:
            # If 4 it means power lost to all sensors
            if cda.sensor_lost_power_msg_cnt == 0:
                msg = config.get("Pzem","sensor_lost_power_msg")
                msgOut = []
                msgOut.append(msg)
                smsHandler.sendSMS(config.get("Developer","phones"), msgOut, "Developer")
                cda.sensor_lost_power_msg_cnt = cda.sensor_lost_power_msg_cnt + 1
            else:
                cda.sensor_lost_power_msg_cnt = cda.sensor_lost_power_msg_cnt + 1
                if cda.sensor_lost_power_msg_cnt > int(config.get("Pzem","sensor_lost_power_reset_count")):
                    cda.sensor_lost_power_msg_cnt = 0
        else:
            if cda.sensor_io_error_msg_cnt == 0:
                msg = config.get("Pzem","sensor_io_error_msg") + " " + ioErr
                msgOut = []
                msgOut.append(msg)
                smsHandler.sendSMS(config.get("Developer","phones"), msgOut, "Developer")
                cda.sensor_io_error_msg_cnt = cda.sensor_io_error_msg_cnt + 1
            else:
                cda.sensor_io_error_msg_cnt = cda.sensor_io_error_msg_cnt + 1
                if cda.sensor_io_error_msg_cnt > int(config.get("Pzem","sensor_io_error_reset_count")):
                    cda.sensor_io_error_msg_cnt = 0


def checkMsg(msg):
    try:
        global smsMsg
        if msg != "noMsg":
            cda.smsMsg.append(msg)     
    except Exception as e:
        logger.put_msg("E",f"checkThresholds.checkMsg ERROR: {e}")


def checkSMS():
    try:
        # Should SMS be sent
        if (len(cda.smsMsg) > 0):
            numbers = config.get("Maintenance","phones")
            # Pass phone numbers and message array to handler
            smsHandler.sendSMS(numbers, cda.smsMsg, 'Maintenance')
    except Exception as e:
        logger.put_msg("E",f"checkThresholds.checkSMS ERROR: {e}")   
	     

def voltage(data, id):
    try:
        # Check if pumpA has voltage/electricity
        if (data[0] == 0):
            if id == "A":
                cda.aNoV = cda.aNoV + 1
                if cda.aNoV > int(config.get("Limits","no_voltage")):
                    cda.aNoV = 0
                    return "Pump " + id + " " + config.get("Limits","no_voltage_msg")
            elif id == "B":
                cda.bNoV = cda.bNoV + 1
                if cda.bNoV > int(config.get("Limits","no_voltage")):
                    cda.bNoV = 0
                    return "Pump " + id + " " +config.get("Limits","no_voltage_msg")
            elif id == "C":
                cda.cNoV = cda.cNoV + 1
                if cda.cNoV > int(config.get("Limits","no_voltage")):
                    cda.cNoV = 0
                    return "Alarm " + config.get("Limits","no_voltage_msg")

        return "noMsg"
    except Exception as e:
        logger.put_msg("E",f"checkThresholds.voltage ERROR: {e}")
	
	
# Check if pump has powered on lately
def power(data,id):
    try:
        # Check if pumpA has power
        if (data[1] == 0):
            if id == "A":
                cda.aNoP = cda.aNoP + 1
                if cda.aNoP > int(config.get("Limits","no_power")):
                    cda.aNoP = 0
                    return "Pump " + id + " " + config.get("Limits","no_power_msg")
            elif id == "B":
                cda.bNoP = cda.bNoP + 1
                if cda.bNoP > int(config.get("Limits","no_power")):
                    cda.bNoP = 0
                    return "Pump " + id + " " + config.get("Limits","no_power_msg")

        return "noMsg"
    except Exception as e:
        logger.put_msg("E",f"checkThresholds.power ERROR: {e}")