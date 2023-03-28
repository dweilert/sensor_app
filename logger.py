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
import smsHandler

# Data array of pzem-16 sensor data
logData = []
oldData = 0


# def getParms():
#     try:
#         cda.log_dir = config.get("Log","log_directory")
#         cda.log_base = config.get("Log","log_base")
#         cda.log_sms = config.get("Log","log_sms_number")
        
#         if cda.log_dir[-1] != "/":
#             cda.log_dir = cda.log_dir + "/"

#         now = datetime.now()
#         new = now.strftime("%Y_%m_%d")

#         if cda.log_date == "":
#             cda.log_date = new

#         # Check if it is a new day if so swap to new file
#         if cda.log_date != new:
#             cda.log_old_name = cda.log_file_name
#             cda.log_file_name = cda.log_dir+cda.log_base+"_"+cda.log_date+".log"
#         else:
#             cda.log_file_name = cda.log_dir+cda.log_base+"_"+cda.log_date+".log"

#         if cda.log_first_time == True:
#             cda.log_first_time = False

#             now = datetime.now()
#             ts = now.strftime("%Y-%m-%d %H:%M:%S.%f")
#             #sys.stdout.write(f"{ts} (I) : Interval count({iCnt})")
#             #print(f"{ts} (I) : Log message file: {cda.log_file_name}")

#     except Exception as e:
#         exception_type, exception_object, exception_traceback = sys.exc_info()
#         filename = exception_traceback.tb_frame.f_code.co_filename
#         line_number = exception_traceback.tb_lineno
#         print(f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")                       
#         print(f"Get Logger parms error: {e}")
#         return


def put_msg(lvl, msg):
    try:
        #getParms()
        save = False
        now = datetime.now()
        ts = now.strftime("%Y-%m-%d %H:%M:%S.%f")

        if lvl == "i" or lvl == "info" or lvl == "I":
            lvl = "(I) : "
            save = True
        elif lvl == "e" or lvl == "error" or lvl == "E":
            lvl = "(E) : "
            save = True
        elif lvl == "d" or lvl == "debug" or lvl == "D":
            lvl = " (D) : "
            save = False

        # Is message saved or output to console
        if save == True:
            # file1 = open(cda.log_file_name, mode="a", encoding="utf-8")
            # file1.write(ts + " " + lvl + msg + "\n")
            # file1.close()
            # file1 = None
            # # Should msg also be shown on console
            # if config.get("Log","log_console") == "true" or config.get("Log","log_console") == "True" or config.get("Log","log_console") == "TRUE":
            #     print(ts + " " + lvl + msg)
            cda.log_messages.append(ts + " " + lvl + msg)
            if config.get("Log","log_console") == "true" or config.get("Log","log_console") == "True" or config.get("Log","log_console") == "TRUE":
                print(ts + " " + lvl + msg)

            if len(cda.log_messages) > int(config.get("Log","max_records")):
                for i in range(int(config.get("Log","drop_count"))): 
                    cda.log_messages.pop(i)
        else:
            print(ts + lvl + msg)
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print(f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")
        cda.log_msg.append(f"Logger - Exception type: {exception_type} File name: {filename} Line number: {line_number}")            
        cda.log_msg.append(f"Dropped msg: {msg}")


def sms_msg(msg):
    try:
        smsHandler.sendSMS(cda.log_sms, msg, "Developer")
    except Exception as e:
        print(f"logger.sms_msg ERROR: {e}")
