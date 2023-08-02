"""
Copyright (c) Bao Project and Contributors. All rights reserved

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


PARSER = argparse.ArgumentParser(description="Bao Testing Framework")
PARSER.add_argument("--platform", help="Test target platform.")

if __name__ == '__main__':

    print(cons.BLUE_TEXT + "Framework init..." + cons.RESET_COLOR)

    if os.path.isdir("./__pycache__"):
        shutil.rmtree("./__pycache__")
    if os.path.isdir("./.idea"):
        shutil.rmtree("./.idea")

