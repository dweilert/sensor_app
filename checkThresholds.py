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

GENERAL INFORMATION:
    PREREQUISITES
        n/a
"""

import os
import sys
import config
import common
import smsHandler
import dataHandler
import logger

# Voltage
common.aNoV = 0
common.bNoV = 0
common.no_voltage_max = 1
NO_VOLTAGE_MSG = " has lost electricity"

# Power
common.aNoP = 0
common.bNoP = 0
common.no_power_max = 1
NO_POWER_MSG = " has not run lately"

# Data
common.aNoD = 0
common.bNoD = 0
common.no_data_max = 1
NO_DATA_MSG = " is not returning sense data"

# SMS message array
common.smsMsg = []
	
	
def check(pzem_data):
    try:
        # Clear SMS messages
        common.smsMsg = []
        # Increment counters and check against thresholds.

        # pumpA, 
        if (pzem_data[0][0] == "nodata"):
            common.aNoD = common.aNoD + 1
            if common.aNoD > common.no_data_max:
                common.smsMsg.append("Pump A" + NO_DATA_MSG)
                common.aNoD = 0
        else:
            msg = voltage(pzem_data[0],"A")
            checkMsg(msg)
            msg = power(pzem_data[0],"A")
            checkMsg(msg)
       
        # pumpB
        if (pzem_data[1][0] == "nodata"):
            common.bNoD = common.bNoD + 1
            if common.bNoD > common.no_data_max:
                common.smsMsg.append("Pump B" + NO_DATA_MSG)
                common.bNoD = 0
        else:
            msg = voltage(pzem_data[1],"B")
            checkMsg(msg)
            msg = power(pzem_data[1],"B")
            checkMsg(msg)

        # pumpC
        #TO DO: Add logic to check this sensor data

        # pumpD
        #TO DO: Add logic to check this sensor data


        checkSMS()
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno

        logger.put_msg("E",f"Exception type: {exception_type}")
        logger.put_msg("E",f"File name: {filename}")
        logger.put_msg("E",f"Line number: {line_number}")
        logger.put_msg("E",f"checkThresholds.check ERROR: {e}")
    

def checkMsg(msg):
    try:
        global smsMsg
        if msg != "noMsg":
            common.smsMsg.append(msg)     
    except Exception as e:
        logger.put_msg("E",f"checkThresholds.checkMsg ERROR: {e}")


def checkSMS():
    try:
        # Should SMS be sent
        hl = len(common.smsMsg)
        if (len(common.smsMsg) > 0):
            numbers = config.get("Maintenance","phones")
            # Pass phone numbers and message array to handler
            smsHandler.sendSMS(numbers, common.smsMsg, 'Maintenance')
    except Exception as e:
        logger.put_msg("E",f"checkThresholds.checkSMS ERROR: {e}")   
	     

def voltage(data,pump):
    try:
        # Check if pumpA has voltage/electricity
        if (data[0] == 0):
            if pump == "A":
                common.aNoV = common.aNoV + 1
                if common.aNoV > common.no_voltage_max:
                    common.aNoV = 0
                    return "Pump " + pump + NO_VOLTAGE_MSG
            else:
                common.bNoV = common.bNoV + 1
                if common.bNoV > common.no_voltage_max:
                    common.bNoV = 0
                    return "Pump " + pump + NO_VOLTAGE_MSG

        return "noMsg"
    except Exception as e:
        logger.put_msg("E",f"checkThresholds.voltage ERROR: {e}")
	
	
# Check if pump has powered on lately
def power(data,pump):
    try:
        # Check if pumpA has power
        if (data[1] == 0):
            if pump == "A":
                common.aNoP = common.aNoP + 1
                if common.aNoP > common.no_power_max:
                    common.aNoP = 0
                    return "Pump " + pump + NO_POWER_MSG
            else:
                common.bNoP = common.bNoP + 1
                if common.bNoP > common.no_power_max:
                    common.bNoP = 0
                    return "Pump " + pump + NO_POWER_MSG

        return "noMsg"
    except Exception as e:
        logger.put_msg("E",f"checkThresholds.power ERROR: {e}")