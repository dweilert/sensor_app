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
import sys
import requests

import config
import logger
import commonDataArea as cda
import awsHandler
import getCmdInfo


def checkDiag():
    try:
        diag = requests.get(config.get("AWSGateWay","requests_data"))
        #print("Content: ", diag.content)
        #print("Text: ", diag.text, " type: ", type(diag.text))

        if ("payload" in diag.text):
            result =  diagInfo()
            #print("Result length: ", len(result))
            record = {}
            record['id'] = "1000"
            record['p'] = result
            awsHandler.putDiagData(record)
            url = config.get("AWSGateWay","requests_data")
            url = url + "/1000"
            delete_request = requests.delete(url)
            print(delete_request.text)

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"checkDiag() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"checkDiag() {e}")


def diagInfo():
    try:
        result = getCmdInfo.getAllData()
        return result

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"getDiagInfo() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"getDiagInfo() {e}")


def getRAMinfo():
    try:
        # Index 0: total RAM                                                                
        # Index 1: used RAM                                                                 
        # Index 2: free RAM 
        p = os.popen('free')
        i = 0
        while 1:
            i = i + 1
            line = p.readline()
            if i==2:
                return(line.split()[1:4])
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"getRAMinfo() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"getRAMinfo() {e}")
 