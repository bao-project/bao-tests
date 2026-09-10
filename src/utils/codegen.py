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
import re


_C_TOKEN_RE = re.compile(
    r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\r\n]*|/\*.*?(?:\*/|$)',
    re.DOTALL,
)
_BAO_TEST_RE = re.compile(r"BAO_TEST\s*\(([^)]*)\)", re.DOTALL)


def _replace_c_comment(match):
    """Replace comments with whitespace while preserving strings and newlines."""
    token = match.group(0)
    if not token.startswith("/"):
        return token
    return re.sub(r"[^\r\n]", " ", token)


def find_bao_tests(source):
    """Return argument lists for active BAO_TEST markers in C source."""
    source_without_comments = _C_TOKEN_RE.sub(_replace_c_comment, source)
    return [
        [argument.strip().strip('"') for argument in match.group(1).split(",", 3)]
        for match in _BAO_TEST_RE.finditer(source_without_comments)
    ]


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


def _generate_decls_and_calls(tests_list):
    """
    Generate declaration and invocation code for discovered tests.

    Args:
        tests_list (dict): Mapping of suite names to lists of test names.

    Returns:
        tuple(str, str): Generated declarations and generated call blocks.
    """
    decls = ""
    calls = ""
    seen = set()

    for suite, tests in tests_list.items():
        for test in tests:
            func = f"entry_test_{suite}_{test}"
            if func in seen:
                continue
            seen.add(func)

            decls += f"void {func}(void);\n"
            calls += f"\t#if defined({test}) || defined({suite})\n"
            calls += f"\t{func}();\n"
            calls += "\t#endif\n\n"

    return decls.rstrip(), calls.rstrip()


def generate_code(base_dir):
    """
    Scan C sources for BAO_TEST markers and generate test code sections.

    Args:
        base_dir (str): Base directory to search for C source files.

    Returns:
        tuple(str, str): Generated declarations and generated call blocks.
    """
    c_files = get_srcs_list(base_dir)
    tests_list = {}

    for file in c_files:
        with open(file, "r", encoding="utf8") as c_file:
            file_code = c_file.read()

        for test_args in find_bao_tests(file_code):
            if len(test_args) >= 2:
                suite_name, test_name = test_args[:2]
                tests_list.setdefault(suite_name, []).append(test_name)

    return _generate_decls_and_calls(tests_list)


if __name__ == '__main__':
    tool_args = parse_args()
    print("base_dir: ", tool_args.base_dir)
    tests_decls, tests_calls = generate_code(tool_args.base_dir)

    TEMPLATE_FILE = "./template.c"
    if not os.path.isfile(TEMPLATE_FILE):
        print("Template file missing!")
        sys.exit()

    shutil.copy(TEMPLATE_FILE, tool_args.out_code)

    with open(tool_args.out_code, "r", encoding="utf8") as code_file:
        read_code = code_file.readlines()

    decl_begin, decl_end = -1, -1
    call_begin, call_end = -1, -1

    for index, code_line in enumerate(read_code):
        if "// codegen.py declarations begin" in code_line:
            decl_begin = index
        if "// codegen.py declarations end" in code_line:
            decl_end = index
        if "// codegen.py section begin" in code_line:
            call_begin = index
        if "// codegen.py section end" in code_line:
            call_end = index

    OUT_CODE = ""
    OUT_CODE += ''.join(read_code[:decl_begin + 1])
    OUT_CODE += tests_decls + "\n"
    OUT_CODE += ''.join(read_code[decl_end:call_begin + 1])
    OUT_CODE += tests_calls + "\n"
    OUT_CODE += ''.join(read_code[call_end:])

    with open(tool_args.out_code, "w", encoding="utf8") as out_file:
        out_file.write(OUT_CODE)
        print("Successfully generated bao tests code")
