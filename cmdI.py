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
        if os.path.exists(results_file):
            f = open(results_file,"r")
            print(f.read())
            command_sent = 0
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
    print("    status  - get current status of monitor service")
    print("    pumps   - show information regarding pumps")
    print("    sensors - get list of sensors that are currently monitoring environment")
    print("    help    - show this help information")
    print("    quit    - stop command interface")


def getCommand():
    try:
        while True:
            print("Enter command: ")
            cmd = input()
            if cmd == "q" or cmd == "quit":
                print("Command interface closed")
                break
            elif cmd == "help":
                show_help()
            elif cmd == "status":
                writeCommand(cmd)
            elif cmd == "pumps":
                writeCommand(cmd)
            elif cmd == "sensors":
                writeCommand(cmd)
            else:
                print("Invalid command, type help for valid commands")

            if command_sent == True:
                while True:
                    if getResults == True:
                        print("---")
                        break
                    else:
                        results_check_cnt = results_check_cnt + 1
                        if results_check_cnt > 3:
                            print("stopped waiting for command results, retry")
                            break
                        print("waiting for command results")
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
        print(cmd_file + " " + results_file)
        getCommand()
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print(f"Exception type: {exception_type} File name: {filename} Line number: {line_number}")             

        print(f'Command Interface Error {e}')
        sys.exit(1)