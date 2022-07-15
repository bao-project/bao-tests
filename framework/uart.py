"""
UART utils submodule
"""
import os
import subprocess
import time
from serial import Serial
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


def listener(port):
    """
    Listener to receive test results
    """
    # continuously listen to commands on the master device
    while cons.TEST_RESULTS == '':
        res = b""
        while not res.endswith(b"#$#\r\n"):
            # keep reading one byte at a time until we have a full line
            res += os.read(port, 1)
            if res == b'':
                print("res: ", res)
                time.sleep(0.2)

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


def establish_connection(port):
    """
    Establish connection between test framework and platform
    """
    file_desc = None
    port_name = '/dev/pts/' + port
    print("Connecting to ", port_name, " ...")

    try:
        file_desc = os.open(port_name, os.O_RDWR)
    except OSError:
        file_desc = None
        print("Port ", port_name, " not available")
    return file_desc


def serial_handshake(port):
    """
    Validate connection between test framework and platform
    """
    port_name = os.ttyname(port)
    ser = Serial(port_name, cons.UART_BAUDRATE, timeout=cons.UART_TIMEOUT)
    ack_signal = []
    res = b""
    for char in cons.UART_HS_CODE:
        ser.write(char.encode())
        trials = 0
        while not res.endswith(b"\n") and trials < cons.UART_HS_MAXTRIALS:
            # keep reading one byte at a time until we have a full line
            res += ser.read(1)
            # res += os.read(port, 1)
            trials += 1
            time.sleep(1 / 4000)
        ack_signal.append(res[0:3].decode())
        res = b""

    if ack_signal.count('#$#') > 5:
        return port

    return None
