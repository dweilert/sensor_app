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

import sys
from datetime import datetime

import commonDataArea as cda
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
            # Check if Current in row[3] is seen 	
            if int(row[3]) > 0:
                if cda.pumpA_status == "OFF":
                    cda.pumpA_status = "ON"		
                    cda.pumpA_start = row[1]
                    cda.pumpA_stop = ""
                    cda.pumpA_energy_start = row[7]
                    cda.pumpA_energy_latest = 0
                    cda.pumpA_cycles = []
                    cda.pumpA_cycles.append(row)
                    cda.pumpA_cycle_cnt = cda.pumpA_cycle_cnt + 1  
                else:
                    cda.pumpA_energy_latest = row[7]
                    cda.pumpA_stop = row[1]	
                    cda.pumpA_cycles.append(row)	 
                     		    				    
            else:		
                if cda.pumpA_status == "ON":
                    cda.pumpA_cycles.append(row)
                    cda.pumpA_stop = row[1]
                    setHLA("A")
                    energy = int(cda.pumpA_energy_latest) - int(cda.pumpA_energy_start)
                    record['p'] = "A"                                          # pump
                    record['sd'] = cda.pumpA_start                             # start_date
                    record['se'] = cda.pumpA_energy_start                      # start energy 
                    record['ed'] = cda.pumpA_stop                              # end date 
                    record['ee'] = cda.pumpA_energy_latest                     # end energy
                    record['ue'] = str(energy)                                 # used energy
                    record['ah'] = cda.pumpA_amp_high
                    record['al'] = cda.pumpA_amp_low
                    record['aa'] = cda.pumpA_amp_avg

                    # Reset pump data
                    cda.pumpA_status = "OFF"

                    # Send data to AWS
                    awsHandler.putSensorData(record)		    		
        
        
        elif row[0] == "B":
            # Check if Current is seen 	
            if int(row[3]) > 0:
                if cda.pumpB_status == "OFF":
                    cda.pumpB_status = "ON"		
                    cda.pumpB_start = row[1]
                    cda.pumpB_stop = ""
                    cda.pumpB_energy_start = row[7]
                    cda.pumpB_energy_latest = 0
                    cda.pumpB_cycles = []
                    cda.pumpB_cycles.append(row)
                    cda.pumpB_cycle_cnt = cda.pumpB_cycle_cnt + 1 
                else:
                    cda.pumpB_energy_latest = row[7]
                    cda.pumpB_stop = row[1]
                    cda.pumpB_cycles.append(row)		    		    				    
            else:		
                if cda.pumpB_status == "ON":
                    cda.pumpB_cycles.append(row)
                    cda.pumpB_stop = row[1]
                    setHLA("B")
                    energy = int(cda.pumpB_energy_latest) - int(cda.pumpB_energy_start)
                    record['p'] = "B"                                          # pump
                    record['sd'] = cda.pumpB_start                          # start_date
                    record['se'] = cda.pumpB_energy_start                   # start energy 
                    record['ed'] = cda.pumpB_stop                           # end date 
                    record['ee'] = cda.pumpB_energy_latest                  # end energy
                    record['ue'] = str(energy)                              # used energy
                    record['ah'] = cda.pumpB_amp_high
                    record['al'] = cda.pumpB_amp_low
                    record['aa'] = cda.pumpB_amp_avg

                    # Reset pump data
                    cda.pumpB_status = "OFF"

                    # Send data to AWS
                    awsHandler.putSensorData(record)		    		

        return 
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.put_msg("E",f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.put_msg("E",f"dataHandler.sumData ERROR: {e}")
    
def setHLA(id):
    try:
        high = 0
        low = 9999999
        total = 0
        avg = 0
        cnt = 0
        if id == "A":
            data = cda.pumpA_cycles
        else:
            data = cda.pumpB_cycles
        for d in data:
            if int(d[3]) > high:
                high = int(d[3])
            if int(d[3]) < low and int(d[3]) > 0:
                low = int(d[3])
            if int(d[3]) > 0: 
                total = total + int(d[3]) 
                cnt = cnt + 1

        if cnt > 0:
            avg = total / cnt
        else:
            avg = 0

        if id == "A":
            cda.pumpA_amp_high = high
            cda.pumpA_amp_low = low
            cda.pumpA_amp_avg = avg
        else:
            cda.pumpB_amp_high = high
            cda.pumpB_amp_low = low
            cda.pumpB_amp_avg = avg

        logger.put_msg("I", id + " - High:" + str(high) + " Low:" + str(low) + " Avg:" + str(avg))

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.put_msg("E",f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.put_msg("E",f"dataHandler.setHLA ERROR: {e}")
