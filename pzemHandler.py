"""
Author: Dave Weilert
Copyright(C) 2023 Freeware
Date: 3/19/2023

REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------
  2023/03/19  DaW             Initial creation 

OVERVIEW:
    Read PZEM-16 AC sensor. The AC modules measure voltage, current, power, 
    energy, frequency, and power factor. 

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
        sudo pip3 install pymodbus    # Install ModBus 

HARDWARE VERIFICATION of PZEM-16:
        From terminal using command line
        ls /dev/ttyUSB*    # Show USB devices
        lsusb -v           # Show USB devices with details

PZEM-16 MODULES

AC MODULES (80-260V):
Commmunication interface: RS-485
Communication protocol: Baud: 9600, Parity: N, Data bits: 8, Stop bit: 1

By reading the input registers the followin data is obtained:

Voltage:       Measuring range: 80-260V, Resolution: 0.1V, Measurment accuracy: 0.5%
Current:       Measuring range: 0-100A 
               Starting measuring current: 0.02A
               Resolution: 0.001A, Measurment accuracy: 0.5%
Active power:  Measuring range: 0-23kW 
               Starting measuring power: 0.4W, Resolution: 0.1W
               Format: <1000W one decimal, >=1000W only integer, Measurment accuracy: 0.5%
Power factor:  Measuring range: 0.00-1.00, Resolution: 0.01, Measurment accuracy: 1%
Frequency:     Measuring range: 45-65 Hz, Resolution: 0.1 Hz, Measurment accuracy: 0.5%
Active Energy: Measuring range: 0-999.99 kWh, Resolution: 1 Wh, Measurment accuracy: 0.5%
               Format: <10kWh integer Wh, >=10kWh then kWh

"""

import os
import time
import subprocess
import sys
from datetime import datetime
# --------------------------------------------------------------------------- #
# import the pymodbus client implementations
# --------------------------------------------------------------------------- #
from pymodbus.client import ModbusSerialClient
from pymodbus.constants import Defaults

import config
import common
import dataHandler
import logger


def monitor(usbPort, id):
    #Get register data
    try:
        rtn = ["nodata"]
        if common.portA == "na" and id == "A": 
            return rtn
        if common.portB == "na" and id == "B": 
            return rtn
        if common.portC == "na" and id == "C":
            return rtn
        if common.portD == "na" and id == "D":
            return rtn        
        client = ModbusSerialClient(port=usbPort,timeout=4,baudrate=9600,bytesize=8,parity="N",stopbits=1)
        client.connect()
        request = client.read_input_registers(0,10,1)
        # Save the sensor data is in the registers element
        dataHandler.saveData(request.registers, id)
        #print(request.registers)
        rtn = request.registers
        if config.get("Debug","show_regs") == "true":
            print(f"ID: {id} Regs {request.registers}")
        client.close()
        return rtn
    except Exception as e:
        logger.put_msg("E",f"pzemHandler.monitor Exception: {e}")

"""
Determine which ttyUSB* ports are supporting the connected PZEM modules.
This accomplished by parsing the results of issuing a 'dmesg' command.
From the last line of the command output begin searching for which 
USB port signature is mapped to what ttyUSB.  

The USB port signature is hardcoded and represents the utilized USB hub
and the connected PZEM modules.

Signatures:
   PZEM A  - usb 1-1.2.1: ch341-uart converter now attached to
   PZEM B  - usb 1-1.2.2: ch341-uart converter now attached to
   PZEM C  - usb 1-1.2.3: ch341-uart converter now attached to
   PZEM D  - usb 1-1.2.4: ch341-uart converter now attached to
   
"""
def find_usb_ports():
    try:
        # run command on OS to get info for devices
        usblist = subprocess.run(["dmesg"], capture_output=True, text=True)
        lines = usblist.stdout
        newlines = lines.split("\n")
        lines = newlines
        newlines = ""
        hl = len(lines)
        ln = 1

        common.portA = "na"
        common.portB = "na"
        common.portC = "na"
        common.portD = "na"  
        
        portA_sig = config.get("USBPortSignatures","portA")
        portB_sig = config.get("USBPortSignatures","portB")
        portC_sig = config.get("USBPortSignatures","portC")
        portD_sig = config.get("USBPortSignatures","portD")
        disconn = config.get("USBPortSignatures","disconn")
            
        while True:
            line = lines[ln]
            if config.get("Debug","show_dmesg") == "true":
                print(line)
            if disconn in line:
                chkUSB = '/dev/ttyUSB' + line[-1]
                print(f"Look for : {chkUSB}")

                if common.portA == chkUSB:
                    logger.put_msg("I",f"Sensor 1 disconned from USB port: {chkUSB}")
                    common.portA = "na"
                elif common.portB == chkUSB:
                    logger.put_msg("I",f"Sensor 2 disconned from USB port: {chkUSB}")
                    common.portB = "na"
                elif common.portC == chkUSB:
                    logger.put_msg("I",f"Sensor 3 disconned from USB port: {chkUSB}")
                    common.portC = "na"
                elif common.portD == chkUSB:
                    logger.put_msg("I",f"Sensor 4 disconned from USB port: {chkUSB}")
                    common.portD = "na"

            if portA_sig in line:
                if common.portA == "na":
                    if len(line) > 65:
                        pid = line[65:72]
                        common.portA = "/dev/" + pid
                        logger.put_msg("I",f"Sensor 1 set to USB port: {common.portA}")
        
            if portB_sig in line:
                if common.portB == "na":
                    if len(line) > 65:
                        pid = line[65:72]
                        common.portB = "/dev/" + pid
                        logger.put_msg("I",f"Sensor 2 set to USB port: {common.portB}")

            if portC_sig in line:
                if len(line) > 65:
                    pid = line[65:72]
                    common.portC = "/dev/" + pid
                    logger.put_msg("I",f"Sensor 3 set to USB port: {common.portC}")

            if portD_sig in line:
                if len(line) > 65:
                    pid = line[65:72]
                    common.portD = "/dev/" + pid
                    logger.put_msg("I",f"Sensor 4 set to USB port: {common.portD}")
            
            # Decrease line to get
            ln = ln + 1

            # No more lines to process
            if ln >= hl:
                logger.put_msg("I","------------")
                logger.put_msg("E",f"Sensor 1 usb port: {common.portA}")
                logger.put_msg("E",f"Sensor 2 usb port: {common.portB}")
                logger.put_msg("E",f"Sensor 3 usb port: {common.portC}")
                logger.put_msg("E",f"Sensor 4 usb port: {common.portD}")
                logger.put_msg("I","------------")
                break
                        
        return
    except Exception as e:
        logger.put_msg("E",f"pzemHandler.find_usb_ports Exception: {e}")