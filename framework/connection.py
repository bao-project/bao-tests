"""
Copyright (c) Bao Project and Contributors. All rights reserved
SPDX-License-Identifier: Apache-2.0
UART utils submodule
"""
import subprocess
import threading
import serial
import constants as cons

thread_finished = threading.Event()
stop_event = threading.Event()

def scan_pts_ports():
    """
    Scan available pts ports
    """
    std_out = subprocess.run(['ls', '/dev/pts/'],
                             stdout=subprocess.PIPE,
                             check=True)
    std_out = std_out.stdout.decode('ASCII')
    ports = std_out.split()
    return ports

def diff_ports(ports_init, ports_end):
    """
    Find allocated pts ports
    """
    diff = list(set(ports_end) - set(ports_init))
    return diff


def connect_to_platform_port(ports_list, echo):
    """
    Establishes connections to multiple serial ports concurrently and starts a
    listener thread for each port.

    Args:
        ports_list (list): A list of serial port names (e.g., ['COM1',
        '/dev/ttyUSB0']).
    """

    threads = []

    for port in ports_list:
        ser_port = open_connection(port)
        new_thread = threading.Thread(target=listener, args=[ser_port, echo])
        threads.append(new_thread)

    for thread in threads:
        thread.start()

    thread_finished.wait()
    stop_event.set()

    for thread in threads:
        thread.join()

def listener(ser_port, echo):
    """
    Listener to receive test results
    """
    replacements = [
        ('\\r\\n', '\r\n'),
        ('\\x1b[0m\\x1b[1;', '\\x1b[1;'),
        ('\\x1b[1;', '\033['),
        ('\\x1b', '\033'),
        ('#$#', '#')
    ]

    while not stop_event.is_set():
        res = b""
        res_log = []
        while not (res.endswith(b"\r\n") and b"[TESTF-C]" in res):
            res = ser_port.readline()
            new_line = res.decode(errors='ignore')
            for old, new in replacements:
                new_line = new_line.replace(old, new)
            res_log.append(new_line)

            if (b"[INFO]" in res) and (echo):
                print(new_line, end="")

            if stop_event.is_set():
                break

        for line in res_log:
            #print("line: " + line)
            if "[TESTF-C]" in line:
                if echo:
                    print(line)
                cons.TEST_RESULTS = line
                thread_finished.set()

    print(cons.BLUE_TEXT +
          "Closing connection to " +
          ser_port.name +
          "..." +
          cons.RESET_COLOR)

    ser_port.close()


def open_connection(port):
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

    return ser
