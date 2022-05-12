ifndef TESTF_TESTS_DIR
TESTF_TESTS_DIR:=$(SRC_DIR)/tests
endif

ifndef TESTF_REPO_DIR
TESTF_REPO_DIR:=$(SRC_DIR)/../../bao-tests
endif

BAO_TEST_DIR:=$(TESTF_REPO_DIR)/src
BAO_TEST_INC_DIR:=$(BAO_TEST_DIR)/inc

ifdef BAO_TEST
BAO_TEST_SRCS += $(BAO_TEST_DIR)/bao_test.c 
BAO_TEST_SRCS += $(wildcard $(TESTF_TESTS_DIR)/*.c)

ifndef SUITES
ifndef TESTS
$(error User must define the variable(s) SUITES and/or TESTS)
endif
endif

ifdef SUITES
BAO_TEST_FLAGS+=-DSUITES='"$(SUITES)"'
endif

ifdef TESTS
BAO_TEST_FLAGS+=-DTESTS='"$(TESTS)"'
endif 

ifdef TESTF_LOG_LEVEL
BAO_TEST_FLAGS+=-DTESTF_LOG_LEVEL=$(TESTF_LOG_LEVEL)
endif

else
BAO_TEST_SRCS := $(BAO_TEST_DIR)/bao_weak.c
endif



#test:
#	call our framework to properly make the binary
#	use case 	> make test SUITES="abcd xpto"
#	instead of 	> make BAO_TEST=1 SUITES="abcd xpto"

#run-test:
#	ideally used to run/flash the binary
