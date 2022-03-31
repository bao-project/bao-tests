SHELL:=bash

# Define directories and include their submakes

root_dir:=$(realpath .)
src_dir:=$(root_dir)/src
framework_dir:=$(root_dir)/framework

# Round-up source and include directories

inc_dirs:=$(addsuffix /inc, $(src_dir))
c_srcs+=$(wildcard $(src_dir)/*.c)
c_hdrs+=$(foreach inc_dir, $(inc_dirs), $(wildcard $(inc_dir)/*.h))
python_srcs+=$(wildcard $(framework_dir)/*.py)
yaml_srcs+=$(wildcard $(framework_dir)/*.yaml)
$(info $(c_hdrs))
$(info $(c_srcs))
$(info $(python_srcs))
$(info $(yaml_srcs))

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

$(call ci, cppcheck, $(c_srcs) $(c_hdrs))
$(call ci, format, $(c_srcs) $(c_hdrs))
$(call ci, tidy, $(c_srcs) $(c_hdrs))
$(call ci, pylint, $(python_srcs))
$(call ci, yamllint, $(yaml_srcs))