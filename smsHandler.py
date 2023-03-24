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

import os
from twilio.rest import Client
import time
from datetime import datetime
import json

import common
import config
import awsHandler
import logger

# Download the helper library from https://www.twilio.com/docs/python/install
# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure

common.sid = ""
common.token = ""
common.from_number = ""
common.test_number = ""
common.test_message = ""
common.skip_sending = ""
common.msg_header = ""

def getParms():
    try:
        common.sid = config.get("Twilio","accountSID")
        common.token = config.get("Twilio","authToken")
        common.from_number = config.get("Twilio","from_number")
        common.test_number = config.get("Twilio","test_number")
        common.test_message = config.get("Twilio","test_message")
        common.skip_sending = config.get("Twilio","skip_sending")
        common.msg_header = config.get("Twilio","msg_header")+" "
    except Exception as e:
        print(f"Get SMS parms error: {e}")    

def sendSMS(toNumbers, msgBody, who):
    try:
        getParms()
        if "," in toNumbers:
            newNum = toNumbers.split(",")
            toNumbers = newNum
        else:
            newNum = []
            newNum.append(toNumbers)
            toNumbers = newNum

        now = datetime.now()
        fmtDate = now.strftime("%m/%d/%Y at %H:%M:%S")
        msg = common.msg_header + fmtDate
        cnt = 1

        # Build the message to send
        for m in msgBody:
            msg = msg + "(" + str(cnt) + ") " + m + " "
            cnt = cnt + 1
	
        client = Client(common.sid, common.token)    
        first_msg = True
        for number in toNumbers:
            #print("Send message to: ", number)
            if common.skip_sending == "TRUE" or common.skip_sending == "True" or common.skip_sending == "true":
                logger.put_msg("I","Skipped sending SMS: " + msg )
            else:
                client.messages.create(
                    to=number, 
                    from_=common.from_number, 
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
        print("SMS error: ", e)

    finally:
        return msg

def testSMS():    
    sendSMS(common.test_number, common.test_message, "Test")
