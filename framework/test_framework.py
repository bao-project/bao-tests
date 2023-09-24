# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Bao Project and Contributors. All rights reserved

"""
Test framework main file
"""
import argparse
import os
import sys
import subprocess
import psutil
import constants as cons
from pydevicetree import Devicetree

PARSER = argparse.ArgumentParser(description="Bao Testing Framework")
PARSER.add_argument("--dts_path", help="Path to .dts configuration file")

test_config = {
    'nix_file': '',
    'suites': '',
    'tests': '',
    'tests_configs': {
        'log_level': ''
    }
}

def parse_dts_file(file_path):
    """
    Parse a DTS (Device Tree Source) file and extract relevant information.

    Args:
        file_path (str): The path to the DTS configuration file.
    """
    tree = Devicetree.parseFile(file_path)
    test_config['platform'] = \
        tree.children[0].properties[0].values[0]
    test_config['nix_file'] = \
        tree.children[0].children[0].children[0].properties[0].values[0]
    test_config['suites'] = \
        tree.children[0].children[0].children[0].properties[1].values[0]
    test_config['tests'] = \
        tree.children[0].children[0].children[0].properties[2].values[0]
    test_config['tests_configs']['log_level'] = \
        tree.children[0].children[0].children[0].properties[2].values[0]

def run_command_in_terminal(command):
    """
    Run a command in a new Terminal window.

    Args:
        command (str): The command to execute.
    """
    # pylint: disable=R1732
    terminal_process = subprocess.Popen(
        ['/bin/bash', '-c', command],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE
    )
    # pylint: enable=R1732

    return terminal_process

def terminate_children_processes(parent_process):
    """
    Terminate all child processes of the given parent process.

    Args:
        parent_process: The parent process whose children will be terminated.
    """
    parent = psutil.Process(parent_process.pid)
    children = parent.children(recursive=True)
    for child in children:
        child.terminate()
        child.wait()

def deploy_test(platform):
    """
    Deploy a test on a specific platform.

    Args:
        platform (str): The platform to deploy the test on.
    """
    if platform in ["qemu-aarch64-virt", "qemu-riscv64-virt"]:
        arch = platform.split("-")[1]
        run_cmd = "../platform/qemu/run.sh " + arch
        process = run_command_in_terminal(run_cmd)
        # Connection to platform will run here
        # which will stall the platform untill the results
        # are sent from the platform to the framework
        terminate_children_processes(process)

if __name__ == '__main__':

    print(cons.BLUE_TEXT + "Framework init..." + cons.RESET_COLOR)
    print(cons.BLUE_TEXT +
          "Framework init..." +
          cons.RESET_COLOR)

    args = PARSER.parse_args()

    print(cons.BLUE_TEXT +
          "Reading config.dts..." +
          cons.RESET_COLOR)

    dts_path = args.dts_path
    print("config.dts file: " + dts_path)

    if args.dts_path is None:
        print(cons.RED_TEXT +
              "Error: Please provide the --dts_path argument." +
              cons.RESET_COLOR)
    else:
        dts_path = args.dts_path

    parse_dts_file(dts_path)
    print(cons.GREEN_TEXT + "config.dts successfully read!" + cons.RESET_COLOR)

    print(cons.BLUE_TEXT +
          "Creating tests source file..." +
          cons.RESET_COLOR)
    CURR_DIR = os.getcwd()
    print("CURR_DIR: " + CURR_DIR)
    os.chdir("../")
    RUN_CMD = "python3 codegen.py -dir ../src/ "
    RUN_CMD += "-o ./src/testf_weak.c"
    os.system(RUN_CMD)
    os.chdir(CURR_DIR)

    print(cons.BLUE_TEXT + "Running nix build..." + cons.RESET_COLOR)
    BUILD_CMD = 'nix-build ../../' + test_config['nix_file']
    list_suites = test_config['suites'].split()
    list_tests = test_config['tests'].split()
    BUILD_CMD += " --argstr platform " + test_config['platform']
    if len(list_suites):
        BUILD_CMD += " --argstr list_suites \""
        for suit in list_suites:
            BUILD_CMD += suit + " "
        BUILD_CMD = BUILD_CMD[:-1] + "\""
    if len(list_tests):
        BUILD_CMD += " --argstr list_tests \""
        for suit in list_tests:
            BUILD_CMD += suit + " "
        BUILD_CMD = BUILD_CMD[:-1] + "\""

    print(BUILD_CMD)
    res = os.system(BUILD_CMD)
    if res==0:
        print(cons.GREEN_TEXT +
            "nix build successfully completed..." +
            cons.RESET_COLOR)

    else:
        print(cons.RED_TEXT +
               "nix build failed..." +
               cons.RESET_COLOR)
        sys.exit(-1)

    print(cons.BLUE_TEXT + "Launching QEMU..." + cons.RESET_COLOR)
    deploy_test(test_config['platform'])
