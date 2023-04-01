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
	
def checkTemperature(temp):
    try:
        cda.smsMsg = []
        # Check if Raspberry Pi temperature is too high
        if temp > int(config.get("Limits","temp_high")):
            cda.high_temp_cnt = cda.high_temp_cnt + 1
            if cda.high_temp_cnt > int(config.get("Limits","temp_high_cnt")):
                sms = []
                sms.append(config.get("Messages","temp_high_msg"))
                sms.append(config.get("Messages","temp_high_who"))
                cda.smsMsg.append(sms)
                cda.high_temp_cnt = 0
                smsHandler.checkSMS("temp")
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"checkTemperature() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"checkTemperature() {e}")
        	

def checkUPSCharge(charge):
    # Check if Raspberry Pi UPS has been charging for a long time
    try:
        cda.smsMsg = []
        if charge < 0:
            cda.ups_charge_cnt = cda.ups_charge_cnt + 1
            if cda.ups_charge_cnt > int(config.get("Limits","ups_charge_cnt")):
                sms = []
                sms.append(config.get("Messages","ups_charge_msg"))
                sms.append(config.get("Messages","ups_charge_who"))
                cda.smsMsg.append(sms)
                cda.ups_charge_cnt = 0
                smsHandler.checkSMS("ups_charge")
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"checkUPSCharge() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"checkUPSCharge() {e}")

	
def checkUPSPercent(pct):
    # Check if Raspberry Pi UPS percent is below level
    try:
        cda.smsMsg = []
        if pct < int(config.get("Limits","ups_percent")):
            cda.ups_percent_cnt = cda.ups_percent_cnt + 1
            if cda.ups_percent_cnt > int(config.get("Limits","ups_percent_cnt")):
                sms = []
                sms.append(config.get("Messages","ups_percent_msg"))
                sms.append(config.get("Messages","ups_percent_who"))
                cda.smsMsg.append(sms)
                cda.ups_percent_cnt = 0
                smsHandler.checkSMS("ups_percent")
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"checkUPSPercent() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"checkUPSPercent() {e}")
                   	

def checkPump(pzem_data,id):
    # Increment counters and check against thresholds.
    try:
        cda.smsMsg = []
        if id == "A": 
            if (pzem_data[0] == "nodata"):
                cda.aNoD = cda.aNoD + 1
                if cda.aNoD > int(config.get("Limits","no_data")):
                    sms = []
                    sms.append("Pump A " + config.get("Messages","no_data_msg"))
                    sms.append(config.get("Messages","no_data_who"))
                    cda.smsMsg.append(sms)
                    cda.aNoD = 0
                    smsHandler.checkSMS("no_data")
            else:
                # Check voltage
                if (pzem_data[0] == 0):
                    cda.aNoV = cda.aNoV + 1
                    if cda.aNoV > int(config.get("Limits","no_voltage")):
                        sms = []
                        sms.append("Pump A sensor " + config.get("Messages","no_voltage_msg"))
                        sms.append(config.get("Messages","no_voltage_who"))
                        cda.smsMsg.append(sms)
                        cda.aNoV = 0
                        smsHandler.checkSMS("no_voltage")

                # Check current (this is greater than zero when pump is using electricity)
                if (pzem_data[1] == 0):
                    cda.aNoP = cda.aNoP + 1
                    if cda.aNoP > int(config.get("Limits","no_power")):
                        sms = []
                        sms.append("Pump A " + config.get("Messages","no_power_msg"))
                        sms.append(config.get("Messages","no_power_who"))
                        cda.smsMsg.append(sms)
                        cda.aNoP = 0
                        smsHandler.checkSMS("no_power")

        elif id == "B": 
            if (pzem_data[0] == "nodata"):
                cda.bNoD = cda.bNoD + 1
                if cda.bNoD > int(config.get("Limits","no_data")):
                    sms = []
                    sms.append("Pump B " + config.get("Messages","no_data_msg"))
                    sms.append(config.get("Messages","no_data_who"))
                    cda.smsMsg.append(sms)
                    cda.bNoD = 0
                    smsHandler.checkSMS("no_data")
            else:
                # Check voltage
                if (pzem_data[0] == 0):
                    cda.bNoV = cda.bNoV + 1
                    if cda.bNoV > int(config.get("Limits","no_voltage")):
                        sms = []
                        sms.append("Pump B sensor " + config.get("Messages","no_voltage_msg"))
                        sms.append(config.get("Messages","no_voltage_who"))
                        cda.smsMsg.append(sms)
                        cda.bNoV = 0
                        smsHandler.checkSMS("no_voltage")

                # Check current (this is greater than zero when pump is using electricity)
                if (pzem_data[1] == 0):
                    cda.bNoP = cda.bNoP + 1
                    if cda.bNoP > int(config.get("Limits","no_power")):
                        sms = []
                        sms.append("Pump B " + config.get("Messages","no_power_msg"))
                        sms.append(config.get("Messages","no_power_who"))
                        cda.smsMsg.append(sms)
                        cda.bNoP = 0
                        smsHandler.checkSMS("no_power")

        elif id == "C": 
            if (pzem_data[0] == "nodata"):
                cda.cNoD = cda.cNoD + 1
                if cda.cNoD > int(config.get("Limits","no_data")):
                    sms = []
                    sms.append("Pump C " + config.get("Messages","no_data_msg"))
                    sms.append(config.get("Messages","no_data_who"))
                    cda.smsMsg.append(sms)
                    cda.cNoD = 0
                    smsHandler.checkSMS("no_data")
            else:
                # Check voltage
                if (pzem_data[0] == 0):
                    cda.cNoV = cda.cNoV + 1
                    if cda.cNoV > int(config.get("Limits","no_voltage")):
                        sms = []
                        sms.append("Pump C sensor " + config.get("Messages","no_voltage_msg"))
                        sms.append(config.get("Messages","no_voltage_who"))
                        cda.smsMsg.append(sms)
                        cda.cNoV = 0
                        smsHandler.checkSMS("no_voltage")

                # Check current (this is greater than zero when pump is using electricity)
                if (pzem_data[1] == 0):
                    cda.cNoP = cda.cNoP + 1
                    if cda.cNoP > int(config.get("Limits","no_power")):
                        sms = []
                        sms.append("Pump C " + config.get("Messages","no_power_msg"))
                        sms.append(config.get("Messages","no_power_who"))
                        cda.smsMsg.append(sms)
                        cda.cNoP = 0
                        smsHandler.checkSMS("no_power")

        elif id == "D": 
            if (pzem_data[0] == "nodata"):
                cda.dNoD = cda.dNoD + 1
                if cda.dNoD > int(config.get("Limits","no_data")):
                    sms = []
                    sms.append("Pump D " + config.get("Messages","no_data_msg"))
                    sms.append(config.get("Messages","no_data_who"))
                    cda.smsMsg.append(sms)
                    cda.dNoD = 0
                    smsHandler.checkSMS("no_data")
            else:
                # Check voltage
                if (pzem_data[0] == 0):
                    cda.dNoV = cda.dNoV + 1
                    if cda.dNoV > int(config.get("Limits","no_voltage")):
                        sms = []
                        sms.append("Pump D sensor " + config.get("Messages","no_voltage_msg"))
                        sms.append(config.get("Messages","no_voltage_who"))
                        cda.smsMsg.append(sms)
                        cda.dNoV = 0
                        smsHandler.checkSMS("no_voltage")

                # Check current (this is greater than zero when pump is using electricity)
                if (pzem_data[1] == 0):
                    cda.dNoP = cda.dNoP + 1
                    if cda.dNoP > int(config.get("Limits","no_power")):
                        sms = []
                        sms.append("Pump D " + config.get("Messages","no_power_msg"))
                        sms.append(config.get("Messages","no_power_who"))
                        cda.smsMsg.append(sms)
                        cda.dNoP = 0
                        smsHandler.checkSMS("no_power")

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"checkPump() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"checkPump() {e}")


def checkSensors():
    try:
        cda.smsMsg = []
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
            cda.sensor_connect_error_cnt = cda.sensor_connect_error_cnt + 1
            if cda.sensor_connect_error_cnt > int(config.get("Limits","sensor_connect_error")):
                sms = []
                sms.append(config.get("Messages","sensor_connect_error_msg") + connErr)
                sms.append(config.get("Messages","sensor_connect_error_who"))
                cda.smsMsg.append(sms)
                cda.sensor_connect_error_cnt = 0
                smsHandler.checkSMS("connect_error")
        
        cda.smsMsg = []
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
            if ioCnt == int(config.get("Pzem","total_sensors")):
                # If all sensors have I/O error it means power was lost
                cda.all_sensors_io_error_cnt = cda.all_sensors_io_error_cnt + 1
                if cda.all_sensors_io_error_cnt > int(config.get("Limits","all_sensors_io_error")):
                    sms = []
                    sms.append(config.get("Messages","all_sensors_io_error_msg") + connErr)
                    sms.append(config.get("Messages","all_sensors_io_error_who"))
                    cda.smsMsg.append(sms)
                    cda.all_sensors_io_error_cnt = 0
                    smsHandler.checkSMS("all_sensors_io_error")
            else:
                cda.sensor_io_error_cnt = cda.sensor_io_error_cnt + 1
                if cda.sensor_io_error_cnt > int(config.get("Limits","sensor_io_error")):
                    sms = []
                    sms.append(config.get("Messages","sensor_io_error_msg") + connErr)
                    sms.append(config.get("Messages","sensor_io_error_who"))
                    cda.smsMsg.append(sms)
                    cda.sensor_io_error_cnt = 0
                    smsHandler.checkSMS("io_error")

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"checkSensors() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"checkSensors() {e}")
