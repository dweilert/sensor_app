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

Register       Description                      Resolution
address
-------------------------------------------------------------------------------
0x0000      Voltage value               Measuring range: 80-260V 
            Volts                       Resolution: 0.1V
                                        Measurment accuracy: 0.5%
                                        What is being supplied on the 110
                                        leads connected to the PZEM

0x0001      Current (low 16 bits)       Measuring range: 0-100A 
            AMPS                        Starting measuring current: 0.02A
                                        Resolution: 0.001A
                                        Measurment accuracy: 0.5%
                                        Amps being seen when monitored device
                                        is being used

0x0002      Current (high 16 bits)

0x0003      Power (low 16 bits)         Measuring range: 0-23kW 
            Watts                       Starting measuring power: 0.4W, 
                                        Resolution: 0.1W
                                        Format: <1000W one decimal, >=1000W only integer
                                        Measurment accuracy: 0.5% 
                                        Watts being seen when monitored device
                                        is being used

0x0004      Power (high 16 bits)         

0x0005      Energy (low 16 bits)        Measuring range: 0-999.99 kWh, 
            kWh                         Resolution: 1 Wh, 
                                        Measurment accuracy: 0.5%
                                        Format: <10kWh integer Wh, >=10kWh then kWh

0x0006      Energy (high 16 bits)   

0x0007      Frequency                   Measuring range: 45-65 Hz, 
            Hz                          Resolution: 0.1 Hz, 
                                        Measurment accuracy: 0.5%

0x0008      Power factor                Measuring range: 0.00-1.00, 
                                        Resolution: 0.01, 
                                        Measurment accuracy: 1%

0x0009      Alarm status                0xFFFF alarm is on
                                        0x0000 alarm is off
                                        PF power fault

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


def resetEnergy(usbPort):
    # Not currently working
    try:
        client = ModbusSerialClient(port=usbPort, timeout=int(config.get(
            "Pzem", "timeout")), baudrate=9600, bytesize=8, parity="N", stopbits=1)
        client.connect()
        result = client.write_register(1, 0x42)
        print(result)
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg(
            "E", f"resetEnergy() Exception type: {exception_type} File name: {filename} Line number: {line_number}")
        logger.msg("E", f"resetEnergy() {e}")


def readSensor(usbPort, id):
    # Get register data
    try:
        rtn = []
        # Check if sensor was found, if not skip
        if cda.portA == "na" and id == "A":
            rtn = []
            rtn.append(False)
            rtn.append("na")
            return rtn
        if cda.portB == "na" and id == "B":
            rtn = []
            rtn.append(False)
            rtn.append("na")
            return rtn
        if cda.portC == "na" and id == "C":
            rtn = []
            rtn.append(False)
            rtn.append("na")
            return rtn
        if cda.portD == "na" and id == "D":
            rtn = []
            rtn.append(False)
            rtn.append("na")
            return rtn

        client = ModbusSerialClient(port=usbPort, timeout=int(config.get(
            "Pzem", "timeout")), baudrate=9600, bytesize=8, parity="N", stopbits=1)
        status = client.connect()

        # If the connection to the sensor fails flag it as a connection error
        # and return and build Failed return data array
        if status != True:
            client = None
            if id == "A":
                cda.sensor_A_connect_error = True
            elif id == "B":
                cda.sensor_B_connect_error = True
            elif id == "C":
                cda.sensor_C_connect_error = True
            elif id == "D":
                cda.sensor_D_connect_error = True

            rtn = []
            rtn.append(False)
            rtn.append("connection failed")
            return rtn

        # No connection error so continue and get the sensor register data
        # and convert to a string
        request = client.read_input_registers(0, 10, 1)
        rType = type(request)
        rType = str(rType)

        # Check if the sensor register data is located then process. Else
        # check the data for erros and return the data as an error.
        if "pymodbus.register_read_message.ReadInputRegistersResponse" in rType:

            # If either one of the pumps SAVE the data
            if id == "A" or id == "B":
                dataHandler.saveData(request.registers, id)

            # No errors so set flags to False
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

            rtn = []
            rtn.append(True)
            rtn.append(request.registers)
            client.close()
            return rtn

        # Two specific errors are captured IO Error and Connection Error.  All
        # other issues are treated as Other Errors

        elif "pymodbus.exceptions.ModbusIOException" in rType:
            if id == "A":
                cda.sensor_A_io_error = True
            elif id == "B":
                cda.sensor_B_io_error = True
            elif id == "C":
                cda.sensor_C_io_error = True
            elif id == "D":
                cda.sensor_D_io_error = True

            rtn = []
            rtn.append(False)
            rtn.append("IOException")
            client.close()
            return rtn

        elif "pymodbus.exceptions.ConnectionException" in rType:
            if id == "A":
                cda.sensor_A_connect_error = True
            elif id == "B":
                cda.sensor_B_connect_error = True
            elif id == "C":
                cda.sensor_C_connect_error = True
            elif id == "D":
                cda.sensor_D_connect_error = True

            rtn = []
            rtn.append(False)
            rtn.append("ConnectionError")
            client.close()
            return rtn

        else:
            rtn = []
            rtn.append(False)
            rtn.append(f"Other {rType}")
            client.close()
            return rtn

    except Exception as e:
        errorLine = f"Exception: {e}"
        if config.get("Pzem", "ioException") in errorLine:
            if id == "A":
                cda.sensor_A_io_error = True
            elif id == "B":
                cda.sensor_B_io_error = True
            elif id == "C":
                cda.sensor_C_io_error = True
            elif id == "D":
                cda.sensor_D_io_error = True

        if config.get("Pzem", "connectionError") in errorLine:
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

        # If "Errno 71" is located increase the counter
        eStr = f"type: {e}"
        if "Errno 71" in eStr:
            eStr = None
            cda.Errno71_cnt = cda.errno71_cnt + 1

        logger.msg(
            "E", f"readSensor() Exception type: {exception_type} File name: {filename} Line number: {line_number}")
        logger.msg("E", f"readSensor() PzemHandler.monitor() error type: {e}")
        logger.msg("E", f"readSensor() usbPort: {usbPort} id: {id}")

        rtn = []
        rtn.append(False)
        rtn.append(exception_type)
        return rtn


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

        # Initial values for USB ports
        cda.portA = "na"
        cda.portB = "na"
        cda.portC = "na"
        cda.portD = "na"

        # Get port signature values to search for in the dmesg data
        portA_sig = config.get("USBPortSignatures", "portA")
        portB_sig = config.get("USBPortSignatures", "portB")
        portC_sig = config.get("USBPortSignatures", "portC")
        portD_sig = config.get("USBPortSignatures", "portD")
        disconn = config.get("USBPortSignatures", "disconn")

        while True:
            line = lines[ln]
            if config.get("Debug", "show_dmesg") == "true":
                print(line)
            if disconn in line:
                chkUSB = '/dev/ttyUSB' + line[-1]

                if cda.portA == chkUSB:
                    if config.get("Debug", "show_dmesg") == "true":
                        logger.msg(
                            "I", f"Sensor 1 disconned from USB port: {chkUSB}")
                    cda.portA = "na"
                elif cda.portB == chkUSB:
                    if config.get("Debug", "show_dmesg") == "true":
                        logger.msg(
                            "I", f"Sensor 2 disconned from USB port: {chkUSB}")
                    cda.portB = "na"
                elif cda.portC == chkUSB:
                    if config.get("Debug", "show_dmesg") == "true":
                        logger.msg(
                            "I", f"Sensor 3 disconned from USB port: {chkUSB}")
                    cda.portC = "na"
                elif cda.portD == chkUSB:
                    if config.get("Debug", "show_dmesg") == "true":
                        logger.msg(
                            "I", f"Sensor 4 disconned from USB port: {chkUSB}")
                    cda.portD = "na"

            if portA_sig in line:
                if cda.portA == "na":
                    if len(line) > 65:
                        pid = line[65:72]
                        cda.portA = "/dev/" + pid
                        if config.get("Debug", "show_dmesg") == "true":
                            logger.msg(
                                "I", f"Sensor 1 set to USB port: {cda.portA}")

            if portB_sig in line:
                if cda.portB == "na":
                    if len(line) > 65:
                        pid = line[65:72]
                        cda.portB = "/dev/" + pid
                        if config.get("Debug", "show_dmesg") == "true":
                            logger.msg(
                                "I", f"Sensor 2 set to USB port: {cda.portB}")

            if portC_sig in line:
                if cda.portC == "na":
                    if len(line) > 65:
                        pid = line[65:72]
                        cda.portC = "/dev/" + pid
                        if config.get("Debug", "show_dmesg") == "true":
                            logger.msg(
                                "I", f"Sensor 3 set to USB port: {cda.portC}")

            if portD_sig in line:
                if cda.portD == "na":
                    if len(line) > 65:
                        pid = line[65:72]
                        cda.portD = "/dev/" + pid
                        if config.get("Debug", "show_dmesg") == "true":
                            logger.msg(
                                "I", f"Sensor 4 set to USB port: {cda.portD}")

            # Increase line in the dmesg data to get
            ln = ln + 1

            # No more lines to process
            if ln >= hl:
                # logger.msg("I", "------------")
                # logger.msg("I", f"Sensor 1 usb port: {cda.portA}")
                # logger.msg("I", f"Sensor 2 usb port: {cda.portB}")
                # logger.msg("I", f"Sensor 3 usb port: {cda.portC}")
                # logger.msg("I", f"Sensor 4 usb port: {cda.portD}")
                # logger.msg("I", "------------")
                break

        return
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg(
            "E", f"find_usb_ports() Exception type: {exception_type} File name: {filename} Line number: {line_number}")
        logger.msg("E", f"find_usb_ports() {e}")
