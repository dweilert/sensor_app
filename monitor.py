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

import os
import time
import subprocess
import sys
import configparser
from datetime import datetime

import config
import common
import pzemHandler
import checkThresholds
import upsHandler
import logger


def getPorts():
    try:
        common.portA = "na"
        common.portB = "na"
        common.portC = "na"
        common.portD = "na"
        pzemHandler.find_usb_ports()
        common.getPortsCnt = common.getPortsCnt + 1
    except Exception as e:
        logger.put_msg("E","monitor.getPorts ERROR: " + e)
        #time.sleep(1)

def mainLine():
    try:
        while True:
            getPorts()
            cnt = 0   
            if (common.portA != "na"):
                cnt = cnt + 1
            if (common.portB != "na"):
                cnt = cnt + 1
            if (common.portC != "na"):
                cnt = cnt + 1
            if (common.portD != "na"):
                cnt = cnt + 1    

            # check if any ports were located
            if cnt > 0:
                break
            else:	    
                time.sleep(int(common.wait_to_check_for_ports))

        iCnt = 0
        rtn = []
        while True:
            iCnt = iCnt + 1
            if common.portA != "na": 
                rtn.append(pzemHandler.monitor(common.portA,"A"))
            if common.portB != "na": 
                rtn.append(pzemHandler.monitor(common.portB,"B"))
            if common.portC != "na": 
                rtn.append(pzemHandler.monitor(common.portB,"C")) 
            if common.portD != "na": 
                rtn.append(pzemHandler.monitor(common.portB,"D"))           
            # Evaluate the collected sensor data
            checkThresholds.check(rtn)
            rtn = []
            ups = upsHandler.getUPSInfo()
            # Log iteration and wait
            logger.put_msg("I", "Interval count: " + str(iCnt) + " UPS Current: " + str(common.upsCurrent))
            time.sleep(int(common.wait_to_check_sensors))
            
    except Exception as e:
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
        logger.put_msg("E",f"monitor.__main__ Exception: {e}")    
        time.sleep(5)
        mainLine()

