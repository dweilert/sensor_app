"""
Author: Dave Weilert
Copyright(C) 2023 Freeware
Date: 3/19/2023

REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------
  2023/03/19  DaW             Initial creation 

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

import time
import sys
from datetime import datetime

import config
import commonDataArea as cda
import pzemHandler
import smsHandler
import checkThresholds
import upsHandler
import logger


def getPorts():
    try:
        pzemHandler.find_usb_ports()
        cda.getPortsCnt = cda.getPortsCnt + 1
        if cda.getPortsCnt > int(config.get("Limits","no_ports")):
            smsHandler.sendSMS(config.get("Limits","no_ports_number"), config.get("Limits","no_ports_msg"), config.get("Limits","no_ports_who"))
            cda.getPortsCnt = 0
    except Exception as e:
        logger.put_msg("E","monitor.getPorts ERROR: " + e)


def mainLine():
    try:
        while True:
            getPorts()
            cnt = 0   
            if (cda.portA != "na"):
                cnt = cnt + 1
            if (cda.portB != "na"):
                cnt = cnt + 1
            if (cda.portC != "na"):
                cnt = cnt + 1
            if (cda.portD != "na"):
                cnt = cnt + 1    

            # check if any ports were located
            if cnt > 0:
                break
            else:	    
                time.sleep(int(config.get("Interval","wait_to_check_for_ports")))

        iCnt = 0
        rtn = []
        while True:
            iCnt = iCnt + 1
            rtn = []
            rtn = pzemHandler.monitor(cda.portA,"A")
            if config.get("Debug","show_regs") == "true":
                logger.put_msg("D",f"Port A Regs: {rtn}")
            checkThresholds.check(rtn,"A")
            rtn = []
            rtn = pzemHandler.monitor(cda.portB,"B")
            if config.get("Debug","show_regs") == "true":
                logger.put_msg("D",f"Port B Regs: {rtn}")
            checkThresholds.check(rtn,"B")
            rtn = []
            rtn = pzemHandler.monitor(cda.portC,"C") 
            if config.get("Debug","show_regs") == "true":
                logger.put_msg("D",f"Port C Regs: {rtn}")
            checkThresholds.check(rtn,"C")
            rtn = []
            rtn = pzemHandler.monitor(cda.portD,"D")          
            if config.get("Debug","show_regs") == "true":
                logger.put_msg("D",f"Port D Regs: {rtn}")
            checkThresholds.check(rtn,"D")

            ups = upsHandler.getUPSInfo()
            # Log iteration and wait

            #print(f"Interval count: {iCnt}", end="")
            now = datetime.now()
            ts = now.strftime("%Y-%m-%d %H:%M:%S.%f")
            #sys.stdout.write(f"{ts} (I) : Interval count({iCnt})")
            print(f"{ts} (I) : Interval count({iCnt})")

            time.sleep(int(config.get("Interval","wait_to_check_sensors")))
            
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.put_msg("E",f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.put_msg("E",f"monitor.mainLine Exception: {e}")
        time.sleep(15)
        mainLine()
	

# Main section 
if __name__ == "__main__":
    # reset_usb()
    try:
        # Read config.ini file for parameters
        config.readConfig()
        mainLine()
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.put_msg("E",f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")               
        logger.put_msg("E",f"monitor.__main__ Exception: {e}")    
        time.sleep(5)
        mainLine()
