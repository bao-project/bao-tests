CUR_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
BAO_TEST_DIR:=$(CUR_DIR)
BAO_TEST_INC_DIR:=$(BAO_TEST_DIR)inc

#$(info    CUR_DIR is $(CUR_DIR))
#$(info    BAO_TEST_DIR is $(BAO_TEST_DIR))
#$(info    BAO_TEST_INC_DIR is $(BAO_TEST_INC_DIR))


ifdef BAO_TEST
BAO_TEST_SRCS += $(BAO_TEST_DIR)bao_test.c 
BAO_TEST_SRCS += $(wildcard $(TEST_DIR)/*.c)
$(info    TEST_DIR is $(TEST_DIR))
$(info    BAO_TEST_SRCS is $(BAO_TEST_SRCS))
ifdef SUITES
BAO_TEST_FLAGS+=-DSUITES='"$(SUITES)"'
endif

ifdef TESTS
BAO_TEST_FLAGS+=-DTESTS='"$(TESTS)"'
endif 

else
BAO_TEST_SRCS := $(BAO_TEST_DIR)bao_weak.c
endif



#test:
#	call our framework to properly make the binary
#	use case 	> make test SUITES="abcd xpto"
#	instead of 	> make BAO_TEST=1 SUITES="abcd xpto"

#run-test:
#	ideally used to run/flash the binary