#!/bin/sh
#  This script reads the Broadcom SoC temperature value and shuts down if it
#  exceeds a particular value.
#  80ºC is the maximum allowed for a Raspberry Pi.


# Get the reading from the sensor and strip the non-number parts
SENSOR="`/opt/vc/bin/vcgencmd measure_temp | cut -d "=" -f2 | cut -d "'" -f1`"
# -gt only deals with whole numbers, so round it.
TEMP="`/usr/bin/printf "%.0f\n" ${SENSOR}`"
# How hot will we allow the SoC to get?
MAX="60"

if [ "${TEMP}" -gt "${MAX}" ] ; then
 # This will be mailed to root if called from cron
 echo "${TEMP}ºC is too hot!"
 # Send a message to syslog
 /usr/bin/logger "Shutting down due to SoC temp ${TEMP}."
 # Halt the box
 pkill fbi
 pkill kodi
 sudo /sbin/shutdown -h now
 echo "Initiating shutdown..."
 else
  exit 0
fi

