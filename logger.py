"""
Author: Dave Weilert
Copyright(C) 2023 Freeware
Date: 3/19/2023

REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------
  2023/03/23  DaW             Initial creation 

OVERVIEW:
    Custom logging module.  Module receive log message, stores the message
    and calls smsHandler to send SMS messages if necessary. 

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
from datetime import datetime

import commonDataArea as cda
import config

# Data array of pzem-16 sensor data
logData = []


def msg(lvl, msg):
    print(msg)
    try:
        now = datetime.now()
        ts = now.strftime("%Y-%m-%d %H:%M:%S.%f")

        if lvl == "i" or lvl == "info" or lvl == "I":
            lvl = "(I) : "
        elif lvl == "e" or lvl == "error" or lvl == "E":
            lvl = "(E) : "
        elif lvl == "d" or lvl == "debug" or lvl == "D":
            lvl = "(D) : "

        cda.log_messages.append(ts + " " + lvl + msg)
        if cda.write_msg_to_console == True:
            print(ts + " " + lvl + msg)

        # Determine if maximum log entries are in array and remove some
        # if reached
        if len(cda.log_messages) > int(config.get("Log", "max_records")):
            wrapLogs()

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print(
            f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")
        cda.log_messages.append(
            f"Logger - Exception type: {exception_type} File name: {filename} Line number: {line_number}")
        cda.log_messages.append(f"Dropped msg: {msg}")


def wrapLogs():
    try:
        hl = len(cda.log_messages)
        if (hl > 10):
            sp = round(hl/2)
            newLog = []
            ptr = sp
            for i in sp:
                newLog.append(cda.log_messages[ptr])
                ptr = ptr + 1

            cda.log_messages = newLog
            newLog = None
            return True
        else:
            return True

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print(
            f"wrapLogs() Exception type: {exception_type} File name: {filename} Line number: {line_number}")
        print(f"wrapLogs() {e}")
        cda.log_messages = []
        return False
