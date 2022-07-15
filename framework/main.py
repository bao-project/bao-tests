"""
Test framework main file
"""
import argparse
import signal
import threading
import time
import os
import subprocess
import uart
import constants as cons
import yaml_utils as yutils
from test_run import Runner



CFG_YAML_PATH = './config.yaml'
MAKE_LIST = []

parser = argparse.ArgumentParser(description="Bao Testing Framework")
parser.add_argument("--platform", help="Test target platform.")

if __name__ == '__main__':

    print(cons.BLUE_TEXT + "Framework init..." + cons.RESET_COLOR)

    # Parser - Load test config from yaml file
    yaml_cfg_data = yutils.load_config(CFG_YAML_PATH)
    if yaml_cfg_data is not None:
        platform_cfg = yutils.YAMLPatformCfg(yaml_cfg_data)
        PLAT_IDX = 0
        for platform in platform_cfg.platforms:
            print(cons.BLUE_TEXT + "Testing platformn: " + platform + cons.RESET_COLOR)
            architecture = cons.plat_arch_dict[platform]

            if platform_cfg.cross_compile is not None \
                    and len(platform_cfg.platforms) == len(platform_cfg.cross_compile):
                cross_compile = platform_cfg.cross_compile[PLAT_IDX]
                PLAT_IDX = PLAT_IDX + 1
            else:
                toolchain = cons.plat_toolchain_dict[architecture]
                cross_compile = yutils.select_toolchain(toolchain, platform_cfg.toolchain_path)
                cross_compile = platform_cfg.toolchain_path + cross_compile + '/bin/' \
                                + toolchain + "-"

            for test_setup in platform_cfg.setup_cfg:
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
                                            log_lvl=platform_cfg.log_level,
                                            csrcs=test_config.csrcs)

                    # Logging Monitor - Connect to testing platform and monitor test results
                    print(cons.BLUE_TEXT + "Connecting to Test Platform..." + cons.RESET_COLOR)

                    init_ports = uart.scan_pts_ports()
                    test_runner.run()
                    time.sleep(0.5)
                    final_ports = uart.scan_pts_ports()

                    new_ports = uart.diff_ports(init_ports, final_ports)

                    time.sleep(10)

                    HS_PORT = True
                    for port in new_ports:
                        fd = uart.establish_connection(port)
                        if fd is not None:
                            HS_PORT = uart.serial_handshake(fd)
                            if HS_PORT:
                                break

                    if HS_PORT:
                        print(cons.GREEN_TEXT +
                              "Test Platform launched and successfully connected to Test Framework."
                              + cons.RESET_COLOR)
                        thread = threading.Thread(target=uart.listener, args=[HS_PORT])
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
