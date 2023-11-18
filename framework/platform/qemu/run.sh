#!/usr/bin/env nix-shell
#!nix-shell --pure -p qemu -i bash

# Check if a version argument is provided
if [ -z "$2" ]; then
    echo "Usage: $0 <qemu-version> <flash_bin_path> <bao-bin-path>"
    exit 1
fi

qemu_version="$1"
flash_bin_path="$2"
bao_bin_path="$3"
# -s -S -nographic\
qemu-system-"$qemu_version" -nographic\
    -M virt,secure=on,virtualization=on,gic-version=3 \
   -cpu cortex-a53 -smp 4 -m 4G\
   -bios $flash_bin_path \
   -device loader,file="$bao_bin_path",addr=0x50000000,force-raw=on\
   -device virtio-net-device,netdev=net0 -netdev user,id=net0,hostfwd=tcp:127.0.0.1:5555-:22\
   -serial pty

# qemu-system-"$qemu_version" -nographic\
#    -M virt,secure=on,virtualization=on,gic-version=3 \
#    -cpu cortex-a53 -smp 4 -m 4G\
#    -bios ./result-2/bin/qemu-"$qemu_version"-virt/flash.bin \
#    -device loader,file="./result-3/bin/bao.bin",addr=0x50000000,force-raw=on\
#    -device virtio-net-device,netdev=net0 -netdev user,id=net0,hostfwd=tcp:127.0.0.1:5555-:22\
#    -device virtio-serial-device -chardev pty,id=serial3 -device virtconsole,chardev=serial3

