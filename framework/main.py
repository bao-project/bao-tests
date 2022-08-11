"""
Copyright (c) 2021-2023, Bao Project (www.bao-project.com). All rights reserved.

SPDX-License-Identifier: Apache-2.0

Test framework main file
"""
import argparse
import signal
import threading
import time
import os
import subprocess
import shutil
import uart
import constants as cons
import yaml_utils as yutils
from test_run import Runner



CFG_YAML_PATH = './config.yaml'
MAKE_LIST = []

PARSER = argparse.ArgumentParser(description="Bao Testing Framework")
PARSER.add_argument("--platform", help="Test target platform.")

if __name__ == '__main__':

    print(cons.BLUE_TEXT + "Framework init..." + cons.RESET_COLOR)

    if os.path.isdir("./__pycache__"):
        shutil.rmtree("./__pycache__")
    if os.path.isdir("./.idea"):
        shutil.rmtree("./.idea")

    # Parser - Load test config from yaml files
    YAML_CFG_DATA = yutils.load_config(CFG_YAML_PATH)
    if YAML_CFG_DATA is not None:
        PLATFORM_CFG = yutils.YAMLPatformCfg(YAML_CFG_DATA)
        PLAT_IDX = 0
        for platform in PLATFORM_CFG.platforms:
            print(cons.BLUE_TEXT + "Testing platformn: " + platform + cons.RESET_COLOR)
            architecture = cons.PLAT_ARCH_DICT[platform]

            if PLATFORM_CFG.cross_compile is not None \
                    and len(PLATFORM_CFG.platforms) == len(PLATFORM_CFG.cross_compile):
                cross_compile = PLATFORM_CFG.cross_compile[PLAT_IDX]
                PLAT_IDX = PLAT_IDX + 1
            else:
                toolchain = cons.PLAT_TOOLCHAIN_DICT[architecture]
                cross_compile = yutils.select_toolchain(toolchain, PLATFORM_CFG.toolchain_path)
                cross_compile = PLATFORM_CFG.toolchain_path + cross_compile + '/bin/' \
                                + toolchain + "-"

            for test_setup in PLATFORM_CFG.setup_cfg:
                print(cons.BLUE_TEXT + "Test config: " + test_setup + cons.RESET_COLOR)

                test_yaml_data = yutils.load_config(test_setup)
                test_config = yutils.YAMLTestCfg(test_yaml_data)

                for mut_idx in range(test_config.n_mut):
                    mut = test_config.list_mut[mut_idx]
                    test_config.set_mut_tests(mut)
                    test_config.generate_makes()

                    # Run - Launch QEMU and run tests
                    print(cons.BLUE_TEXT + "Creating runner..." + cons.RESET_COLOR)

                    test_runner = Runner(platform=platform,
                                         arch=architecture,
                                         cross_compile=cross_compile,
                                         make_cmd_list=MAKE_LIST)

                    print(cons.BLUE_TEXT + "Building setup..." + cons.RESET_COLOR)
                    test_runner.build_setup(tests_list=test_config.make_cmd,
                                            log_lvl=PLATFORM_CFG.log_level,
                                            csrcs=test_config.csrcs)

                    # Logging Monitor - Connect to testing platform and monitor test results
                    print(cons.BLUE_TEXT + "Connecting to Test Platform..." + cons.RESET_COLOR)

                    init_ports = uart.scan_pts_ports()
                    test_runner.run()
                    time.sleep(0.5)
                    final_ports = uart.scan_pts_ports()

                    new_ports = uart.diff_ports(init_ports, final_ports)

                    SER_PORT = False
                    for port in new_ports:
                        SER_PORT = uart.serial_handshake(port)
                        if SER_PORT:
                            break

                    if SER_PORT:
                        print(cons.GREEN_TEXT +
                              "Test Platform launched and successfully connected to Test Framework."
                              + cons.RESET_COLOR)
                        thread = threading.Thread(target=uart.listener, args=[SER_PORT])
                        thread.start()
                        thread.join()
                    else:
                        print(cons.RED_TEXT +
                              "Unable to connect to Testing Platform." +
                              cons.RESET_COLOR)

                    # Clear all subprocesses
                    for pid in test_runner.qemu_pid_list:
                        try:
                            os.kill(pid, signal.SIGTERM)
                        except OSError:
                            continue

                    if len(test_runner.qemu_pid_list) > 0:
                        RUN_PID = subprocess.check_output("pidof make run", shell=True)
                        RUN_PID = int(RUN_PID.decode())
                        try:
                            os.kill(RUN_PID, signal.SIGTERM)
                        except OSError:
                            continue

                    print("Test " + test_setup + " finished...")
                    print(cons.TEST_RESULTS)
                    cons.test_results = ''
