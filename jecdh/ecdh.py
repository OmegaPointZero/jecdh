import base64
from datetime import datetime
import re
import os
import socket
import subprocess
import time

from py4j.java_gateway import JavaGateway, GatewayParameters


def _strip(string):
    string = string.decode("utf-8")
    headers = re.findall("(-----.*-----)", string)
    for header in headers:
        string = string.replace(header, "")
    string.replace("\n", "")
    return base64.b64decode(string)


class JECDH:
    def __init__(self, gateway_port=25333, timeout=600):

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip_address = '127.0.0.1'
        try:
            # Try to connect to the server
            client_socket.connect((ip_address, gateway_port))
            print("Server detected running on port %s."
                  "(Make sure this is your Java Gateway server if "
                  "you are having trouble)" % gateway_port)
            client_socket.close()
        except ConnectionRefusedError:
            # Kick off the script to start it, and make sure that the
            # script will kill it after the timeout specified.
            print("Server not detected on port %s, starting server...." % gateway_port)
            ts = time.time()
            print("[TIMESTAMP]: %s" % datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
            command = "python3 jecdh/runserver.py %s %s" % (gateway_port, timeout)
            print("Running script: %s" % command)
            command_list = command.split(" ")
            process = subprocess.Popen(command_list,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       shell=False)
            # Wait for the server to start before continuing, fixes errors in testing and automated workflows.
            time.sleep(1.5)
            print("Done, server started.")
            print("="*33)


        parameters = GatewayParameters(port=gateway_port)
        gateway = JavaGateway(gateway_parameters=parameters)
        # Close the socket
        client_socket.close()
        self.backend = gateway.entry_point
        self.private_key = None
        self.public_key = None
        self.private_key_type = "PEM"
        self.public_key_type = "X509"
        self.private_pass = ""
        self.private_types = ["PEM", "PKCS8", "PKCS12"]
        self.public_types = ["X509"]  # To do: Expand so it takes the raw bytes

    def set_private_key(self, private_key, key_type="PEM", passwd=""):
        if key_type == "PKCS12" and passwd == "":
            raise Exception(
                "Error: PKCS12 Keystores require a password. Keystores without a password are not supported.")
        if key_type == "PKCS12" or key_type == "PKCS8":
            private_key = _strip(private_key)
        elif key_type == "PEM":
            private_key = private_key.decode("utf-8")
        elif key_type not in self.private_types:
            raise Exception(
                "Unsupported private key type: %s. Available types: %s" % (
                key_type, str([x for x in self.private_types])))
        self.private_key = private_key
        self.private_key_type = key_type
        self.private_pass = passwd

    def set_public_key(self, public_key, key_type="X509"):
        if key_type == "X509":
            self.public_key = _strip(public_key)
        elif key_type not in self.public_types:
            raise Exception(
                "Unsupported public key type: %s. Available types: %s" % (
                key_type, str([x for x in self.public_types])))

    def exchange(self):
        if self.private_key is None:
            raise Exception("Error: No private key set. Use set_private_key() to set it.")
        elif self.public_key is None:
            raise Exception("Error: No public key set. Use set_public_key() to set it.")

        return self.backend.key_exchange(self.private_key,
                                  self.private_key_type,
                                  self.public_key,
                                  self.public_key_type,
                                  self.private_pass)