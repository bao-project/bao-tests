# Bao Test Framework Examples

## Available Examples

| Example                                               | Description                                            |
| ----------------------------------------------------- | ------------------------------------------------------ |
| [Remote Hypervisor Sources](#local-baremetal-sources)   | Use Bao Test Framework to test local guest (baremetal) |
| [Local Hypervisor Sources](#local-hypervisor-sources) | Use Bao Test Framework to test local hypervisor        |


## Local Baremetal Sources
### 0. Setup the working directory
Start by setting the working directory with the following structure:
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
For this example, we will consider the Module Under Test (MUT) a baremetal guest. Start by cloning a
baremetal guest example:
```sh
git clone --branch demo https://github.com/bao-project/bao-hypervisor.git
cd bao-hypervisor
export ROOT_DIR=$(realpath .)
```

Then, let's set de working directory by:
1. Creating the tests directory:
```sh
mkdir -p $ROOT_DIR/tests/configs
mkdir -p $ROOT_DIR/tests/src
```
This repository corresponds to the place where test configs (in the format of `.dts` files) should
be placesd (`tests/configs`) and also the tests' sources (`tests/src`).

2. Cloning the Bao tests repository:
```sh
git clone https://github.com/bao-project/bao-tests
```
3. Cloning the Bao nix repository:
```sh
git clone --branch update/guests-recipes https://github.com/bao-project/bao-nix.git
```

### 1. Manage Tests
1. Create Test Sources
Let's start by creating a test source file:
```sh
cd $ROOT_DIR/tests/src
touch hello_world_test.c
```

And then define the following tests in the `hello_world_test.c` file:
```c
#include "testf.h"

BAO_TEST(HELLO, TEST_A)
{
    printf("Hello World!!!\n");
}

BAO_TEST(HELLO, TEST_B)
{
    printf(" Bao Test Framework is up!!!\n");
}
```

2. Create Test Config
Create a configuration file:
```sh
cd $ROOT_DIR/tests/configs
touch config_suite.dts
```
And then define the following setup in the `config_suite.dts` file:
```dts
/dts-v1/;
/ {
    platform = "qemu-aarch64-virt";
    log_echo = <1>;

    test_config {
        recipe_test {
            nix_file = "default.nix";
            suites = "HELLO";
            tests = "";
            log_level = "0";
        };
    };
};
```

In this configuration file, both tests will run since that we are selecting the Suite. To run just a
specific test, let's create a second config file:
```sh
cd $ROOT_DIR/tests/configs
touch config_test.dts
```

And then define the following setup in the `config_test.dts` file:
```dts
/dts-v1/;
/ {
    platform = "qemu-aarch64-virt";
    log_echo = <1>;

    test_config {
        recipe_test {
            nix_file = "default.nix";
            suites = "";
            tests = "TEST_A";
            log_level = "0";
        };
    };
};
```

3. Create the test recipe
For building the setup, we will leverage recipes from the Bao nix repoistory. Nonetheless, we need
to define a recipe that describes the testing setup. Let's start by creating the recipe file:
```sh
cd $ROOT_DIR
touch default.nix
```

This recipe should contain the following inputs:
1. **platform** - allows to select the platform to deploy the tests
2. **list_tests** - allow to select the list of tests to be deployed
3. **list_suites** - allow to select the list of suites (list of tests) to be deployed

And it will build the following packages:
1. **platform_cfg** - contains the platform details (architecture and toolchain)
2. **build_toolchain** - contains the compiled toolchain for the selected platform
3. **demos dependencies** - contains demos and bao-tests dependencies (will be deprecated)
4. **bao** - builds the Bao hypervisor
5. **u-boot** and **atf** - builds the firmware to deploy the tests


```nix
{
  pkgs ? import (fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/refs/tags/22.11.tar.gz";
    sha256 = "sha256:11w3wn2yjhaa5pv20gbfbirvjq6i3m7pqrq2msf0g7cv44vijwgw";
  }) {},
  platform ? " ",
  list_tests ? " ",
  list_suites ? " "
}:

with pkgs;

let
  packages = rec {

    # Get Platform details
    plat_cfg  = callPackage ./bao-nix/pkgs/platforms/platforms.nix{
      inherit platform;
    };
    arch = plat_cfg .platforms-arch.${platform};

    # Build toolchain
    aarch64-none-elf = callPackage ./bao-nix/pkgs/toolchains/aarch64-none-elf-11-3.nix{};

    # Build Tests Dependencies (will be deprecated)
    demos = callPackage ./bao-nix/pkgs/demos/demos.nix {};
    bao-tests = callPackage ./bao-nix/pkgs/bao-tests/bao-tests.nix {};
    tests = callPackage ./bao-nix/pkgs/tests/tests.nix {};
    baremetal = callPackage ./bao-nix/pkgs/guest/baremetal-remote-tf.nix
                { 
                  toolchain = aarch64-none-elf;
                  guest_name = "baremetal";
                  platform_cfg = plat_cfg;
                  inherit list_tests; 
                  inherit list_suites;
                  bao-tests = ./bao-tests;
                  tests_srcs = ./tests;
                  testf_patch = ./baremetal.patch;
                };


    # Build Hypervisor
    bao = callPackage ./bao-nix/pkgs/bao/bao.nix 
                { 
                  toolchain = aarch64-none-elf; 
                  guest = baremetal; 
                  inherit demos; 
                  platform_cfg = plat_cfg;
                };

    # Build firmware (1/2)
    u-boot = callPackage ./bao-nix/pkgs/u-boot/u-boot.nix 
                { 
                  toolchain = aarch64-none-elf; 
                };

    # Build firmware (2/2)
    atf = callPackage ./bao-nix/pkgs/atf/atf.nix 
                { 
                  toolchain = aarch64-none-elf; 
                  inherit u-boot; 
                  inherit platform;
                };

    inherit pkgs;
  };
in
  packages
``` 

4. Change Guest to Enable Testing

:information_source: Please refrain from replicating the subsequent steps in
this demo. To streamline the process, the baremetal build recipe already
integrates a patch containing the necessary modifications. To implement this,
simply copy the [patch](/examples/patches/baremetal.patch) placed at
`/examples/patches/baremetal.patch` to the `$ROOT_DIR` using the command:
`cp patches/baremetal.patch $ROOT_DIR/baremetal.patch`.

First, we need to define an entry point for the tests. In the `main.c` file of
the baremetal, apply the following changes:
```diff
void main(void){
         printf("Bao bare-metal test guest\n");
         spin_unlock(&print_lock);
 
+        testf_entry();

         irq_set_handler(UART_IRQ_ID, uart_rx_handler);
         irq_set_handler(TIMER_IRQ_ID, timer_handler);
         irq_set_handler(IPI_IRQ_ID, ipi_handler);
```

Then, the `Makefile` needs to be updated to include the build of the tests
sources:
```diff
 src_dirs+=$(src_dir) $(core_dir) $(platform_dir)
 SRC_DIRS+=$(src_dirs)
 INC_DIRS+=$(addsuffix /inc, $(src_dirs))
 
+# Test framework setup
+include $(TESTF_REPO_DIR)/src/bao-test.mk
+SRC_DIRS+=$(TESTF_SRC_DIR) $(TESTF_TESTS_DIR)
+C_SRC+=$(TESTF_SRCS)
+INC_DIRS+=$(TESTF_INC_DIR)
+CFLAGS+=$(TESTF_FLAGS)
+# End of test framework setup

 ifeq ($(wildcard $(platform_dir)),)
 $(error unsupported platform $(PLATFORM))
 endif
```

### 2. Run Test Framework
Let's start by running the tests running the entire suite of tests:
```sh
cd $ROOT_DIR/bao-tests/framework
python3 test_framework.py\
  -dts_path $ROOT_DIR/tests/configs/config_suite.dts\
  -bao_test_src_path $ROOT_DIR/bao-tests/src\
  -tests_src_path $ROOT_DIR/tests/src
```
Which should produce the following output:
```sh
[INFO] Running HELLO    TEST_A
[INFO] Running HELLO    TEST_B
[INFO] Final Report
[TESTF-C] TOTAL#2 SUCCESS#2 FAIL#0
```

Then, let's run the configuration that selects only one test, rather than the
suite of tests:
```sh
cd $ROOT_DIR/bao-tests/framework
python3 test_framework.py\
  -dts_path $ROOT_DIR/tests/configs/config_test.dts\
  -bao_test_src_path $ROOT_DIR/bao-tests/src\
  -tests_src_path $ROOT_DIR/tests/src
```
Now, the output should be the following:
```sh
[INFO] Running HELLO    TEST_A
[INFO] Final Report
[TESTF-C] TOTAL#1 SUCCESS#1 FAIL#0
```
## Local Hypervisor Sources