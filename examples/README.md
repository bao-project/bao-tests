# Bao Test Framework Examples

## Available Examples

| Example                                               | Description                                            |
| ----------------------------------------------------- | ------------------------------------------------------ |
| [Local Baremetal Sources](#local-baremetal-sources)   | Use Bao Test Framework to test local guest (baremetal) |
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
git clone --branch demo https://github.com/bao-project/bao-baremetal-guest.git
cd bao-baremetal-guet
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

## Local Hypervisor Sources