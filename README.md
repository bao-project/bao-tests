# Bao Kao - Bao Hypervisor Testing Framework

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![CI](https://github.com/bao-project/bao-kao/actions/workflows/base-ci.yml/badge.svg)](https://github.com/bao-project/bao-kao/actions/workflows/base-ci.yml)

**Bao Kao** (`kao`) is the automated testing framework for the [Bao hypervisor](https://github.com/bao-project/bao-hypervisor). It handles the full lifecycle of a test run: toolchain setup, guest compilation, hypervisor and firmware builds, platform launch, and result collection on both emulated and real hardware targets.

---

## Table of Contents

- [Bao Kao - Bao Hypervisor Testing Framework](#bao-kao---bao-hypervisor-testing-framework)
  - [Table of Contents](#table-of-contents)
  - [Requirements](#requirements)
  - [Motivation](#motivation)
  - [What is Bao Kao?](#what-is-bao-kao)
  - [Quick Start](#quick-start)
  - [Supported Platforms](#supported-platforms)
    - [Toolchains](#toolchains)
  - [Architecture Overview](#architecture-overview)
    - [End-to-End Flow](#end-to-end-flow)
  - [Usage](#usage)
    - [Running Tests](#running-tests)
    - [Hypervisor Modes](#hypervisor-modes)
    - [Useful Flags](#useful-flags)
  - [Configuration](#configuration)
    - [YAML VM Configuration](#yaml-vm-configuration)
    - [Test Discovery](#test-discovery)
  - [Directory Structure](#directory-structure)
  - [CI](#ci)
  - [Contributing](#contributing)
  - [License](#license)

## Requirements

- Python 3.8+
- `make`
- `git`

Install Python dependencies with:

```bash
pip install Jinja2==3.1.6 prettytable==3.17.0 pyserial==3.5 PyYAML==6.0.3
```

Firmware and emulator builds may require additional host dependencies. For example, building U-Boot with `CONFIG_TOOLS_MKEFICAPSULE` requires the GnuTLS development headers (`libgnutls28-dev` on Ubuntu and Debian). Physical platforms also require access to the target hardware and their platform-specific launch tools.

## Motivation

Testing a hypervisor across multiple architectures and boards requires coordinating cross-compilers, firmware build systems, emulators, and serial monitors. Doing this manually is error-prone and does not scale across a platform matrix.

Bao Kao automates the full flow. A single command downloads the toolchain, builds the guest, assembles the hypervisor image, boots the platform, and collects results, whether the target is QEMU on a developer machine or a physical board in a lab.

---

## What is Bao Kao?

Bao Kao is a Python-based framework that:

- **Discovers** tests from source annotations.
- **Builds** cross-compiled guest binaries, the Bao hypervisor, and required firmware in the correct order.
- **Launches** the system image on the selected platform (emulator or real board).
- **Monitors** serial output and parses structured test result markers.
- **Reports** pass/fail results per test with configurable verbosity.

It works both interactively during development and as an automated step in CI pipelines.

---

## Quick Start

**Requirements:** Python 3.8+, `make`, `git`.

```bash
# Clone the repository and its submodules (framework lives under tests/kao)
git clone --recurse-submodules https://github.com/bao-project/bao-hypervisor.git
cd bao-hypervisor/tests/kao

# Install Python dependencies
pip install Jinja2==3.1.6 prettytable==3.17.0 pyserial==3.5 PyYAML==6.0.3

# Run all tests on QEMU AArch64
python3 src/kao.py -p qemu-aarch64-virt -t \
    --hyp-srcs ../.. --wrkdir ../wrkdir

# Skip toolchain download if already in PATH
python3 src/kao.py -p qemu-aarch64-virt -t \
    --hyp-srcs ../.. --wrkdir ../wrkdir --no-toolchain-build
```

> The first run downloads the cross-compiler and QEMU if not already present. Subsequent runs reuse cached artifacts under `tests/wrkdir/`.

If the repository was cloned without its submodules, initialize Bao Kao from the
Bao hypervisor root with:

```bash
git submodule update --init --recursive tests/kao
```

---

## Supported Platforms

| Platform | CLI Name | Architecture | Type | Firmware / Launcher |
|---|---|---|---|---|
| QEMU AArch64 virt | `qemu-aarch64-virt` | AArch64 | Emulator | ATF + U-Boot |
| QEMU RISC-V 64 virt | `qemu-riscv64-virt` | RISC-V 64 | Emulator | OpenSBI |
| Arm FVP-R | `fvp-r` | AArch64 | Emulator | None (direct boot) |
| Arm FVP-A | `fvp-a` | AArch64 | Emulator | ATF + U-Boot |
| Xilinx ZCU104 | `zcu104` | AArch64 | Real board | U-Boot (HTTP boot) |
| NXP S32Z270 | `s32z270` | AArch32 | Real board | Lauterbach Trace32 |
| Renesas RH850 | `rh850` | V850 | Real board | Backend incomplete |
| Infineon TriCore TC4Dx | `tc4dx` | TriCore | Real board | Lauterbach Trace32 |

### Toolchains

Each platform requires a specific cross-compiler. The framework normally downloads and installs it automatically on the first run.

| Toolchain | Prefix | Managed Version |
|---|---|---|
| Arm GNU AArch64 | `aarch64-none-elf-` | 14.2.rel1 |
| Arm GNU ARM32 | `arm-none-eabi-` | 14.2.rel1 |
| RISC-V | `riscv64-unknown-elf-` | gc891d8dc23e |
| V850 | `v850-elf-` | v14.2.0 |
| TriCore | `tricore-elf-` | 09-2025 |

Pass `--no-toolchain-build` to skip the download and use a toolchain already in `PATH`. The configured TriCore download URL currently returns HTTP 404, so TC4Dx requires a separately installed toolchain and this option until the URL is updated.

---

## Architecture Overview

```
kao.py
  │
  ├── inputs.py          CLI parsing and validation
  ├── constants.py       Shared constants (baud rate, timeouts, log helpers)
  ├── logger.py          Serial monitor and test result parser
  │
  ├── platforms/         One module per target platform
  │   ├── generic_platform.py   Base platform and emulator classes
  │   └── <platform>.py         Platform-specific build and launch logic
  │
  ├── toolchains/        Toolchain download and setup helpers
  ├── firmware/          ATF / U-Boot / OpenSBI build helpers + config fragments
  │
  ├── hypervisor/
  │   ├── generic.py             Generic and standalone hypervisor classes
  │   └── bao/
  │       ├── bao.py             Bao build integration
  │       ├── config_renderer.py YAML-to-C config renderer (Jinja2)
  │       └── templates/         C config Jinja2 templates
  │
  ├── guests/
  │   └── baremetal.py   Baremetal guest clone, codegen, and build
  │
  └── utils/
      ├── process.py         Subprocess helpers
      ├── codegen.py         Test entry point code generator
      └── toolchain_helpers.py  Toolchain base classes
```

### End-to-End Flow

```
Invoke kao.py
     │
     ├─ Discover tests from source annotations
     ├─ Load and validate platform module
     ├─ Setup platform (install QEMU / FVP model if needed)
     ├─ Build toolchain (download cross-compiler if needed)
     │
     ├─ For each test:
     │    ├─ Build guest binary (baremetal-test repo + codegen)
     │    ├─ Render Bao config from YAML (config_renderer)
     │    ├─ Build Bao hypervisor with embedded guest
     │    ├─ Build firmware (ATF / U-Boot / OpenSBI)
     │    ├─ Launch platform (QEMU / FVP / board)
     │    └─ Monitor serial → parse results → report
     │
     └─ Print final summary
```

---

## Usage

### Running Tests

Run the framework from `bao-hypervisor/tests/kao`:

```bash
# Run all tests
python3 src/kao.py -p <platform> -t \
    --hyp-srcs ../.. --wrkdir ../wrkdir

# Run specific test IDs
python3 src/kao.py -p <platform> -t 100,101,200 \
    --hyp-srcs ../.. --wrkdir ../wrkdir

# Exclude specific IDs from a full run
python3 src/kao.py -p <platform> -t --test-exclude 101 \
    --hyp-srcs ../.. --wrkdir ../wrkdir

# Run with maximum verbosity
python3 src/kao.py -p <platform> -t -l 2 \
    --hyp-srcs ../.. --wrkdir ../wrkdir
```

Test IDs are assigned at discovery time. `--generate-id-readme` currently prints tables mapping every ID to its suite, name, and description, then exits. The current implementation does not write the optional path to a file.

### Hypervisor Modes

| Flag | Mode | Effect |
|---|---|---|
| `-H bao` (default) | Bao | Builds and boots the Bao hypervisor wrapping the guest |
| `-H none` | Standalone | Guest runs bare-metal with no hypervisor layer |

`standalone` is accepted as a deprecated alias for `none`. In Bao mode, use `--hyp-srcs <path>` to point the framework at the local Bao source tree.

### Useful Flags

| Flag | Description |
|---|---|
| `-p <name>` | Target platform (required) |
| `-t [IDs]` | Run tests - all, or comma-separated IDs |
| `--test-exclude IDs` | Exclude test IDs from a full `-t` run |
| `-b [IDs]` | Run benchmarks - all, or comma-separated IDs |
| `--benchmark-exclude IDs` | Exclude benchmark IDs from a full benchmark run |
| `-l <0\|1\|2>` | Log level: `0` final only, `1` failures, `2` all |
| `-e <full\|tf\|none>` | Output filter: all output, framework only, silent |
| `-H <bao\|none>` | Hypervisor mode |
| `--hyp-srcs <path>` | Use a local Bao source tree |
| `--wrkdir <path>` | Set the generated-artifact working directory |
| `--no-toolchain-build` | Skip toolchain download; expect it in `PATH` |
| `--no-firmware-build` | Skip firmware rebuild |
| `--plat-virt-args <args>` | Platform-specific arguments (e.g., `GICV3`) |
| `--generate-id-readme [path]` | Print the workload ID reference tables |

Test and benchmark selection arguments cannot be combined.

---

## Configuration

### YAML VM Configuration

Tests are configured via YAML files placed under:

```
tests/tests/configs/<setup>/<platform>.yaml
```

Each file describes the VMs that Bao will manage for that setup:

```yaml
vms:
  - vm1:
      name: baremetal            # Guest type
      build_options:
        cpu_num: 4               # Number of vCPUs to build for
        generic_flags: ""        # Extra flags passed to the guest build
      config:                    # Bao hypervisor VM configuration
        image:
          base_addr: 0x50000000
        entry: 0x50000000
        platform:
          cpu_num: 4
          regions:
            - base: 0x50000000
              size: 0x04000000
          devs:
            - pa:   0x08000000
              va:   0x08000000
              size: 0x00010000
              interrupts: [25, 26, 27]
        arch:
          gic:
            gicd_addr: 0x08000000
            gicr_addr: 0x080a0000
```

`config_renderer` translates this YAML into a C configuration file using Jinja2 templates, which is then compiled into the Bao hypervisor image.

### Test Discovery

Tests are written in C using the `BAO_TEST` macro:

```c
BAO_TEST(suite_name, test_name, setup_name, "Human-readable description")
{
    /* test body */
}
```

The framework scans `tests/tests/src/*.c`, extracts all `BAO_TEST` declarations, and assigns each a numeric ID. Source files are sorted and numbered from 1, while tests within each file are numbered from 0:

```
ID = source_file_number × 100 + test_number
```

For example, the first test in `boot.c` gets ID `100`, the second gets `101`, and the first test in `irq.c` gets `200`.

---

## Directory Structure

```
├── kao/                            Bao Kao submodule
│   ├── Makefile                    CI orchestration
│   ├── README.md                   This file
│   ├── ci/                         CI rule definitions and checker scripts
│   └── src/
│       ├── kao.py                  Main entry point
│       ├── constants.py            Shared constants and log helpers
│       ├── inputs.py               CLI argument parser and validator
│       ├── logger.py               Serial monitor and result parser
│       ├── platforms/              One module per supported platform
│       │   ├── generic_platform.py Base classes
│       │   ├── qemu_aarch64_virt.py
│       │   ├── qemu_riscv64_virt.py
│       │   ├── fvp_r.py
│       │   ├── fvp_a.py
│       │   ├── zcu104.py
│       │   ├── s32z270.py
│       │   ├── rh850.py
│       │   └── tc4dx.py
│       ├── toolchains/             Toolchain download and setup helpers
│       ├── firmware/               ATF, U-Boot, OpenSBI build helpers
│       │   ├── configs/            U-Boot config fragments per platform
│       │   └── patches/            Platform-specific patches
│       ├── hypervisor/
│       │   ├── generic.py          Base hypervisor classes
│       │   └── bao/
│       │       ├── bao.py          Bao build integration
│       │       ├── config_renderer.py YAML-to-C config renderer
│       │       └── templates/      Jinja2 C config templates
│       ├── guests/
│       │   └── baremetal.py        Baremetal guest build helpers
│       └── utils/
│           ├── codegen.py          Test entry point generator
│           ├── process.py          Subprocess wrapper
│           └── toolchain_helpers.py Toolchain base classes
└── tests/                          Test integration data
    ├── configs/                    Per-platform YAML configurations
    └── src/                        C test sources and headers
```

Artifacts produced during a run are placed under `tests/wrkdir/` (created at runtime, excluded from version control):

```
tests/wrkdir/
├── .kao-wrkdir        Bao Kao ownership marker
├── toolchains/         Downloaded cross-compilers
├── platforms/
│   ├── firmware/       Built ATF, U-Boot, OpenSBI images
│   └── qemu*/          QEMU sources (if built from source)
├── guests/
│   ├── baremetal/      Guest source tree
│   └── build/          Compiled guest binaries (.bin, .elf)
└── configs/            Generated Bao C configuration files
```

Bao is built from the source directory passed with `--hyp-srcs`; its sources are not copied into `tests/wrkdir/`. Bao Kao refuses to use an existing working directory that does not contain `.kao-wrkdir`.

---

## CI

Run the full CI check suite locally with:

```bash
make ci
```

This runs:

- **pylint** - Python style and static analysis across all `src/` modules.
- **license-check** - Verifies every source file carries an `SPDX-License-Identifier: Apache-2.0` header.

The same checks run on every pull request via GitHub Actions (`.github/workflows/base-ci.yml`), together with a separate `gitlint` job.

---

## Contributing

Contributions are welcome. Before submitting a pull request:

1. Ensure `make ci` passes cleanly.
2. Add or update the relevant YAML configs and C source files for any new test.
3. For new platform support, add a module under `src/platforms/` implementing the `GenericPlatform` interface (see `generic_platform.py`).
4. Sign off every commit with `git commit -s` to certify the [Developer Certificate of Origin](https://developercertificate.org/).

---

## License

Bao Kao is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

Copyright (c) Bao Project and Contributors. All rights reserved.