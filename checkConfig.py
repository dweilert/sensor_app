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
  2023/06/26  DaW             Removed three def's checkDiag, diagInfo, and 
                              getRAMinfo and moved them to a new util.py file.

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
from datetime import datetime


import config
import logger
import commonDataArea as cda


if __name__ == "__main__":
    # reset_usb()
    try:
        # get current date
        now = datetime.now()
        print("------------")
        print("Checking Monitor config.ini a at: " +
              now.strftime("%m/%d/%Y, %H:%M:%S"))

        cda.current_date = now.strftime("%Y_%m_%d")

        time.sleep(5)
        # Read config.ini file for parameters
        config_status = config.readConfig()
        if config_status == False:
            print("FATAL ERROR starting unable to read config file")
            sys.exit()
        else:
            print("Read config file OK")
            print(f"log_console: {config.get('Log', 'log_console')}")
            print(f"max-records: {config.get('Log', 'max_records')}")
            sys.exit()

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg(
            "E", f"__main__ Exception type: {exception_type} File name: {filename} Line number: {line_number}")
        logger.msg("E", f"__main__ {e}")
        time.sleep(5)
