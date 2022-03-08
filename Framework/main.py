import yaml_utils as yutils
from test_run import runner

red_text = '\033[31m'
green_text = '\033[32m'
blue_text = '\033[34m'
reset_color = '\033[0m'

cfg_yaml_path = './config.yaml'
make_list = []

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    print(blue_text + "Framework init..." + reset_color)

    yaml_data = yutils.load_config(cfg_yaml_path)
    if (yaml_data != None):
        test_config = yutils.yaml_cfg(yaml_data)

        print(blue_text + "Generating make commands" + reset_color)
        for mut_idx in range(test_config.n_mut):
            mut = test_config.list_mut[mut_idx]
            test_config.set_mut_tests(mut)
            test_config.generate_makes()
            print(green_text + "Module Under test: ", mut + reset_color)
            print(green_text + "Make cmd: " + reset_color + test_config.make_cmd)
            make_list.append(test_config.make_cmd)

    print(blue_text + "Create runner..." + reset_color)
    test_runner = runner(platform=test_config.platform,
                         arch=test_config.architecture,
                         cross_compile=test_config.cross_compile,
                         wrkdir_list=[],
                         make_cmd_list=make_list)


