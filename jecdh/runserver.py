import os
import signal
import subprocess
import sys


def run_java_with_timeout(timeout, port_number):
    print("-"*77)
    current_script_path = os.path.abspath(__file__)
    current_script_dir = os.path.dirname(current_script_path)
    java_files_dir = os.path.dirname(current_script_dir) + "/java/"
    os.chdir(java_files_dir)
    command1 = "javac -cp py4j.jar:bouncycastle.jar:bcprov-jdk18on-171.jar:. EllipticCurve.java"
    command2 = "java -cp py4j.jar:bouncycastle.jar:bcprov-jdk18on-171.jar:. EllipticCurve %s" % port_number
    print("Working in directory: %s" % java_files_dir)
    # Create the subprocess
    print("Running command number one: ")
    print(command1)
    os.system(command1)
    print("...Done.\nNow attempting to run command number two:")
    print(command2)
    proc = subprocess.Popen(command2, shell=True)

    # Set a timeout and kill the process if it exceeds the specified time
    def kill_proc():
        if proc.poll() is None:
            print("Timeout reached, killing the process...")
            proc.kill()
    signal.signal(signal.SIGALRM, kill_proc)
    signal.alarm(timeout)

    # Wait for the process to finish
    try:
        stdout, stderr = proc.communicate()
    except subprocess.TimeoutExpired:
        # The timeout was reached
        kill_proc()
        stdout, stderr = proc.communicate()
    # Cancel the timeout alarm
    signal.alarm(0)
    print(stdout.decode('utf-8'))
    os.chdir(current_script_dir)
    return proc.returncode


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 1:
        to = 600
        port = 25333
    elif len(args) != 3:
        print("Usage: python3 runserver.py (Default args Only)")
        print("Usage: python3 runserver.py <port_number> <timeout>")
        sys.exit()
    elif len(args) == 3:
        to = int(args[2])
        port = int(args[1])
    print("Attempting to run on %i for %i seconds" % (to, port))
    run_java_with_timeout(to, port)
