"""
Author: Dave Weilert
Copyright(C) 2023 Freeware
Date: 3/19/2023

REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------
  2023/03/19  DaW             Initial creation 

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
import logging
from gpiozero import CPUTemperature
import socket
from threading import Thread

import config
import commonDataArea as cda
import pzemHandler
import smsHandler
import checkThresholds
import upsHandler
import logger


def getPorts():
    try:
        pzemHandler.find_usb_ports()
        cda.getPortsCnt = cda.getPortsCnt + 1
        if cda.getPortsCnt > int(config.get("Limits","no_ports")):
            smsHandler.sendSMS(config.get("Limits","no_ports_number"), config.get("Limits","no_ports_msg"), config.get("Limits","no_ports_who"))
            cda.getPortsCnt = 0
    except Exception as e:
        logger.put_msg("E","monitor.getPorts ERROR: " + e)


def mainLine():
    try:
        while True:
            getPorts()
            cnt = 0   
            if (cda.portA != "na"):
                cnt = cnt + 1
            if (cda.portB != "na"):
                cnt = cnt + 1
            if (cda.portC != "na"):
                cnt = cnt + 1
            if (cda.portD != "na"):
                cnt = cnt + 1    

            # check if any ports were located
            if cnt > 0:
                break
            else:	    
                time.sleep(int(config.get("Interval","wait_to_check_for_ports")))

        iCnt = 0
        rtn = ""
        while True:
            iCnt = iCnt + 1
            rtn = pzemHandler.monitor(cda.portA,"A")
            if config.get("Debug","show_regs") == "true":
                logger.put_msg("D",f"Port A Regs: {rtn}")
            checkThresholds.check(rtn,"A")
            
            rtn = pzemHandler.monitor(cda.portB,"B")
            if config.get("Debug","show_regs") == "true":
                logger.put_msg("D",f"Port B Regs: {rtn}")
            checkThresholds.check(rtn,"B")
            
            rtn = pzemHandler.monitor(cda.portC,"C") 
            if config.get("Debug","show_regs") == "true":
                logger.put_msg("D",f"Port C Regs: {rtn}")
            checkThresholds.check(rtn,"C")
            
            rtn = pzemHandler.monitor(cda.portD,"D")          
            if config.get("Debug","show_regs") == "true":
                logger.put_msg("D",f"Port D Regs: {rtn}")
            checkThresholds.check(rtn,"D")

            # Check for io errors and connection errors
            checkThresholds.checkSensors()

            ups = upsHandler.getUPSInfo()

            # # Check if a command request has been submitted
            # if cda.cmdI != "":
            #     cda.cmdI == ""
            #     print(f"Command to execute: {cda.cmdI}")



            # Log iteration and wait

            #print(f"Interval count: {iCnt}", end="")
            now = datetime.now()
            ts = now.strftime("%Y-%m-%d %H:%M:%S.%f")
            cpu = CPUTemperature()
            print(f"{ts} (I) : Interval count({iCnt} CPU temp: {cpu.temperature} C)")

            time.sleep(int(config.get("Interval","wait_to_check_sensors")))
            
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.put_msg("E",f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.put_msg("E",f"monitor.mainLine Exception: {e}")
        time.sleep(15)
        mainLine()

class interface:

    def __init__(self, name, isDaemon) :
        if os.path.exists("/tmp/sensor_server_socket"): 
            os.remove( "/tmp/sensor_server_socket")
        self._name = name
        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self._socket.bind("/tmp/sensor_server_socket")
        self._thread = Thread(target=self._listener)
        self._thread.setDaemon(isDaemon)
        self._thread.start()

    def _listener(self) :
        while True:
            data = self._socket.recvfrom(1024)
            print(type(data[0]))
            print(data[0])
            ndata = data[1].decode('utf-8')
            print(type(ndata))
            print(ndata)
            # ndata = string(data)
            # print(type(ndata)) 
            # for d in data:
            #     print(d)
            #     #d = d.decode('utf-8')
            #     #ndata = ndata + d
            #print(f"cmdI received: {data}")
            print(ndata)
            #cda.cmdI = data
            if ndata == "pump":
                msg = "Pump data to be returned"
                break
            elif ndata == "ups":                
                msg = "UPS data to be returned"
                break
            elif ndata == "status":
                msg = "Status data to be returned"
                break
            else:
                msg = "Invalid command"
                break

        msg = "Invalid command"
        rtn = bytes(msg, 'utf-8')
        print(type(rtn))
        print(rtn)
        self._send(rtn)


    def _send(self, data) :
        _s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        _s.sendto(data, "/tmp/sensor_server_socket")

	

# Main section 
if __name__ == "__main__":
    # reset_usb()
    try:
        logging.basicConfig()
        log = logging.getLogger()
        log.setLevel(logging.DEBUG)        
        # Read config.ini file for parameters
        config.readConfig()
        # Create UNIX socket to listen for inbound command requests
        cda.cmdI = ""
        cmdInterface = interface(name="cmdI", isDaemon=True)
        mainLine()
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.put_msg("E",f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")               
        logger.put_msg("E",f"monitor.__main__ Exception: {e}")    
        time.sleep(5)
        mainLine()
