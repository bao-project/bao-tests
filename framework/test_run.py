import os
import constants as cons

class runner:
    make_list = []
    srcs_path = []
    platform = ''
    architecture = ''
    cross_compiler = ''

    def __init__(self, platform, arch, cross_compile, wrkdir_list, make_cmd_list):
        self.plaform = platform
        self.architecture = arch
        self.cross_compiler = cross_compile
        self.srcs_path = wrkdir_list
        self.make_list = make_cmd_list

    def run(self):

        return 0

    def launch_QEMU(self):
        os.chdir(cons.main_dir)
        os.system("make run")
