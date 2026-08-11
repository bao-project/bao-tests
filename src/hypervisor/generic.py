"""
Copyright (c) Bao Project and Contributors. All rights reserved
SPDX-License-Identifier: Apache-2.0
Generic hypervisor support classes.
"""

from __future__ import annotations

import importlib
import os
import sys

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CUR_DIR, "../"))

if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

print_log = getattr(importlib.import_module("constants"), "print_log")

class GenericHypervisor:  # pylint: disable=too-few-public-methods
    """Base hypervisor helper with source management and build helpers."""

    def __init__(self, wrkdir, srcs_path=""):
        """
        Initialize generic hypervisor paths and source metadata.

        Args:
            wrkdir (str): Framework working directory.
            srcs_path (str): Optional path to pre-existing hypervisor sources.
        """
        self.wrkdir = wrkdir
        self.srcs_path = srcs_path
    def fetch_sources(self, hypervisor_srcs):
        """Fetch or select hypervisor sources in subclasses."""


class StandaloneGenericHypervisor:
    """Hypervisor shim for standalone guest binaries."""

    def __init__(self, wrkdir):
        self.srcs_path = wrkdir

    def fetch_sources(self, _hypervisor_srcs):  # pylint: disable=no-self-use
        """No sources to fetch for standalone mode."""

    @staticmethod
    def build(  # pylint: disable=too-many-arguments,unused-argument
        wrkdir_imgs,
        config_repo,
        config_name,
        platform,
        env,
    ):
        """Return the expected standalone output artifact names."""
        bin_name = "guest1.bin"
        elf_name = "guest1.elf"
        out_img = os.path.join(wrkdir_imgs, bin_name)
        return out_img, bin_name, elf_name

generic_hypervisor = GenericHypervisor  # pylint: disable=invalid-name
standalone = StandaloneGenericHypervisor  # pylint: disable=invalid-name
