import os
import sys
import time

import commonDataArea as cda
import config

 
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
    print("  Valid commands: ")
    print("    f  - free and used memory information")
    print("    h  - show this help information")
    print("    l  - log data")
    print("    m  - monitor service current status")
    print("    p  - pump information, both pumps")
    print("    q  - quit command interface")
    print("    r1 - register information for sensor 1 ")
    print("    r2 - register information forsensor 2 register")
    print("    r3 - register information forsensor 3 register")
    print("    r4 - register information forsensor 4 register")
    print("    s  - sensors USB mappings and status")
    print("    t  - temperature information for Raspberry Pi")
    print("    u  - ups information for Raspberry Pi")
    print("  SMS related commands")
    print("    sms_own   - send test SMS message to owners")
    print("    sms_man   - send test SMS message to maintenace")
    print("    sms_dev   - send test teXt message to developer")
    print("    sms_fixed - send all clear SMS to owners.  Send this after issues are resovled.")
 
    print(" ")
    print("---")


def getCommand():
    try:
        global command_sent
        global results_check_cnt
        dots = ""
        while True:
            prompt = "Enter command: "
            cmd = input(prompt)
            if cmd == "q" or cmd == "quit":
                print("Command interface closed")
                print("\n"+"---")
                break
            elif cmd == "h":
                show_help()
            elif cmd == "s":
                writeCommand("sensors")
            elif cmd == "f":
                writeCommand("memory")
            elif cmd == "p":
                writeCommand("pumps")
            elif cmd == "m":
                writeCommand("monitor")
            elif cmd == "l":
                writeCommand("logs")
            elif cmd == "u":
                writeCommand("ups")
            elif cmd == "t":
                writeCommand("temp")
            elif cmd == "r1":
                writeCommand("r1")
            elif cmd == "r2":
                writeCommand("r2")
            elif cmd == "r3":
                writeCommand("r3")
            elif cmd == "r4":
                writeCommand("r4")
            elif cmd == "sms_own":
                writeCommand("sms_own")                
            elif cmd == "sms_man":
                writeCommand("sms_man")                
            elif cmd == "sms_dev":
                writeCommand("sms_dev")                
            elif cmd == "sms_fixed":
                writeCommand("sms_fixed")                
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


# Main section 
if __name__ == "__main__":
    # reset_usb()
    try:
        config.readConfig()
        cmd_file = config.get("CommandInterface","cmd_file")
        results_file = config.get("CommandInterface","results_file")

        getCommand()
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print(f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")             

        print(f'Command Interface Error {e}')
        sys.exit(1)