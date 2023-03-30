import minimalmodbus

import logger

def clearEnergy(sensor):
    try: 
        pz = minimalmodbus.Instrument(sensor, 1)
        pz.serial.baudrate = 9600

        pz._performCommand(42, '')
        return "Zero out of energy has been completed"
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.put_msg("E",f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")               
        logger.put_msg("E",f"reset.clearEnergy ERROR: {e}")
        return 'Failed to zero out energy'
    
# Main section 
if __name__ == "__main__":
    # reset_usb()
    try:
        # Read config.ini file for parameters
        clearEnergy('/dev/ttyUSB0')
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.put_msg("E",f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")               
        logger.put_msg("E",f"reset.main ERROR: {e}")
