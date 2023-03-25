"""
Author: Dave Weilert
Copyright(C) 2023 Freeware
Date: 3/19/2023

REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------
  2023/03/23  DaW             Initial creation 

OVERVIEW:
    Common module to store data used in multiple modules. 

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


# logger
log_dir = ""
log_base = ""
log_date = ""
log_file_name = ""
log_old_name = ""
log_sms = ""
log_first_time = True

# monitor
getPortsCnt = 0
portA = "na"
portB = "na"
portC = "na"
portD = "na"
wait_to_check_sensors = 15
wait_to_check_for_ports = 15

# pumpHandler
no_data_max = 10000
no_power_max = 10000
no_voltage_max = 10000


# Data array of pzem-16 sensor data
sensorData = []
saveCount = 0

# Pump A data
pumpA_status = "OFF"
pumpA_start = ""
pumpA_stop = ""
pumpA_energy_start = 0
pumpA_energy_latest = 0
pumpA_record = ""

# Pump B data
pumpB_status = "OFF"
pumpB_start = ""
pumpB_stop = ""
pumpB_energy_start = 0
pumpB_energy_latest = 0
pumpB_record = ""

def saveSensorData(data):
    sd = data.split(",")
    global sensorData
    global saveCount
    sensorData.append(sd)
    saveCount = saveCount + 1

def getSensorData():
    return sensorData

def clearSensorData():
    global sensorData
    global saveCount
    sensorData = []
    saveCount = 0

def getSensorCount():
    return saveCount
