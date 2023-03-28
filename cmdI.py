import os
import sys
import time

import commonDataArea as cda
import config
 
command_sent = False
results_check_cnt = 0

def writeCommand(cmd):
    try: 
        command_sent = True
        deleteResults()
        results_check_cnt = 0

        f = open(config.get("CommandInterface","cmd_file"), "w")
        f.write(cmd)
    finally: 
        f.close()


def deleteResults():    
    if os.path.exists(config.get("CommandInterface","results_file")):
        os.remove(config.get("CommandInterface","results_file"))


def checkForResults():
    try: 
        if os.path.exists(config.get("CommandInterface","results_file")):
            f = open(config.get("CommandInterface","results_file"),"r")
            for line in f:
                print(line)
            f.close()
            command_sent = 0
            results_check_cnt = 0
            deleteResults()
            return True
        else:
            return False
    except Exception as e: 
        print(f"Get results error: {e}")


def show_help():
    print(" ")
    print("  Valid commands: ")
    print("    status  - get current status of monitor service")
    print("    pumps   - show information regarding pumps")
    print("    sensors - get list of sensors that are currently monitoring environment")
    print("    help    - show this help information")
    print("    quit    - stop command interface")


def getCommand():
    while True:
        try:
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
                    if checkForResults == True:
                        print("---")
                        break
                    else:
                        results_check_cnt = results_check_cnt + 1
                        print("waiting for command results")
                        time.sleep(2)


        except Exception as e:
            print(f"Input error: {e}")


# Main section 
if __name__ == "__main__":
    # reset_usb()
    try:
        getCommand()
    except Exception as e:
        print(f'Error {e}')
        sys.exit(1)