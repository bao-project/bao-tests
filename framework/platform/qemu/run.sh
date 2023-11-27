#!/usr/bin/env nix-shell
#!nix-shell --pure -p qemu -i bash

# Check if a version argument is provided
if [ -z "$2" ]; then
    echo "Usage: $0 <qemu-platform> <flash_bin_path> <bao-bin-path>"
    exit 1
fi

qemu_platform="$1"
flash_bin_path="$2"
bao_bin_path="$3"
# -s -S -nographic\
qemu-system-"$qemu_platform" -nographic\
    -M virt,secure=on,virtualization=on,gic-version=3 \
   -cpu cortex-a53 -smp 4 -m 4G\
   -bios $flash_bin_path \
   -device loader,file="$bao_bin_path",addr=0x50000000,force-raw=on\
   -device virtio-net-device,netdev=net0 -netdev user,id=net0,hostfwd=tcp:127.0.0.1:5555-:22\
   -serial pty
