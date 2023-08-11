# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Bao Project and Contributors. All rights reserved

import numpy as np
import argparse
import glob
import os

"""
This script is used to generate Bao Project tests code.
It searches for C source files with 'BAO_TEST' markers and creates
corresponding test functions.
"""

def parse_args():
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
    c_srcs = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".c"):
                c_srcs.append(os.path.join(root, file))
    return c_srcs


def code_header():
    code = "/*" + "\n"
    code += "* Copyright (c) Bao Project and Contributors. "
    code += "All rights reserved" + "\n"
    code += "*" + "\n"
    code += "* SPDX-License-Identifier: Apache-2.0" + "\n"
    code += "*/" + "\n"
    return code


def code_includes():
    code = "#include \"testf.h\"" + "\n"
    code += "#include <stdio.h>" + "\n"
    code += "#include <string.h>" + "\n"
    return code


def code_variables():
    code = "unsigned int testframework_tests;" + "\n"
    code += "unsigned int testframework_fails;" + "\n"
    return code


def generate_defines(base_dir):
    c_files = get_srcs_list(base_dir)
    tests_list = {}
    code = ""
    for file in c_files:
        with open(file, "r") as f:
            file_code = f.readlines()

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

    for suite in tests_list.keys():
        for test in tests_list[suite]:
            code += "\t#if defined " + test + " || " + suite + "\n"
            code += "\tentry_test_" + suite + "_" + test + "();" + "\n"
            code += "\t#endif" + "\n" + "\n"

    return code


def code_functions(base_dir):
    code = "void testf_entry(void)" + "\n"
    code += "{" + "\n"

    code += generate_defines(base_dir)

    code += "\tif (testframework_tests > 0) {" + "\n"
    code += "\t\tBAO_LOG_TESTS();" + "\n"
    code += "\t} else {" + "\n"
    code += "\t\tBAO_INFO_TAG();" + "\n"
    code += "\t\tprintf(\"No tests were executed!\\n\");" + "\n"
    code += "\t}" + "\n"
    code += "\treturn;" + "\n"
    code += "}" + "\n"
    return code


def generate_code(base_dir):
    code = ""
    code += code_header() + "\n"
    code += code_includes() + "\n"
    code += code_variables() + "\n"
    code += code_functions(base_dir) + "\n"
    return code


if __name__ == '__main__':
    tool_args = parse_args()
    print("base_dir: ", tool_args.base_dir)
    code = generate_code(tool_args.base_dir)

    with open(tool_args.out_code, "w") as f:
        f.write(code)

    print("Successfully generated bao tests code")
