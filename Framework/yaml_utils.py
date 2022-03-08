import yaml
import constants as cons


class yaml_cfg:
    n_mut = 0
    platform = 'none'
    architecture = 'none'
    cross_compile = 'none'
    config = 'none'
    list_mut = []
    list_suits = []
    list_tests = []
    make_cmd = ''

    def __init__(self, yaml_data):
        self.config = yaml_data
        self.n_mut = len(self.config['tests_cfg']['mut'])
        self.list_mut = list(self.config['tests_cfg']['mut'])
        self.platform = self.config['platform_cfg']['platform']
        self.architecture = cons.plat_arch_dict[self.platform]
        self.cross_compile = self.config['bao_cfg']['cross_compile']


    def set_mut_tests(self, MUT):
        self.list_suits = list(self.config['tests_cfg']['mut'][MUT]['suites'])

        self.list_tests = []
        for suit in self.config['tests_cfg']['mut'][MUT]['suites']:
            self.list_tests.append(self.config['tests_cfg']['mut'][MUT]['suites'][suit]['tests'])

    def generate_makes(self):
        # enable bao test
        self.make_cmd = "make BAO_TEST=1 "

        self.make_cmd += "suites=\""
        for suit in range(len(self.list_suits)):
            self.make_cmd += self.list_suits[suit] + " "
        self.make_cmd = self.make_cmd[:-1] + "\" "

        self.make_cmd += "TESTS=\""
        for suit in range(len(self.list_suits)):
            for test in range(len(self.list_tests)):
                self.make_cmd += self.list_tests[suit][test] + " "
        self.make_cmd = self.make_cmd[:-1] + "\" "


def load_config(file_path):
    try:
        with open(file_path) as file:
            yaml_data = yaml.safe_load(file)
        print(cons.green_text + "config.yaml loaded successfully!" + cons.reset_color)
        return yaml_data

    except IOError:
        print(cons.red_text + "Could not read file:", file_path + cons.reset_color)
        return None

    return


