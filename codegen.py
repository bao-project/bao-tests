# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Bao Project and Contributors. All rights reserved
import sys
import argparse
import shutil
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

def generate_code(base_dir):
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

    return code[:-2]


if __name__ == '__main__':
    tool_args = parse_args()
    print("base_dir: ", tool_args.base_dir)
    tests_code = generate_code(tool_args.base_dir)

    # Copy template to output directory
    template_file = "./template.c"
    if not os.path.isfile(template_file):
        print("Template file missing!")
        sys.exit()
    shutil.copy(template_file, tool_args.out_code)

    # Read template
    with open(tool_args.out_code, "r") as f:
        code = f.readlines()

    # Get codegen.py writable sections
    code_sec_begin, code_sec_end = -1, -1
    for index, line in enumerate(code):
        if "// codegen.py section begin" in line:
            code_sec_begin = index

        if "// codegen.py section end" in line:
            code_sec_end = index

    # Write generated code to output file
    out_code = ''.join(code[0:code_sec_begin+1])
    out_code += tests_code
    out_code += ''.join(code[code_sec_end:])
    with open(tool_args.out_code, "w") as f:
        f.writelines(out_code)
        print("Successfully generated bao tests code")
