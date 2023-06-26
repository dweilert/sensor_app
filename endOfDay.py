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

import sys

import config
import logger
import commonDataArea as cda
import smsHandler

def getDailyData():
    try:
        result = "---- Daily stats ---- \n"
        result = result + "Pump A -\n"
        result = result + "  Used count: " + cda.daily_pump_A_cnt + "\n"
        result = result + "  High amps : " + cda.daily_pump_A_high_amp + "\n"
        result = result + "Pump B -\n"
        result = result + "  Used count: " + cda.daily_pump_B_cnt + "\n"
        result = result + "  High amps : " + cda.daily_pump_B_high_amp + "\n"
        return result

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"sendInfo() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"sendInfo() {e}")

def sendDailyInfo():
    try:
        sms = []
        sms.append(config.get("Messages","end_of_day_msg") + getDailyData())
        sms.append(config.get("Messages","end_of_day_who"))
        cda.smsMsg.append(sms)
        smsHandler.sendSMS() 

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"sendInfo() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"sendInfo() {e}")
