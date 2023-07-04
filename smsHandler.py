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


def checkSMS(what):
    try:
        # print(f"checkSMS parameter: {what} from sensor: {cda.from_sensor}")
        send = True

        if what == "all_sensors_io_error":
            if cda.resend_all_sensors_io_error_cnt == 0:
                send = True
                cda.resend_all_sensors_io_error_cnt = 1
            else:
                cda.resend_all_sensors_io_error_cnt += 1
                if cda.resend_all_sensors_io_error_cnt < cda.resend_wait:
                    send = False
                else:
                    cda.resend_all_sensors_io_error_cnt = 0

        elif what == "amps":
            send = True

        elif what == "connect_error":
            if cda.resend_sensor_connect_error_cnt == 0:
                send = True
                cda.resend_sensor_connect_error_cnt = 1
            else:
                cda.resend_sensor_connect_error_cnt += 1
                if cda.resend_sensor_connect_error_cnt < cda.resend_wait:
                    send = False
                else:
                    cda.resend_sensor_connect_error_cnt = 0

        elif what == "high_level_alarm":
            if cda.resend_high_level_alarm_cnt == 0:
                send = True
                cda.resend_high_level_alarm_cnt = 1
            else:
                cda.resend_high_level_alarm_cnt += 1
                if cda.resend_high_level_alarm_cnt < cda.resend_wait:
                    send = False
                else:
                    cda.resend_high_level_alarm_cnt = 0

        elif what == "io_error":
            if cda.resend_sensor_io_error_cnt == 0:
                send = True
                cda.resend_sensor_io_error_cnt = 1
            else:
                cda.resend_sensor_io_error_cnt += 1
                if cda.resend_sensor_io_error_cnt < cda.resend_wait:
                    send = False
                else:
                    cda.resend_sensor_io_error_cnt = 0

        elif what == "no_data":
            if cda.resend_sensor_no_data_cnt == 0:
                send = True
                cda.resend_sensor_no_data_cnt = 1
            else:
                cda.resend_sensor_no_data_cnt += 1
                if cda.resend_sensor_no_data_cnt < cda.resend_wait:
                    send = False
                else:
                    cda.resend_sensor_no_data_cnt = 0

        elif what == "no_power_a":
            if cda.resend_sensor_no_power_a_cnt == 0:
                send = True
                cda.resend_sensor_no_power_a_cnt = 1
            else:
                cda.resend_sensor_no_power_a_cnt += 1
                if cda.resend_sensor_no_power_a_cnt < cda.resend_wait:
                    send = False
                else:
                    cda.resend_sensor_no_power_a_cnt = 0

        elif what == "no_power_b":
            if cda.resend_sensor_no_power_b_cnt == 0:
                send = True
                cda.resend_sensor_no_power_b_cnt = 1
            else:
                cda.resend_sensor_no_power_b_cnt += 1
                if cda.resend_sensor_no_power_b_cnt < cda.resend_wait:
                    send = False
                else:
                    cda.resend_sensor_no_power_b_cnt = 0

        elif what == "no_overall_power":
            if cda.resend_no_overall_power_cnt == 0:
                send = True
                cda.resend_no_overall_power_cnt = 1
            else:
                cda.resend_no_overall_power_cnt += 1
                if cda.resend_no_overall_power_cnt < cda.resend_wait:
                    send = False
                else:
                    cda.resend_no_overall_power_cnt = 0

        elif what == "temp":
            if cda.resend_rasp_temp_cnt == 0:
                send = True
                cda.resend_rasp_temp_cnt = 1
            else:
                cda.resend_rasp_temp_cnt += 1
                if cda.resend_rasp_temp_cnt < cda.resend_wait:
                    send = False
                else:
                    cda.resend_rasp_temp_cnt = 0

        elif what == "ups_percent":
            if cda.resend_rasp_ups_percent_cnt == 0:
                send = True
                cda.resend_rasp_ups_percent_cnt = 1
            else:
                cda.resend_rasp_ups_percent_cnt += 1
                if cda.resend_rasp_ups_percent_cnt < cda.resend_wait:
                    send = False
                else:
                    cda.resend_rasp_ups_percent_cnt = 0

        else:
            if what != "other":
                send = False
                logger.msg(
                    "W", f"smsHandler.checkSMS did not receive valid type, RECEIVED: {what}")

        if send == True:
            sendSMS()

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg(
            "E", f"checkSMS() Exception type: {exception_type} File name: {filename} Line number: {line_number}")
        logger.msg("E", f"checkSMS() {e}")


def sendSMS():
    try:
        who = cda.smsMsg[0][1]
        toNumbers = config.get("SMSNumbers", who)

        if "," in toNumbers:
            newNum = toNumbers.split(",")
            toNumbers = newNum
        else:
            newNum = []
            newNum.append(toNumbers)
            toNumbers = newNum

        now = datetime.now()
        fmtDate = now.strftime("%m/%d/%Y at %H:%M:%S")
        # msg = config.get("Twilio", "msg_header") + " " + fmtDate + " - "
        msg = config.get("Twilio", "msg_header") + " - "
        msg = msg + " " + cda.smsMsg[0][0]

        client = Client(config.get("Twilio", "accountSID"),
                        config.get("Twilio", "authToken"))
        first_msg = True
        for number in toNumbers:
            # print("Send message to: ", number)
            if config.get("Twilio", "skip_sending") == "true":
                logger.msg("I", "Skipped sending SMS: " + msg)
            else:
                client.messages.create(
                    to=number,
                    from_=config.get("Twilio", "from_number"),
                    body=msg)
                if first_msg == True:
                    first_msg = False
                    logger.msg("I", "Sent SMS: " + msg + " to " + who)
                    j_data = {}
                    j_data["d"] = fmtDate
                    j_data["m"] = cda.smsMsg[0][0]            
                    # j_data["m"] = msg
                    j_data["w"] = who
                    awsHandler.putSMSData(j_data)
                time.sleep(1)

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg(
            "E", f"sendSMS() Exception type: {exception_type} File name: {filename} Line number: {line_number}")
        logger.msg("E", f"sendSMS() {e}")
