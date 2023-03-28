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
        #print("\n")
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
    print("    s (or) status  - get current status of monitor service")
    print("    p (or) pumps   - show information regarding pumps")
    print("    m (or) monitor - get list of sensors that are currently monitoring environment")
    print("    h (or) help    - show this help information")
    print("    q (or) quit    - stop command interface")
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
            elif cmd == "help" or cmd == "h":
                show_help()
            elif cmd == "status" or cmd == "s":
                writeCommand("status")
            elif cmd == "pumps" or cmd == "p":
                writeCommand("pumps")
            elif cmd == "monitor" or cmd == "m":
                writeCommand("monitor")
            elif cmd == "logs" or cmd == "l":
                writeCommand("logs")
            else:
                print("Invalid command, type help for valid commands")
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
                        if results_check_cnt > 5:
                            print("stopped waiting for command results, retry", end="\r")
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