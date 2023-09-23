# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Bao Project and Contributors. All rights reserved

"""
Test framework main file
"""
import argparse
import constants as cons
from pydevicetree import Devicetree
import os
import sys

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
