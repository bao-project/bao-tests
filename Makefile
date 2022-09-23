SHELL:=bash

# Define directories and include their submakes

root_dir:=$(realpath .)
src_dir:=$(root_dir)/src
framework_dir:=$(root_dir)/framework

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

# ifeq ($(PLATFORM),qemu-aarch64-virt) 
	clang-arch:=arm64
# endif

# ifeq ($(PLATFORM),qemu-riscv64-virt) 
# 	clang-arch:=riscv64
# endif

inc_dirs:=$(addsuffix /inc, $(src_dir))

override CPPFLAGS+=$(addprefix -I, $(inc_dirs))

c_srcs+=$(wildcard $(src_dir)/*.c)
c_hdrs+=$(foreach inc_dir, $(inc_dirs), $(wildcard $(inc_dir)/*.h))
$(call ci, cppcheck, $(c_srcs) $(c_hdrs), $(CPPFLAGS))
$(call ci, tidy, $(c_srcs) $(c_hdrs), $(CPPFLAGS))
$(call ci, format, $(c_srcs) $(c_hdrs))

python_srcs+=$(wildcard $(framework_dir)/*.py)
yaml_srcs+=$(wildcard $(framework_dir)/*.yaml)
$(call ci, pylint, $(python_srcs))
$(call ci, yamllint, $(yaml_srcs))

other_srcs+=$(wildcard $(src_dir)/*.mk)
other_srcs+=$(wildcard $(src_dir)/*.ld)
all_files:=$(c_srcs) $(c_hdrs) $(python_srcs) $(yaml_srcs)  $(other_srcs)
$(call ci, license, "Apache-2.0", $(all_files))

ci: cppcheck format-check pylint yamllint license-check tidy
