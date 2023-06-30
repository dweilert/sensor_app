#!/usr/bin/env python3

"""
Author: Dave Weilert
Copyright(C) 2023 Freeware
Date: 3/19/2023

REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------
  2023/03/19  DaW             Initial creation
  2023/06/22  DaW             Added checkAmps function to check for high or 
                              low amps on each pump

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
from datetime import datetime

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

# SMS message array
cda.smsMsg = []


def checkAmps(i):
    try:
        cda.smsMsg = []
        high = 0
        low = 99
        # Check pump amps for too high or to low
        if i == "A":
            high = cda.pumpA_amp_high
            low = cda.pumpA_amp_low
        else:
            high = cda.pumpB_amp_high
            low = cda.pumpB_amp_low

        if high > int(config.get("Limits", "amps_high")):
            sms = []
            sms.append(config.get("Messages", "amps_high_msg"))
            sms.append(config.get("Messages", "amps_high_who"))
            cda.smsMsg.append(sms)
            smsHandler.checkSMS("amps")

        if low < int(config.get("Limits", "amps_low")):
            sms = []
            sms.append(config.get("Messages", "amps_low_msg"))
            sms.append(config.get("Messages", "amps_low_who"))
            cda.smsMsg.append(sms)
            smsHandler.checkSMS("amps")

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E", f"checkAmps() Exception type: {exception_type} File name: {filename} Line number: {line_number}")
        logger.msg("E", f"checkAmps() {e}")


def checkTemperature(temp):
    try:
        cda.smsMsg = []
        # Check if Raspberry Pi temperature is too high
        if temp > int(config.get("Limits", "temp_high")):
            cda.high_temp_cnt = cda.high_temp_cnt + 1
            if cda.high_temp_cnt > int(config.get("Limits", "temp_high_cnt")):
                sms = []
                sms.append(config.get("Messages", "temp_high_msg"))
                sms.append(config.get("Messages", "temp_high_who"))
                cda.smsMsg.append(sms)
                cda.high_temp_cnt = 0
                smsHandler.checkSMS("temp")
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E", f"checkTemperature() Exception type: {exception_type} File name: {filename} Line number: {line_number}")
        logger.msg("E", f"checkTemperature() {e}")


def checkUPSPercent(pct):
    # Check if Raspberry Pi UPS percent is below level
    try:
        cda.smsMsg = []
        if pct < int(config.get("Limits", "ups_percent")):
            sms = []
            msg = config.get("Messages", "ups_percent_msg") + " " + config.get("Limits", "ups_percent") + " percent"
            sms.append(msg)
            sms.append(config.get("Messages", "ups_percent_who"))
            cda.smsMsg.append(sms)
            cda.ups_percent_cnt = 0
            smsHandler.checkSMS("ups_percent")
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E", f"checkUPSPercent() Exception type: {exception_type} File name: {filename} Line number: {line_number}")
        logger.msg("E", f"checkUPSPercent() {e}")


def checkData(pzem_data, id):
    now = datetime.now()
    nowTime = now.strftime("%H:%M:%S")
    # Increment counters and check against thresholds.
    try:
        cda.smsMsg = []
        cda.from_sensor = id
        if id == "A":
            if (len(pzem_data) == 0):
                cda.aNoD = cda.aNoD + 1
                if cda.aNoD > int(config.get("Limits", "no_data")):
                    sms = []
                    sms.append("Pump A check " + config.get("Messages", "no_data_msg"))
                    sms.append(config.get("Messages", "no_data_who"))
                    cda.smsMsg.append(sms)
                    cda.aNoD = 0
                    smsHandler.checkSMS("no_data")
            else:
                # Check current (this is greater than zero when pump is using electricity)
                if (pzem_data[1] == 0):
                    cda.aNoP = cda.aNoP + 1
                    if cda.aNoP > int(config.get("Limits", "no_power")):
                        sms = []
                        sms.append("Pump A check " + config.get("Messages", "no_power_msg"))
                        sms.append(config.get("Messages", "no_power_who"))
                        cda.smsMsg.append(sms)
                        cda.aNoP = 0
                        smsHandler.checkSMS("no_power_a")
                else:
                    cda.aNoP = 0

        elif id == "B":
            if (len(pzem_data) == 0):
                cda.bNoD = cda.bNoD + 1
                if cda.bNoD > int(config.get("Limits", "no_data")):
                    sms = []
                    sms.append("Pump B check " + config.get("Messages", "no_data_msg"))
                    sms.append(config.get("Messages", "no_data_who"))
                    cda.smsMsg.append(sms)
                    cda.bNoD = 0
                    smsHandler.checkSMS("no_data")
            else:
                # Check current (this is greater than zero when pump is using electricity)
                if (pzem_data[1] == 0):
                    cda.bNoP = cda.bNoP + 1
                    if cda.bNoP > int(config.get("Limits", "no_power")):
                        sms = []
                        sms.append("Pump B check " + config.get("Messages", "no_power_msg"))
                        sms.append(config.get("Messages", "no_power_who"))
                        cda.smsMsg.append(sms)
                        cda.bNoP = 0
                        smsHandler.checkSMS("no_power_b")
                    else:
                        cda.bNoP = 0

        elif id == "C":
            if (len(pzem_data) == 0):
                cda.cNoD = cda.cNoD + 1
                if cda.cNoD > int(config.get("Limits", "no_data")):
                    sms = []
                    sms.append("High-level alarm check " + config.get("Messages", "no_data_msg"))
                    sms.append(config.get("Messages", "no_data_who"))
                    cda.smsMsg.append(sms)
                    cda.cNoD = 0
                    smsHandler.checkSMS("no_data")
            else:
                # Check current, if found the high-level alarm is on
                if (pzem_data[1] > 0):
                    cda.cNoP = cda.cNoP + 1
                    if cda.cNoP > int(config.get("Limits", "high_level_alarm")):
                        sms = []
                        sms.append(config.get("Messages", "high_level_alarm_msg"))
                        sms.append(config.get("Messages", "high_level_alarm_who"))
                        cda.smsMsg.append(sms)
                        cda.cNoP = 0
                        smsHandler.checkSMS("high_level_alarm")
                    else:
                        cda.cNoP = 0

        elif id == "D":
            if (len(pzem_data) == 0):
                cda.dNoD = cda.dNoD + 1
                if cda.dNoD > int(config.get("Limits", "no_data")):
                    sms = []
                    sms.append("Overall power check " + config.get("Messages", "no_data_msg"))
                    sms.append(config.get("Messages", "no_data_who"))
                    cda.smsMsg.append(sms)
                    cda.dNoD = 0
                    smsHandler.checkSMS("no_data")
            else:
                # Check current
                if (pzem_data[1] == 0):
                    cda.dNoP = cda.dNoP + 1
                    if cda.dNoP > int(config.get("Limits", "no_overall_power")):
                        sms = []
                        sms.append(config.get("Messages", "no_overall_power_msg"))
                        sms.append(config.get("Messages", "no_overall_power_who"))
                        cda.smsMsg.append(sms)
                        cda.dNoP = 0
                        smsHandler.checkSMS("no_overall_power")
                    else:
                        cda.dNoP = 0

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E", f"checkPump() Exception type: {exception_type} File name: {filename} Line number: {line_number}")
        logger.msg("E", f"checkPump() {e}")
