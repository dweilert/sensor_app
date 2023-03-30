#!/usr/bin/env python3

"""
Author: Dave Weilert
Copyright(C) 2023 Freeware
Date: 3/19/2023

REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------
  2023/03/19  DaW             Initial creation 

OVERVIEW:
    Routine to send SMS message using Twilio software.

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


GENERAL INFORMATION:
    PREREQUISITES
        sudo pip3 install twilio    # Install Twilio 
"""

import sys
import time
from datetime import datetime
from twilio.rest import Client

import config
import awsHandler
import logger
import commonDataArea as cda

# Download the helper library from https://www.twilio.com/docs/python/install
# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure

def checkSMS():
    try:
        if len(cda.smsMsg) > 0:
            for s in cda.smsMsg:
                numbers = ""
                if s[1] == "developer":
                    numbers = config.get("SMSNumbers","developer")
                if s[1] == "maintenance":
                    numbers = config.get("SMSNumbers","maintenance")
                if s[1] == "owners":
                    numbers = config.get("SMSNumbers","owners")
                sendSMS(numbers, s[0], s[1])
            cda.smsMsg = []
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.put_msg("E",f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")               
        logger.put_msg("E",f"smsHandler.checkSMS ERROR: {e}")

def sendSMS(toNumbers, msgBody, who):
    try:
        if "," in toNumbers:
            newNum = toNumbers.split(",")
            toNumbers = newNum
        else:
            newNum = []
            newNum.append(toNumbers)
            toNumbers = newNum

        now = datetime.now()
        fmtDate = now.strftime("%m/%d/%Y at %H:%M:%S")
        msg = config.get("Twilio","msg_header") + " " + fmtDate + " - "
        cnt = 1

        # Build the message to send
        for m in msgBody:
            msg = msg + "(" + str(cnt) + ") " + m + " "
            cnt = cnt + 1
	
        client = Client(config.get("Twilio","accountSID"), config.get("Twilio","authToken"))    
        first_msg = True
        for number in toNumbers:
            #print("Send message to: ", number)
            if config.get("Twilio","skip_sending") == "true":
                logger.put_msg("I","Skipped sending SMS: " + msg )
            else:
                client.messages.create(
                    to=number, 
                    from_=config.get("Twilio","from_number"), 
                    body=msg)
                if first_msg == True:
                    first_msg = False				    	    
                    logger.put_msg("I","Sent SMS: " + msg + " to " + who )		
                    j_data = {}
                    j_data["d"] = fmtDate
                    j_data["m"] = msg
                    j_data["w"] = who
                    awsHandler.putSMSData(j_data)
                time.sleep(1)

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.put_msg("E",f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")               
        logger.put_msg("E",f"smsHandler.sendSMS ERROR: {e}")

    finally:
        return msg
