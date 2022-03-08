
# Text coloring
red_text = '\033[31m'
green_text = '\033[32m'
blue_text = '\033[34m'
reset_color = '\033[0m'

# Platform/architecture dictionary
plat_arch_dict = {
    "zcu102" : "aarch64",               # Xilinx ZCU102
    "zcu104" : "aarch64",               # Xilinx ZCU104
    "imx8qm" : "aarch64",               # NXP i.MX8QM
    "tx2" : "aarch64",                  # Nvidia TX2
    "rpi4" : "aarch64",		            # Raspberry 4 Model B
    "qemu-aarch64-virt" : "aarch64",	# QEMU Aarch64 virt
    "qemu-riscv64-virt" : "riscv"	    # QEMU RV64 virt
}

# Directories
main_dir = './bao-demos/'
