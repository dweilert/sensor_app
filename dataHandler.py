"""
Author: Dave Weilert
Copyright(C) 2023 Freeware
Date: 3/19/2023

REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------
  2023/03/23  DaW             Initial creation 

OVERVIEW:
    Module to store data in files.

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
import sys
import time
from datetime import datetime

import common
import config
import logger
import awsHandler


def saveData(data, id):
    try:
        now = datetime.now()
        new = id + "," + now.strftime("%m/%d/%Y-%H:%M:%S")
        for item in data:
            new = new + "," + str(item) 
        
        row = new.split(",")
        # Record format for A & B  : 
        #id, start date, start energy, stop date, latest energy, energy used
        record = {}
        energy = 0
        if row[0] == "A":
            # Check if Current row[3] is seen 	
            if int(row[3]) > 0:
                if common.pumpA_status == "OFF":
                    common.pumpA_status = "ON"		
                    common.pumpA_start = row[1]
                    common.pumpA_energy_start = row[7]
                else:
                    common.pumpA_energy_latest = row[7]
                    common.pumpA_stop = row[1]		    		    				    
            else:		
                if common.pumpA_status == "ON":
                    common.pumpA_stop = row[1]
                    energy = int(common.pumpA_energy_latest) - int(common.pumpA_energy_start)
                    record['p'] = "A"                                          # pump
                    record['sd'] = common.pumpA_start                          # start_date
                    record['se'] = common.pumpA_energy_start                   # start energy 
                    record['ee'] = common.pumpA_stop                           # end date 
                    record['ee'] = common.pumpA_energy_latest                  # end energy
                    record['ue'] = str(energy)                                 # used energy
                    # Reset pump data
                    common.pumpA_status = "OFF"
                    common.pumpA_start = ""
                    common.pumpA_energy_start = ""
                    common.pumpA_stop = ""
                    common.pumpA_energy_latest = ""
                    # Send data to AWS
                    awsHandler.putSensorData(record)		    		
        elif row[0] == "B":
            # Check if Current is seen 	
            if int(row[3]) > 0:
                if common.pumpB_status == "OFF":
                    common.pumpB_status = "ON"		
                    common.pumpB_start = row[1]
                    common.pumpB_energy_start = row[7]
                else:
                    common.pumpB_energy_latest = row[7]
                    common.pumpB_stop = row[1]		    		    				    
            else:		
                if common.pumpB_status == "ON":
                    common.pumpB_stop = row[1]
                    energy = int(common.pumpB_energy_latest) - int(common.pumpB_energy_start)
                    record['p'] = "B"                                          # pump
                    record['sd'] = common.pumpB_start                          # start_date
                    record['se'] = common.pumpB_energy_start                   # start energy 
                    record['ee'] = common.pumpB_stop                           # end date 
                    record['ee'] = common.pumpB_energy_latest                  # end energy
                    record['ue'] = str(energy)                                 # used energy
                    # Reset pump data
                    common.pumpB_status = "OFF"
                    common.pumpB_start = ""
                    common.pumpB_energy_start = ""
                    common.pumpB_stop = ""
                    common.pumpB_energy_latest = ""
                    # Send data to AWS
                    awsHandler.putSensorData(record)		    		
        else:
            logger.put_msg("I",f"Pump {row[0]} data not processed")

        return 
    except Exception as e:
        logger.put_msg("E",f"awsHandler.sumData ERROR: {e}")
    
