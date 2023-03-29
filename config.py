"""
Author: Dave Weilert
Copyright(C) 2023 Freeware
Date: 3/19/2023

REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------
  2023/03/23  DaW             Initial creation 

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

configI = configparser.ConfigParser()

def readConfig():
    try:
        #configI = configparser.ConfigParser()
        configI.read("/home/bob/sensor_app/config.ini")
        # Set debug flag from config.ini file
        if configI.get("Debug","status") == "true":
            cda.debug = True
        else:
            cda.debug = False
        return True
    except Exception as e:
        logger.put_msg("E",f"config.readConfig ERROR: {e}")
        return False

def get(k1, k2):
    try:
        data = configI[k1][k2]
        return data
    except Exception as e:
        logger.put_msg("E",f"config.get ERROR: {e}")
        return  "err"
