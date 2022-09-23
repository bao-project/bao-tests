"""
Copyright (c) Bao Project and Contributors. All rights reserved

SPDX-License-Identifier: Apache-2.0

Module to run tests, which comprises the test setup generation and run
"""
import os
import threading
import subprocess
import psutil
import constants as cons


class Runner:
    """
    Runner class includes the features to prepare and run a test setup
    """
    make_list = []
    srcs_path = []
    platform = ''
    architecture = ''
    cross_compiler = ''

    def __init__(self, platform, arch, cross_compile, make_cmd_list):
        self.platform = platform
        self.architecture = arch
        self.cross_compiler = cross_compile
        self.make_list = make_cmd_list
        self.qemu_pid_list = []

    def run(self):
        """
        Run a specific test
        """
        thread = threading.Thread(target=self.launch_qemu, args=[])
        thread.daemon = True
        thread.start()
        return 0

    def create_run_script(self):
        """
        Generate script to prepare a test setup
        """
        curr_dir = os.getcwd()
        os.chdir(cons.MAIN_DIR)
        script = '#! /bin/bash\n'
        script += 'export CROSS_COMPILE=' + self.cross_compiler + '\n'
        script += 'export PLATFORM=' + self.platform + '\n'
        script += 'export DEMO=baremetal\n'
        script += 'make run' + '\n'

        with open('run.sh', 'w', encoding="utf-8") as rsh:
            rsh.write(script)
            rsh.close()

        os.chdir(curr_dir)

    def launch_qemu(self):
        """
        Launch QEMU with the test setup
        """
        self.create_run_script()
        print("Launching QEMU...")
        # proc = subprocess.Popen('bash run.sh', cwd=cons.MAIN_DIR, shell=True)
        with subprocess.Popen('bash run.sh', cwd=cons.MAIN_DIR, shell=True) as proc:
            try:
                parent = psutil.Process(proc.pid)
                self.qemu_pid_list.append(parent.pid)
            except psutil.NoSuchProcess:
                return
            children = parent.children(recursive=True)

            for process in children:
                self.qemu_pid_list.append(process.pid)

    def build_setup(self, tests_list, log_lvl, csrcs):
        """
        Prepare setup following the config file
        """
        script = '#! /bin/bash\n'
        script += 'export CROSS_COMPILE=' + self.cross_compiler + '\n'
        script += 'export PLATFORM=' + self.platform + '\n'
        script += 'export DEMO=baremetal\n'

        # get absolute path to make file
        cur_dir = os.getcwd()
        os.chdir(csrcs)
        testf_tests_dir = os.popen('pwd').read().replace('\n', '')
        testf_tests_dir = testf_tests_dir + '/src/tests'

        testf_repo_dir = os.popen('pwd').read().replace('\n', '')
        testf_repo_dir = testf_repo_dir + '/src/../../bao-tests'

        os.chdir(cur_dir)


        # make clean
        cmd_clean = "make clean " + "TESTF_TESTS_DIR=" + testf_tests_dir + \
                    ' ' + 'TESTF_REPO_DIR=' + testf_repo_dir

        # make build
        cmd_build = "make BAO_TEST=1 " + "TESTF_TESTS_DIR=" + testf_tests_dir + \
                    ' ' + 'TESTF_REPO_DIR=' + testf_repo_dir + \
                    ' ' + tests_list + "TESTF_LOG_LEVEL=" + str(log_lvl)

        script += cmd_clean + '\n'
        script += cmd_build + '\n'

        cur_dir = os.getcwd()
        os.chdir(csrcs)
        with open('build_setup.sh', 'w', encoding="utf-8") as rsh:
            rsh.write(script)
            rsh.close()


        os.system("bash build_setup.sh")
        os.chdir(cur_dir)
