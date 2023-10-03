# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Bao Project and Contributors. All rights reserved

"""
This script is used to generate Bao Project tests code.
It searches for C source files with 'BAO_TEST' markers and creates
corresponding test functions.
"""

import sys
import argparse
import shutil
import os

def parse_args():
    """
    Function to parse command-line arguments for generating tests code.

    Returns:
        args (argparse.Namespace): Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description='Script to parse tests \
                                     sourcesand generate tests code')

    parser.add_argument("-dir", "--base_dir",
                        help="Base directory of the tests directory",
                        default="./")

    parser.add_argument("-o", "--out_code",
                        help="Output file to place the tests code",
                        default="./")

    args = parser.parse_args()
    return args


def get_srcs_list(base_dir):
    """
    Function to retrieve a list of C source files from the specified directory.

    Args:
        base_dir (str): Base directory to search for source files.

    Returns:
        list: List of C source file paths.
    """
    c_srcs = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".c"):
                c_srcs.append(os.path.join(root, file))
    return c_srcs

def generate_code(base_dir):
    """
    Function to generate code based on specified C source files.

    Args:
        base_dir (str): Base directory containing C source files.

    Returns:
        str: Generated code.
    """
    c_files = get_srcs_list(base_dir)
    tests_list = {}
    code = ""
    for file in c_files:
        with open(file, "r", encoding="utf8") as c_file:
            file_code = c_file.readlines()

        for line in file_code:
            if "BAO_TEST" in line:
                clear_line = line.replace(" ", "")
                clear_line = clear_line.replace("BAO_TEST(", "")
                clear_line = clear_line.replace(")", "")
                clear_line = clear_line.replace("\n", "")
                clear_line = clear_line.replace("{", "")
                suite_name = clear_line.split(",")[0]
                test_name = clear_line.split(",")[1]

                if suite_name in tests_list:
                    tests_list[suite_name].append(test_name)

                else:
                    tests_list[suite_name] = [test_name]

    for suite, tests in tests_list.items():
        for test in tests:
            code += f"\t#if defined {test} || {suite}\n"
            code += f"\tentry_test_{suite}_{test}();\n"
            code += "\t#endif\n\n"

    return code[:-2]


if __name__ == '__main__':
    tool_args = parse_args()
    print("base_dir: ", tool_args.base_dir)
    tests_code = generate_code(tool_args.base_dir)

    # Copy template to output directory
    TEMPLATE_FILE = "../src/template.c"
    if not os.path.isfile(TEMPLATE_FILE):
        print("Template file missing!")
        sys.exit()
    shutil.copy(TEMPLATE_FILE, tool_args.out_code)

    # Read template
    with open(tool_args.out_code, "r", encoding="utf8") as code_file:
        read_code = code_file.readlines()

    # Get codegen.py writable sections
    code_sec_begin, code_sec_end = -1, -1
    for index, code_line in enumerate(read_code):
        if "// codegen.py section begin" in code_line:
            code_sec_begin = index

        if "// codegen.py section end" in code_line:
            code_sec_end = index

    # Write generated code to output file
    OUT_CODE = ''.join(read_code[0:code_sec_begin+1])
    OUT_CODE += tests_code
    OUT_CODE += ''.join(read_code[code_sec_end:])
    with open(tool_args.out_code, "w", encoding="utf8") as out_file:
        out_file.writelines(OUT_CODE)
        print("Successfully generated bao tests code")
