SHELL:=bash

# Define directories and include their submakes

root_dir:=$(realpath .)

# Setup toolchain macros and flags

cc:=$(CROSS_COMPILE)gcc
ld:=$(CROSS_COMPILE)ld
objcopy:=$(CROSS_COMPILE)objcopy
objdump:=$(CROSS_COMPILE)objdump

all:
	
clean:

.PHONY: all clean

# Instantiate CI rules

include ci/ci.mk

#TODO: Put instead $(call ci, format, $(c_srcs) $(c_hdrs)) 

$(call ci, format, ./lib/bao_test.c ./lib/bao_weak.c ./lib/bao_test.h)
$(call ci, cppcheck, ./lib/bao_test.c ./lib/bao_weak.c ./lib/bao_test.h)