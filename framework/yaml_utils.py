"""
Yaml utils modules to parse config files
"""
import os
import re
import yaml
import constants as cons


class YAMLPatformCfg:
    """
    Parse platform configurations
    """

    def __init__(self, yaml_data):
        self.platforms = yaml_data['platform_cfg']['platform']
        self.cross_compile = yaml_data['bao_cfg']['cross_compile']
        self.toolchain_path = yaml_data['bao_cfg']['toolchain_path']
        self.demo = yaml_data['bao_cfg']['demo']
        self.setup_cfg = yaml_data['bao_test_cfg']['setups']
        self.log_level = yaml_data['bao_test_cfg']['log_level']

    def get_n_platforms(self):
        """
        Return number of platforms to test
        """
        return len(self.platforms)

    def get_n_setups(self):
        """
        Return number of setups to test
        """
        return len(self.setup_cfg)


class YAMLTestCfg:
    """
    Parse tests configurations
    """
    n_mut = 0
    list_mut = []
    list_suits = []
    list_tests = []
    make_cmd = ''
    csrcs = ''

    def __init__(self, yaml_data):
        self.config = yaml_data
        self.n_mut = len(self.config['tests_cfg']['mut'])
        self.list_mut = list(self.config['tests_cfg']['mut'])
        # self.architecture = cons.plat_arch_dict[self.platform]

    def set_mut_tests(self, mut):
        """
        Identify Module Under Test
        """
        self.list_suits = list(self.config['tests_cfg']['mut'][mut]['suites'])

        self.list_tests = []
        for suit in self.config['tests_cfg']['mut'][mut]['suites']:
            self.list_tests.append(self.config['tests_cfg']['mut'][mut]['suites'][suit])

        self.csrcs = '../wrkdir/srcs/' + mut + '/'

    def generate_makes(self):
        """
        Create make commands to prepare the test setup
        """

        self.make_cmd += "SUITES=\""
        # for suit in range(len(self.list_suits)):
        for index, suit in enumerate(self.list_suits, 0):
            self.make_cmd += self.list_suits[index] + " "
        self.make_cmd = self.make_cmd[:-1] + "\" "

        self.make_cmd += "TESTS=\""
        for suit in range(len(self.list_suits)):
            for test in range(len(self.list_tests[suit])):
                self.make_cmd += self.list_tests[suit][test] + " "
        self.make_cmd = self.make_cmd[:-1] + "\" "


def load_config(file_path):
    """
    Load yaml file (containing the test configuration)
    """
    try:
        with open(file_path, encoding="utf-8") as file:
            yaml_data = yaml.safe_load(file)
        print(cons.GREEN_TEXT + "config.yaml loaded successfully!" + cons.RESET_COLOR)
        return yaml_data

    except IOError:
        print(cons.RED_TEXT + "Could not read file:", file_path + cons.RESET_COLOR)
        return None


def select_toolchain(toolchain, cross_compiler_path):
    """
    Select the toolchain to build the test configuration
    """
    tc_version = '0.0.0.0'
    toolchains = []

    cmd = 'ls ' + cross_compiler_path
    tools = os.popen(cmd).read()
    tools = tools.split('\n')
    tools.remove('')

    # check if there is a toolchain
    for file in tools:
        if file.find(toolchain) != -1:
            toolchains.append(file)

    # get the most recent toolchain
    for tchain in toolchains:
        version = re.findall(r'-\s*([\d.]+)', tchain)
        version = version[0] + '.' + version[1]

        new_ver = version.split('.')
        old_ver = tc_version.split('.')

        if new_ver[0] > old_ver[0]:
            tc_version = version
            ret_tc = tchain

        elif int(new_ver[0]) == int(old_ver[0]):
            if int(new_ver[1]) > int(old_ver[1]):
                tc_version = version
                ret_tc = tchain

            elif int(new_ver[1]) == int(old_ver[1]):
                if int(new_ver[2]) > int(old_ver[2]):
                    tc_version = version
                    ret_tc = tchain

                elif int(new_ver[2]) == int(old_ver[2]):
                    if int(new_ver[3]) > int(old_ver[3]):
                        tc_version = version
                        ret_tc = tchain

    return ret_tc
