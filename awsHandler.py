"""
Author: Dave Weilert
Copyright(C) 2023 Freeware
Date: 3/19/2023

REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------
  2023/03/22  DaW             Initial creation 

OVERVIEW:
    Send sensor or SMS data to AWS via the API Gateway to a Lambda 
    function that writes the data to a DynamoDB data base. 

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

import requests
import time
import json
from datetime import datetime

import common
import config
import logger

def putSensorData(sdata):
    id = getPutID()
    sensorUrl = config.get("AWSGateWay","sensor_data")
    try:
        sdata['id'] = id
        sdata = sdata
        if common.debug == True:
            logger.put_msg("D",f"putHandler.putSensorData sdata: {sdata}")
        url = sensorUrl
        response = requests.put(url, json=sdata)
        if common.debug == True:
            logger.put_msg("D",f"putHandler.putSensorData response: {response}")
        res = response.json()
        if common.debug == True:
            logger.put_msg("D",f"putHandler.putSensorData res: {res}")
    except Exception as e:
        logger.put_msg("E",f"putHandler.putSensorData ERROR: {e}")
    finally:
        if common.debug == True:
            logger.put_msg("D","putHandler.putSensorData finished")


def putSMSData(mdata):
    id = getPutID()
    smsUrl = config.get("AWSGateWay","sms_data")
    #SAMPLE DATA: {"id":"03222023164840","d":"03/21/2023-23:58:04","m":"MMPOAII Sewer Alert : (1) Power has been lost for all equipment","w":"Maintenance"}
    try:
        mdata["id"] = id
        mdata = mdata
        if common.debug == True:
            logger.put_msg("D",f"putHandler.putSMSData sdata: {mdata}")
        url = smsUrl
        response = requests.put(url, json=mdata)
        if common.debug == True:
            logger.put_msg("D",f"putHandler.putSMSData response: {response}")
        res = response.json()
        if common.debug == True:
            logger.put_msg("D",f"putHandler.putSMSData res: {res}")
    except Exception as e:
        logger.put_msg("E",f"putHandler.putSMSData ERROR: {e}")
    finally:
        if common.debug == True:
            logger.put_msg("D","putHandler.putSMSData finished")


def getPutID():
    try:
        # return a unique value to be used for the ID of the put
        now = datetime.now()
        # Sleep for one second to ensure there will never be a duplicate key
        time.sleep(1.0)
        return now.strftime("%m%d%Y%H%M%S")
    except Exception as e:
        logger.put_msg("E",f"putHandler.getPutID ERROR: {e}")
