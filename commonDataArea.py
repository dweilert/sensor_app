"""
Author: Dave Weilert
Copyright(C) 2023 Freeware
Date: 3/19/2023

REVISION HISTORY
  DATE        AUTHOR          CHANGES
  yyyy/mm/dd  --------------- -------------------------------------
  2023/03/23  DaW             Initial creation 

OVERVIEW:
    Common module to store data used in multiple modules. 

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


# logger
log_dir = "~"
log_base = "monitor"
log_date = ""
log_file_name = ""
log_old_name = ""
log_sms = ""
log_first_time = True
log_messages = []

# monitor
getPortsCnt = 0
portA = "na"
portB = "na"
portC = "na"
portD = "na"

wait_to_check_sensors = 15
wait_to_check_for_ports = 15

# pzem
sensor_A_io_error = False
sensor_B_io_error = False
sensor_C_io_error = False
sensor_D_io_error = False

sensor_A_connect_error = False
sensor_B_connect_error = False
sensor_C_connect_error = False
sensor_D_connect_error = False

sensor_A_registers = []
sensor_B_registers = []
sensor_C_registers = []
sensor_D_registers = []

# Pump A data
pumpA_status = "OFF"
pumpA_start = ""
pumpA_stop = ""
pumpA_energy_start = 0
pumpA_energy_latest = 0
pumpA_cycle_cnt = 0
pumpA_cycles = []
pumpA_amp_high = 0
pumpA_amp_low = 0
pumpA_amp_avg = 0

# Pump B data
pumpB_status = "OFF"
pumpB_start = ""
pumpB_stop = ""
pumpB_energy_start = 0
pumpB_energy_latest = 0
pumpB_cycle_cnt = 0
pumpB_cycles = []
pumpB_amp_high = 0
pumpB_amp_low = 0
pumpB_amp_avg = 0

current_date = ""
iCnt = 0
error_cnt = 0

cpu_temps = []
cpu_ram = []
upsData = []

high_temp_cnt = 0
ups_charge_cnt = 0
ups_percent_cnt = 0

sensor_io_error_cnt = 0
all_sensors_io_error_cnt = 0
sensor_connect_error_cnt = 0

no_overall_power_cnt = 0
high_level_alarm_cnt = 0

resend_wait = 1440

resend_sensor_io_error_cnt = 0
resend_all_sensors_io_error_cnt = 0
resend_sensor_connect_error_cnt = 0

resend_sensor_no_power_cnt = 0
resend_sensor_no_data_cnt = 0
resend_sensor_amps_cnt = 0

resend_no_overall_power_cnt = 0
resend_high_level_alarm_cnt = 0

resend_rasp_temp_cnt = 0
resend_rasp_ups_charge_cnt = 0
resend_rasp_ups_percent_cnt = 0

error_stack = []

from_sensor = ""