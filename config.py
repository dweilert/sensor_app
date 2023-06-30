"""
Author: Dave Weilert
Copyright(C) 2023 Freeware
Date: 3/19/2023

REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------
  2023/03/23  DaW             Initial creation
  2023/06/21  DaW             1. Reformat exception error for better understanding
                              2. Removed hard coded loaction for config.ini. Changed to
                              CWD (current working directory)/config.ini 

OVERVIEW:
    Module read configuration file config.ini. 

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

import commonDataArea as cda
import configparser
import logger
import sys
import os

configI = configparser.ConfigParser()


def readConfig():
    try:
        # dir_path = os.path.dirname(os.path.realpath(__file__))
        # cwd_path = os.getcwd()
        # logger.msg("I", "os.path  : " + dir_path)
        # logger.msg("I", "os.getcwd: " + cwd_path)
        # configI.read(cwd_path + "/config.ini")
        configI.read("/home/bob/sensor_app/config.ini")
        # Set debug flag from config.ini file
        cVal = configI.get("Debug", "status")
        if cVal == "true" or cVal == True:
            cda.debug = True
        else:
            cda.debug = False

        setValues()
        return True
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg(
            "E", f"readConfig() Exception type: {exception_type} File name: {filename} Line number: {line_number}")
        logger.msg("E", f"readConfig() {e}")
        return False


def get(k1, k2):
    try:
        data = configI[k1][k2]
        return data
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg(
            "E", f"get() Exception type: {exception_type} File name: {filename} Line number: {line_number}")
        logger.msg("E", f"get() Type : {k1}")
        logger.msg("E", f"get() Value: {k2}")
        return "err"


def setValues():
    try:
        wait_secs = int(get("Interval", "wait_to_check_sensors_seconds"))
        resend_delay = int(get("Interval", "wait_to_resend_sms_hours"))
        resend_delay = resend_delay * 3600   # multiple hours times seconds in hours
        cda.resend_wait = round(resend_delay / wait_secs)
        cda.write_msg_to_console = get("Log", "write_msg_to_console")
        cda.write_msg_to_file = get("Log", "write_msg_to_file")

        # logger.msg("I",f"Resend hours: {resend_delay} Resend seconds: {cda.resend_wait}")
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg(
            "E", f"setValues() Exception type: {exception_type} File name: {filename} Line number: {line_number}")
        logger.msg("E", f"setValues() {e}")
