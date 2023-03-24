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

import os
import time
from datetime import datetime

import common
import config
import smsHandler

# Data array of pzem-16 sensor data
logData = []
oldData = 0


def getParms():
    try:
        if common.log_dir[-1] != "/":
            common.log_dir = common.log_dir + "/"

        now = datetime.now()
        new = now.strftime("%Y_%m_%d")

        if common.log_date == "":
            common.log_date = new

        # Check if it is a new day if so swap to new file
        if common.log_date != new:
            common.log_old_name = common.log_file_name
            common.log_file_name = common.log_dir+common.log_base+"_"+common.log_date+".log"
        else:
            common.log_file_name = common.log_dir+common.log_base+"_"+common.log_date+".log"

        if common.log_first_time == True:
            common.log_first_time = False
            print("Log message file: "+common.log_file_name)

    except Exception as e:
        print(f"Get Logger parms error: {e}")
        return


def put_msg(lvl, msg):
    try:
        getParms()
        save = True
        now = datetime.now()
        ts = now.strftime("%Y-%m-%d %H:%M:%S.%f")

        if lvl == "i" or lvl == "info" or lvl == "I":
            lvl = "(Info) : "
        elif lvl == "e" or lvl == "error" or lvl == "E":
            lvl = "(Error) : "
        elif lvl == "d" or lvl == "debug" or lvl == "D":
            lvl = " : "
            save = False

        # Is message saved or output to console
        if save == True:
            file1 = open(common.log_file_name, mode="a", encoding="utf-8")
            file1.write(ts + " " + lvl + msg + "\n")
            file1.close()
            file1 = None
            # Should msg also be shown on console
            if config.get("Log","log_console") == "true" or config.get("Log","log_console") == "True" or config.get("Log","log_console") == "TRUE":
                print(ts + " " + lvl + msg)
        else:
            print(ts + lvl + msg)
    except Exception as e:
        print(f"logger.put_msg ERROR:  {e}")
        print(f"logger.put_msg Dropped msg: {msg}")


def sms_msg(msg):
    try:
        smsHandler.sendSMS(common.log_sms, msg, "Developer")
    except Exception as e:
        print(f"logger.sms_msg ERROR: {e}")
