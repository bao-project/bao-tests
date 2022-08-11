"""
    Copyright (c) 2021-2023, Bao Project (www.bao-project.com). All rights reserved.

    SPDX-License-Identifier: Apache-2.0

    UART utils submodule
"""
import subprocess
import time
import serial
import constants as cons

MAX_TRIALS = 1000


def scan_pts_ports():
    """
    Scan available pts ports
    """
    std_out = subprocess.run(['ls', '/dev/pts/'], stdout=subprocess.PIPE, check=True)
    std_out = std_out.stdout.decode('ASCII')
    ports = std_out.split()
    return ports


def diff_ports(ports_init, ports_end):
    """
    Find allocated pts ports
    """
    diff = list(set(ports_end) - set(ports_init))
    return diff


def listener(ser_port):
    """
    Listener to receive test results
    """

    # Send run command
    tx_buffer = "[TESTF-PY] run\n"
    ser_port.write(tx_buffer.encode())

    # Wait for response
    time.sleep(0.5)

    # continuously listen to commands on the master device
    while cons.TEST_RESULTS == '':
        res = b""
        while not (res.endswith(b"\r\n") and b"[TESTF-C]" in res):
            res += ser_port.read(64)
            if res == b'':
                print("res list: ", res)
                ser_port.write(b"[TESTF-PY] run")

        res_str = str(res)
        res_str = res_str.replace('\\r\\n', '\r\n')[2:-1]
        res_str = res_str.replace('\\x1b[0m\\x1b[1;', '\\x1b[1;')
        res_str = res_str.replace('\\x1b[1;', '\033[')
        res_str = res_str.replace('\\x1b', '\033')
        res_str = res_str.replace('#$#', '#')
        print(res_str, end="\r\n")

        for line in res_str.split("\n"):
            if "[TESTF-C]" in line:
                cons.TEST_RESULTS = line


def serial_handshake(port):
    """
    Validate connection between test framework and platform
    """

    port_name = '/dev/pts/' + str(port)
    ser = serial.Serial(port_name,
                        cons.UART_BAUDRATE,
                        timeout=cons.UART_TIMEOUT
                        )
    print(cons.BLUE_TEXT +
          "Connecting to " +
          port_name +
          "..." +
          cons.RESET_COLOR)

    ser.close()
    ser.open()
    time.sleep(2)

    # Send init command
    tx_buffer = "[TESTF-PY] init\n"
    ser.write(tx_buffer.encode())

    # Wait for response
    time.sleep(0.5)

    # Read init command
    rx_buffer = ser.readline(64)

    # If acknowledge received, return serial port
    rx_tag = bytes(cons.C_TAG + ' init', 'ascii')

    if rx_tag in rx_buffer:
        return ser

    print(cons.RED_TEXT +
          "Unable to connect to " +
          port_name +
          cons.RESET_COLOR)
    return None
