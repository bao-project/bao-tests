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
git clone https://github.com/bao-project/bao-nix.git
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
touch local_baremetal_suite.dts
```
And then define the following setup in the `local_baremetal_suite.dts` file:
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
touch local_baremetal_test.dts
```

And then define the following setup in the `local_baremetal_test.dts` file:
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
    platform_cfg = callPackage ./bao-nix/pkgs/platforms/platforms.nix{
      inherit platform;
    };
    arch = platform_cfg.platforms-arch.${platform};

    # Build toolchain
    build_toolchain = callPackage ./bao-nix/pkgs/toolchains/aarch64-none-elf-11-3.nix{};

    # Build Tests Dependencies (will be deprecated)
    demos = callPackage ./bao-nix/pkgs/demos/demos.nix {};
    bao-tests = callPackage ./bao-nix/pkgs/bao-tests/bao-tests.nix {};
    tests = callPackage ./bao-nix/pkgs/tests/tests.nix {};
    baremetal = callPackage ./bao-nix/pkgs/guest/baremetal-bao-tf.nix 
                {
                  toolchain = build_toolchain; 
                  inherit platform_cfg;
                  inherit list_tests; 
                  inherit list_suites;
                  inherit bao-tests;
                  inherit tests;
                };

    # Build Hypervisor
    bao = callPackage ./bao-nix/pkgs/bao/bao_tf.nix 
                { 
                  toolchain = build_toolchain; 
                  guest = baremetal; 
                  inherit demos; 
                  inherit platform_cfg;
                };

    # Build firmware (1/2)
    u-boot = callPackage ./bao-nix/pkgs/u-boot/u-boot.nix 
                { 
                  toolchain = build_toolchain; 
                };

    # Build firmware (2/2)
    atf = callPackage ./bao-nix/pkgs/atf/atf.nix 
                { 
                  toolchain = build_toolchain; 
                  inherit u-boot; 
                  inherit platform;
                };

    inherit pkgs;
  };
in
  packages
``` 

4. Change Guest to Enable Testing

First, we need to define an entry point for the tests. In the
[main.c](examples/bao-baremetal-guest/src/main.c) file of the baremetal, apply
the following changes:
```diff

```

## Local Hypervisor Sources