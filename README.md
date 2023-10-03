## 0. Setup test directory

The provided directory tree below illustrates an example of how to use the
framework:

```c
 MUT
 ├── ci
 ├── src
 ├── tests
 │   ├── configs
 │   │   ├── test_cfg1.dts
 │   │   ├── test_cfg2.dts
 │   ├── src
 │   │   ├── test_src1.c
 │   │   ├── test_src2.c
 │   ├── bao-tests            (git repository)
 │   ├── bao-nix              (git repository)
```

## 1. Get Bao-nix repository
```sh
git clone https://github.com/bao-project/bao-nix.git
```

## 2. Get Bao-tests repository
```sh
git clone https://github.com/bao-project/bao-tests.git
```

## 3. How to configure
Configuration of the test framework is performed through a .dts file. This file allows you to define the test recipe, select the target platform, and specify
the tests to be run in a given setup. The configuration file follows this
template:
```dts
/dts-v1/;
/ {
    platform = "test-target-platform";

    test_config {
        recipe_test {
            nix_file = "test-recipe.nix";
            suites = "list-of-suites";
            tests = "list-of-tests";
            log_level = "verbose-level";
        };
    };
};
```
## 4. How to use

After setting up the directory, run the following commands:
```sh
cd /path-to-MUT-dir/tests/bao-tests/framework/
python3 test_framework.py
```

Alternatively, you can launch the framework with the following arguments:
```sh
python3 test_framework.py \
  -dts_path /path/to/config.dts \                # config.dts file
  -bao_test_src_path /path/to/bao-tests/src \    # bao-tests repo (/src)
  -tests_src_path /path/to/tests/src             # tests to be executed
```
