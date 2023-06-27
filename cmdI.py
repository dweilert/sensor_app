import os
import sys
import time
import subprocess

import commonDataArea as cda
import config
import logger

 
command_sent = False
results_check_cnt = 0
cmd_file = ""
results_file = ""

def writeCommand(cmd):
    try: 
        global command_sent
        global results_check_cnt
        command_sent = True
        deleteResults()
        results_check_cnt = 0
        f = open(cmd_file, "w")
        f.write(cmd)
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print(f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")
        print("WriteCommand Error")
    finally: 
        f.close()


def deleteResults():   
    try: 
        if os.path.exists(results_file):
            os.remove(results_file)
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print(f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        print("Delete results file error")


def getResults():
    try: 
        global command_sent
        global results_check_cnt
        if os.path.exists(results_file):
            f = open(results_file,"r")
            print(f.read())
            command_sent = False
            results_check_cnt = 0
            deleteResults()
            return True
        else:
            return False
    except Exception as e: 
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print(f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        print(f"Get results file error: {e}")
        return False


def show_help():
    print(" ")
    print(" Valid commands: ")
    print("   all   - get all data")
    print("    c    - count of intervals since today")
    print("    d    - daily pump count and high amps")
    print("    f    - free and used memory information")
    print("    h    - show this help information")
    print("    l    - all log data")
    print("    l_#  - request a specific number of log entries")
    print("           Example: l_25 will retrieve the last 25 log entries")
    print("    p    - pump information, both pumps")
    print("    q    - quit command interface")
    print("    r    - register information for all sensors")
    print("    s    - sensors USB mappings and status")
    print("    t    - temperature information for Raspberry Pi")
    print("    u    - ups information for Raspberry Pi")
    print("    w    - wrap logs (reduce log stack by 50%)")
    print(" ")
    print("  Monitor service related commands")
    print("    m_status  - get monitor service status")
    print(" ")
    print("    For Monitor start, stop, or restart exit this CLI and issue command: ")
    print("      systemclt <start | stop | restart> monitor (without < >)")
    print(" ")
    print("  SMS related commands")
    print("    sms_own   - send test SMS message to owners")
    print("    sms_man   - send test SMS message to maintenace")
    print("    sms_dev   - send test teXt message to developer")
    print(" ")
    print("    all_clear - send all clear SMS to owners.  Send this after issues are resovled.")
 
    print(" ")
    print("---")


def getCommand():
    try:
        global command_sent
        global results_check_cnt
        dots = ""
        while True:
            qty = 0
            prompt = "Enter command: "
            cmd = input(prompt)
            # determine if the cmd is a log request
            if "l_" in cmd:
                parts = cmd.split("_")
                qty = checkValue(parts[1])
                if qty == 0:
                    print("Invalid number in logs request. Example: l_17 to get last 17 lines in log.")
                    print("\n" + "---")
                    command_sent = False
                else:
                    data = "logs_" + str(qty)
                    writeCommand(data)
            elif cmd == "l":
                writeCommand("logs_999999")
            elif cmd == "q":
                print("Command interface closed")
                print("\n"+"---")
                break

            elif cmd == "all":
                writeCommand("get_all")
            elif cmd == "all_clear":
                writeCommand("all_clear")
            elif cmd == "c":
                writeCommand("count")
            elif cmd == "d":
                writeCommand("daily")                
            elif cmd == "f":
                writeCommand("memory")
            elif cmd == "h":
                show_help()
            elif cmd == "l":
                writeCommand("logs_" + str(qty))
            elif cmd == "m_status":
                callMonitor("status")
            elif cmd == "p":
                writeCommand("pumps")
            elif cmd == "u":
                writeCommand("ups")
            elif cmd == "r":
                writeCommand("r")
            elif cmd == "s":
                writeCommand("sensors")
            elif cmd == "sms_own":
                writeCommand("sms_own")                
            elif cmd == "sms_man":
                writeCommand("sms_man")                
            elif cmd == "sms_dev":
                writeCommand("sms_dev")
            elif cmd == "sms_daily":
                writeCommand("sms_daily")                                
            elif cmd == "t":
                writeCommand("temp")
            elif cmd == "w":
                writeCommand("wrap")                                
            else:
                print("Invalid command, type h for help")
                print("\n" + "---")
                command_sent = False

            time.sleep(0.75)
            if command_sent == True:
                while True:
                    if getResults() == True:
                        print("---")
                        dots = ""
                        break
                    else:
                        results_check_cnt = results_check_cnt + 1
                        dots = dots + "."
                        if results_check_cnt > 8:
                            print("stopped waiting for results, retry", end="\r")
                            break
                        print("waiting " + dots, end="\r")
                        time.sleep(2)


    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print(f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")             
        print(f"Input error: {e}")

def checkValue(v):
    try:
        nV = int(v)
        return nV
    except Exception as e:
        return 0


def callMonitor(cmd):
    try:
        info = subprocess.run(["systemctl",cmd,"monitor"], capture_output=True, text=True)
        lines = info.stdout
        newLines = lines.splitlines()
        print("\nMonitor service Information\n")
        for l in newLines:
            print("  " + l)
        # return lines
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.msg("E",f"callMonitor() Exception type: {exception_type} File name: {filename} Line number: {line_number}")        
        logger.msg("E",f"callMonitor() {e}")
        return "Error getting monitor.service status"


# Main section 
if __name__ == "__main__":
    # reset_usb()
    try:
        config.readConfig()
        cmd_file = config.get("CommandInterface","cmd_file")
        results_file = config.get("CommandInterface","results_file")
        print(f" - Command input file: {cmd_file}")
        print(f" - Result output file: {results_file}")
        print(f" - Enter h for help information")
        getCommand()
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print(f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")             

        print(f'Command Interface Error {e}')
        sys.exit(1)