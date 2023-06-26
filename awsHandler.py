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

import sys
import requests
import time
from datetime import datetime

import config
import logger


def putSensorData(sdata):
    id = getPutID()
    sensorUrl = config.get("AWSGateWay","sensor_data")
    try:
        sdata["id"] = id
        sdata = sdata
        if config.get("Debug","show_aws_put_info") == "true":
            logger.msg("D",f"putSensorData() sdata: {sdata}")
        url = sensorUrl
        response = requests.put(url, json=sdata)
        if config.get("Debug","show_aws_put_info") == "true":
            logger.msg("D",f"putSensorData() response: {response}")
        res = response.json()
        if config.get("Debug","show_aws_put_info") == "true":
            logger.msg("D",f"putSensorData() res: {res}")
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"putSensorData() Exception type: {exception_type} File name: {filename} Line number: {line_number}")               
        logger.msg("E",f"putSensorData() {e}")
    finally:
        if config.get("Debug","show_aws_put_info") == "true":
            logger.msg("D","putSensorData finished")


def putSMSData(mdata):
    id = getPutID()
    smsUrl = config.get("AWSGateWay","sms_data")
    try:
        mdata["id"] = id
        mdata = mdata
        if config.get("Debug","show_aws_put_info") == "true":
            logger.msg("D",f"putSMSData() sdata: {mdata}")
        url = smsUrl
        response = requests.put(url, json=mdata)
        if config.get("Debug","show_aws_put_info") == "true":
            logger.msg("D",f"putSMSData() response: {response}")
        res = response.json()
        if config.get("Debug","show_aws_put_info") == "true":
            logger.msg("D",f"putSMSData() res: {res}")
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"putSMSData() Exception type: {exception_type} File name: {filename} Line number: {line_number}")               
        logger.msg("E",f"putSMSData() {e}")
    finally:
        if config.get("Debug","show_aws_put_info") == "true":
            logger.msg("D","putSMSData() finished")


def putAMPSData(adata):
    id = getPutID()
    ampsUrl = config.get("AWSGateWay","amps_data")
    try:
        adata["id"] = id
        adata = adata
        if config.get("Debug","show_aws_put_info") == "true":
            logger.msg("D",f"putAMPSData() sdata: {adata}")
        url = ampsUrl
        response = requests.put(url, json=adata)
        if config.get("Debug","show_aws_put_info") == "true":
            logger.msg("D",f"putAMPSData() response: {response}")
        res = response.json()
        if config.get("Debug","show_aws_put_info") == "true":
            logger.msg("D",f"putAMPSData() res: {res}")
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"putAMPSData() Exception type: {exception_type} File name: {filename} Line number: {line_number}")               
        logger.msg("E",f"putAMPSData() {e}")
    finally:
        if config.get("Debug","show_aws_put_info") == "true":
            logger.msg("D","putAMPSData() finished")


def putDailyData(ddata):
    # NOT CURRENTLY INVOKED
    diagUrl = config.get("AWSGateWay","daily_data")
    try:
        ddata = ddata
        if config.get("Debug","show_aws_put_info") == "true":
            logger.msg("D",f"putDailyData() ddata: {ddata}")
        url = diagUrl
        response = requests.put(url, json=ddata)
        if config.get("Debug","show_aws_put_info") == "true":
            logger.msg("D",f"putDailyData() response: {response}")
        res = response.json()
        if config.get("Debug","show_aws_put_info") == "true":
            logger.msg("D",f"putDailyData() res: {res}")
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"putDailyData() Exception type: {exception_type} File name: {filename} Line number: {line_number}")               
        logger.msg("E",f"putDailyData() {e}")
    finally:
        if config.get("Debug","show_aws_put_info") == "true":
            logger.msg("D","putDailyData() finished")



def putDiagData(ddata):
    diagUrl = config.get("AWSGateWay","diag_data")
    try:
        ddata = ddata
        if config.get("Debug","show_aws_put_info") == "true":
            logger.msg("D",f"putDiagData() ddata: {ddata}")
        url = diagUrl
        response = requests.put(url, json=ddata)
        if config.get("Debug","show_aws_put_info") == "true":
            logger.msg("D",f"putDiagData() response: {response}")
        res = response.json()
        if config.get("Debug","show_aws_put_info") == "true":
            logger.msg("D",f"putDiagData() res: {res}")
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"putDiagData() Exception type: {exception_type} File name: {filename} Line number: {line_number}")               
        logger.msg("E",f"putDiagData() {e}")
    finally:
        if config.get("Debug","show_aws_put_info") == "true":
            logger.msg("D","putDiagData() finished")


def getPutID():
    try:
        # return a unique value to be used for the ID of the put
        now = datetime.now()
        # Sleep for one second to ensure there will never be a duplicate key
        time.sleep(1.0)
        return now.strftime("%m%d%Y%H%M%S")
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"getPutID() Exception type: {exception_type} File name: {filename} Line number: {line_number}")               
        logger.msg("E",f"getPutID() {e}")