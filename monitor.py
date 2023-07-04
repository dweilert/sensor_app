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
  2023/06/26  DaW             Removed three def's checkDiag, diagInfo, and 
                              getRAMinfo and moved them to a new util.py file.

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
import time
import sys
from datetime import datetime
from gpiozero import CPUTemperature
import requests

import config
import logger
import util
import commonDataArea as cda
import pzemHandler
import smsHandler
import awsHandler
import checkThresholds
import getCmdInfo
import upsHandler
import endOfDay


def getPorts():
    try:
        pzemHandler.find_usb_ports()
        cda.getPortsCnt = cda.getPortsCnt + 1

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg(
            "E", f"getPorts() Exception type: {exception_type} File name: {filename} Line number: {line_number}")
        logger.msg("E", f"getPorts() {e}")


def resetCheck(nowDay, nowHour):
    try:
        # Check if it is a new day, if so reset memory
        if cda.current_date != nowDay:
            cda.current_date = nowDay
            cda.iCnt = 0
            cda.error_cnt = 0
            cda.pumpB_cycle_cnt = 0
            cda.pumpA_cycle_cnt = 0
            cda.sensor_A_registers = []
            cda.sensor_B_registers = []
            cda.sensor_C_registers = []
            cda.sensor_D_registers = []
            cda.cpu_temps = []
            cda.cpu_ram = []
            cda.upsData = []
            cda.high_temp_cnt = 0
            cda.ups_charge_cnt = 0
            cda.ups_percent_cnt = 0

            cda.critical_error = 0
            cda.critical_error_A = 0
            cda.critical_error_B = 0
            cda.critical_error_C = 0
            cda.critical_error_D = 0
            cda.timeout_error = 0

            cda.oserr_A = 0
            cda.oserr_B = 0

            # End of day message and stats
            endOfDay.sendDailyInfo()
            cda.daily_pump_A_cnt = 0
            cda.daily_pump_A_amp_high = 0
            cda.daily_pump_A_amp_low = 9999

            cda.daily_pump_B_cnt = 0
            cda.daily_pump_B_amp_high = 0
            cda.daily_pump_B_amp_low = 9999
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg(
            "E", f"resetCheck() Exception type: {exception_type} File name: {filename} Line number: {line_number}")
        logger.msg("E", f"resetCheck() {e}")


def mainLine():
    """
    Get the USB ports that are connected to the PZEM sensors.  At startup of the
    Raspberry Pi there are messages that are accessable via the linux command
    dmesg.  The pzemHandler will try and find these messages.  If the dmesg 
    output is not located the system will retry 5 times then default to default
    values. 

    Once tttyUSB* ports are set the system will begin polling the sensors on 
    each USB port.
    """

    diagCnt = 0
    find_cnt = 0
    rtn = ""
    critical_count = int(config.get("Limits","critical_error_skip_count"))
    portsFound = 0

    mapA = ""
    mapB = ""
    mapC = ""
    mapD = ""

    try:
        portsFound = 0
        waitSeconds = config.get("Interval", "wait_to_check_for_ports_seconds")
        while True:
            portsfound = 0
            find_cnt = find_cnt + 1

            # Get PZEM port data
            getPorts()

            # Check for if any ports were found is so break out of while
            if (cda.usb_port1 != "na"):
                portsfound = portsfound + 1
            if (cda.usb_port2 != "na"):
                portsfound = portsfound + 1
            if (cda.usb_port3 != "na"):
                portsfound = portsfound + 1
            if (cda.usb_port4 != "na"):
                portsfound = portsfound + 1

            # If at least one port is found check if any ports were located
            if portsfound > 0:
                break

            logger.msg(
                "I", f"Get sensor attempt {find_cnt} of 5 completed, next attempt in {waitSeconds} seconds")

          # Circut breaker to stop looking for USB definitions
            if find_cnt > 5:
                cda.usb_port1 = "/dev/ttyUSB0"
                cda.usb_port2 = "/dev/ttyUSB1"
                cda.usb_port3 = "/dev/ttyUSB2"
                cda.usb_port4 = "/dev/ttyUSB3"
                logger.msg(
                    "I", f"Attempted to read USB ports 5 times, forced use of default USB ports")
                break

            time.sleep(int(waitSeconds))

        # ----------------------------------------------------------------------

        map1 = config.get("USBPortSignatures", "map_usb_port1_to_sensor")
        map2 = config.get("USBPortSignatures", "map_usb_port2_to_sensor")
        map3 = config.get("USBPortSignatures", "map_usb_port3_to_sensor")
        map4 = config.get("USBPortSignatures", "map_usb_port4_to_sensor")


        # Log the sensors located and send SMS about what is found
        logger.msg("I", "------------")
        logger.msg("I", f"USB port 1: {cda.usb_port1} mapped to Sensor: {map1}")
        logger.msg("I", f"USB port 2: {cda.usb_port2} mapped to Sensor: {map2}")
        logger.msg("I", f"USB port 3: {cda.usb_port3} mapped to Sensor: {map3}")
        logger.msg("I", f"USB port 4: {cda.usb_port4} mapped to Sensor: {map4}")
        logger.msg("I", "------------")
        logger.msg("I","Logic checking is:")
        logger.msg("I","  (A) - pump 1")
        logger.msg("I","  (B) - pump 2")
        logger.msg("I","  (C) - high-level alarm")
        logger.msg("I","  (D) - overall power")

        pCnt = 0
        # Check for if any ports were found is so break out of while
        if cda.usb_port1 != "na":
            pCnt = pCnt + 1
        if cda.usb_port2 != "na":
            pCnt = pCnt + 1
        if cda.usb_port3 != "na":
            pCnt = pCnt + 1
        if cda.usb_port4 != "na":
            pCnt = pCnt + 1

        # SMS related message, who
        foundMsg = ""
        who = ""
        if pCnt > 0:
            foundMsg = config.get("Messages", "sensors_at_startup_msg") +  " " + str(portsfound)
            who = config.get("Messages", "sensors_at_startup_who")
        else:
            foundMsg = config.get("Messages", "sensors_default_msg")
            who = config.get("Messages", "sensors_default_who")

        # Send SMS
        sms = []
        sms.append(foundMsg)
        sms.append(who)
        cda.smsMsg.append(sms)
        smsHandler.sendSMS()


        # Now loop forever
        while True:
            now = datetime.now()
            nowDay = now.strftime("%Y_%m_%d")
            nowHour = now.strftime("%H")
            # Reset stats and counters if it is a new day
            resetCheck(nowDay, nowHour)
            # Increment daily interval counter
            cda.iCnt = cda.iCnt + 1

            """ 
            Get data for each USB port sensor.  If the critical error count
            is more than the defined critical count then skip checking the 
            associated sensor for the remainder of the day.

            Checking crtitical count avoids checking a sensor continuiously once
            it has not worked for an extended time frame.
            """
            if cda.usb_port1 != "na":
                if cda.critical_error_A < critical_count: 
                    if map1 != "skip":
                        rtn = []
                        rtn = pzemHandler.readSensor(cda.usb_port1, map1)
                        # print(f"A rtn {rtn}")
                        #print(f"usb_port1 regisiters: {rtn}")
                        if rtn[0] == False:
                            rtn[1] = []
                        checkThresholds.checkData(rtn[1], map1)
                        cda.sensor_A_registers.append(rtn[1])

            if cda.usb_port2 != "na":
                if cda.critical_error_B < critical_count:
                    if map2 != "skip":
                        rtn = []
                        rtn = pzemHandler.readSensor(cda.usb_port2, map2)
                        #print(f"usb_port2 regisiters: {rtn}")
                        if rtn[0] == False:
                            rtn[1] = []
                        checkThresholds.checkData(rtn[1], map2)
                        cda.sensor_B_registers.append(rtn[1])

            if cda.usb_port3 != "na":
                if cda.critical_error_C < critical_count:
                    if map3 != "skip":
                        rtn = []
                        rtn = pzemHandler.readSensor(cda.usb_port3, map3)
                        # print(f"C registers: {rtn}")
                        #print(f"usb_port3 regisiters: {rtn}")
                        if rtn[0] == False:
                            rtn[1] = []
                        checkThresholds.checkData(rtn[1], map3)
                        cda.sensor_C_registers.append(rtn[1])

            if cda.usb_port4 != "na":
                if cda.critical_error_D < critical_count:
                    if map4 != "skip":
                        rtn = []
                        rtn = pzemHandler.readSensor(cda.usb_port4, map4)
                        #print(f"usb_port4 regisiters: {rtn}")
                        if rtn[0] == False:
                            rtn[1] = []
                        checkThresholds.checkData(rtn[1], map4)
                        cda.sensor_D_registers.append(rtn[1])

            # get Raspberry Pi temp and save if it is a new hour
            cpu = CPUTemperature()

            if nowHour != cda.cpu_temp_hour:
                cda.cpu_temps.append(nowHour + ":" + str(cpu.temperature))
                cda.cpu_temp_hour = nowHour
                cda.cpu_temp_high = cpu.temperature

                # Also check when the last pump ran
                cda.pump_last_run = cda.pump_last_run + 1
                if cda.pump_last_run > int(config.get("Limits", "no_pumps_run")):
                    # Send SMS warnng message
                    sms = []
                    msg = config.get("Messages", "no_pumps_run_msg") 
                    msg = msg + " " + str(cda.pump_last_run) + " hours"
                    sms.append(msg)
                    sms.append(config.get("Messages", "no_pumps_run_who"))
                    cda.smsMsg.append(sms)
                    smsHandler.sendSMS()

            # check temperature for out of threshoold ranges
            checkThresholds.checkTemperature(cpu.temperature)

            # get Raspberry Pi UPS info and check the charge level
            upsI = upsHandler.getUPSInfo(False)
            checkThresholds.checkUPSPercent(upsI[1])

            # get Raspberry Pi memory usage data
            cda.cpu_ram.append(util.getRAMinfo())

            # Return RAM information (unit=kb) in a list
            if config.get("Debug", "interval_count") == "true":
                logger.msg("I", f"Interval count({cda.iCnt})")

            # check if the CLI interface has any requests
            getCmdInfo.checkForCommandFile()

            # wait for the defined time and then do it all again
            time.sleep(int(config.get("Interval", "wait_to_check_sensors_seconds")))

            # if diagCnt == 5:
            #     util.checkDiag()
            #     diagCnt = 0
            # else:
            #     diagCnt = diagCnt + 1

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E", f"mainLine() Exception type: {exception_type} File name: {filename} Line number: {line_number}")
        logger.msg("E", f"mainLine() {e}")
        time.sleep(5)
        mainLine()


""" 
===============================================================================
Main section 

This application may have been started as a system service.  If defined as a 
service it will be in the directory:

/lib/systemd/system/

Default service name is monitor.service with the following.  Ensure the User 
parameter is defined of the sensor_app files will not be located.

-------- File contents --------
[Unit]
Description=MMPOAII Monitor

[Service]
User=bob
WorkingDirectory=/home/bob
ExecStart=/usr/bin/python /home/bob/sensor_app/monitor.py
Restart=on-abort
#Environment=PYTHONPATH=/home/bob/sensor_app

[Install]
WantedBy=multi-user.target

-------- End of file --------

Work with the service by using these commands:

  -- What --         ---- command ----
Check status    : systemctl status monitor
Start service   : systemctl start monitor
Stop service    : systemctl stop monitor
Restart service : systemctl restart monitor

===============================================================================
"""
if __name__ == "__main__":
    # reset_usb()
    try:
        # get current date
        now = datetime.now()
        print("------------")
        print("Monitor started at: " + now.strftime("%Y/%m/%d, %H:%M:%S"))

        cda.current_date = now.strftime("%Y_%m_%d")

        # Read config.ini file for parameters
        config_status = config.readConfig()
        if config_status == False:
            print("FATAL ERROR starting unable to read config file")
            sys.exit()

        # initialize values
        # cda.cmdI = ""
        # cda.iCnt = 0
        # cda.error_cnt = 0

        # Check if old CLI command.txt file exists and delete if found
        if os.path.exists(config.get("CommandInterface", "cmd_file")):
            os.remove(config.get("CommandInterface", "cmd_file"))

        # Start
        mainLine()

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E", f"__main__ Exception type: {exception_type} File name: {filename} Line number: {line_number}")
        logger.msg("E", f"__main__ {e}")
        time.sleep(5)

        # Invoke mainLine even if an error occurs
        mainLine()
