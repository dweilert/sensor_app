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

import subprocess
import sys
from datetime import datetime
from pymodbus.client import ModbusSerialClient
from pymodbus.constants import Defaults

import config
import commonDataArea as cda
import dataHandler
import logger


def monitor(usbPort, id):
    print(f"monitor: {usbPort} {id}")
    #Get register data
    try:
        rtn = ["nodata"]
        # Check if sensor was found, if not skip
        if cda.portA == "na" and id == "A": 
            return rtn
        if cda.portB == "na" and id == "B": 
            return rtn
        if cda.portC == "na" and id == "C":
            return rtn
        if cda.portD == "na" and id == "D":
            return rtn   
             
        client = ModbusSerialClient(port=usbPort,timeout=int(config.get("Pzem","timeout")),baudrate=9600,bytesize=8,parity="N",stopbits=1)

        client.connect()

        request = client.read_input_registers(0,10,1)
        # Save the sensor data is in the registers element
        dataHandler.saveData(request.registers, id)
        #print(request.registers)
        rtn = request.registers
        if config.get("Debug","show_regs") == "true":
            logger.put_msg("D",f"ID: {id} Regs {request.registers}")
        client.close()
        # No errors
        if id == "A":
            cda.sensor_A_io_error = False
            cda.sensor_A_connect_error = False
        elif id == "B":
            cda.sensor_B_io_error = False
            cda.sensor_B_connect_error = False
        elif id == "C":
            cda.sensor_C_io_error = False
            cda.sensor_C_connect_error = False
        elif id == "D":
            cda.sensor_D_io_error = False
            cda.sensor_D_connect_error = False

        return rtn
    except Exception as e:
        errorLine = f"Exception: {e}"

        if config.get("Pzem","ioException") in errorLine:
            if id == "A":
                cda.sensor_A_io_error = True
            elif id == "B":
                cda.sensor_B_io_error = True
            elif id == "C":
                cda.sensor_C_io_error = True
            elif id == "D":
                cda.sensor_D_io_error = True

        if config.get("Pzem","connectionError") in errorLine:
            if id == "A":
                cda.sensor_A_connect_error = True
            elif id == "B":
                cda.sensor_B_connect_error = True
            elif id == "C":
                cda.sensor_C_connect_error = True
            elif id == "D":
                cda.sensor_D_connect_error = True

        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.put_msg("E",f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")               
        logger.put_msg("E",f"pzemHandler.monitor Sensor {id} Exception: {e}")
        client.close()
        return ["nodata"]

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

        cda.portA = "na"
        cda.portB = "na"
        cda.portC = "na"
        cda.portD = "na"  
        
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

                if cda.portA == chkUSB:
                    if config.get("Debug","show_dmesg") == "true":
                        logger.put_msg("I",f"Sensor 1 disconned from USB port: {chkUSB}")
                    cda.portA = "na"
                elif cda.portB == chkUSB:
                    if config.get("Debug","show_dmesg") == "true":
                        logger.put_msg("I",f"Sensor 2 disconned from USB port: {chkUSB}")
                    cda.portB = "na"
                elif cda.portC == chkUSB:
                    if config.get("Debug","show_dmesg") == "true":    
                        logger.put_msg("I",f"Sensor 3 disconned from USB port: {chkUSB}")
                    cda.portC = "na"
                elif cda.portD == chkUSB:
                    if config.get("Debug","show_dmesg") == "true":
                        logger.put_msg("I",f"Sensor 4 disconned from USB port: {chkUSB}")
                    cda.portD = "na"

            if portA_sig in line:
                if cda.portA == "na":
                    if len(line) > 65:
                        pid = line[65:72]
                        cda.portA = "/dev/" + pid
                        if config.get("Debug","show_dmesg") == "true":
                            logger.put_msg("I",f"Sensor 1 set to USB port: {cda.portA}")
        
            if portB_sig in line:
                if cda.portB == "na":
                    if len(line) > 65:
                        pid = line[65:72]
                        cda.portB = "/dev/" + pid
                        if config.get("Debug","show_dmesg") == "true":
                            logger.put_msg("I",f"Sensor 2 set to USB port: {cda.portB}")

            if portC_sig in line:
                if cda.portC == "na":
                    if len(line) > 65:
                        pid = line[65:72]
                        cda.portC = "/dev/" + pid
                        if config.get("Debug","show_dmesg") == "true":
                            logger.put_msg("I",f"Sensor 3 set to USB port: {cda.portC}")

            if portD_sig in line:
                if cda.portD == "na":
                    if len(line) > 65:
                        pid = line[65:72]
                        cda.portD = "/dev/" + pid
                        if config.get("Debug","show_dmesg") == "true":
                            logger.put_msg("I",f"Sensor 4 set to USB port: {cda.portD}")
            
            # Decrease line to get
            ln = ln + 1

            # No more lines to process
            if ln >= hl:
                logger.put_msg("I","------------")
                logger.put_msg("I",f"Sensor 1 usb port: {cda.portA}")
                logger.put_msg("I",f"Sensor 2 usb port: {cda.portB}")
                logger.put_msg("I",f"Sensor 3 usb port: {cda.portC}")
                logger.put_msg("I",f"Sensor 4 usb port: {cda.portD}")
                logger.put_msg("I","------------")
                break
                        
        return
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.put_msg("E",f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")               
        logger.put_msg("E",f"pzemHandler.find_usb_ports Exception: {e}")