In order to use Bao Test Framework you have go throught the following steps:

1- add the following lines to your linkerscript

    .testframework : {
        __testframework_start = . ;
        *(.testframework.PRIO* .testframework.prio*)
        *(.testframework.*)
        __testframework_end = . ;        
    }

2- add the following lines to your makefile 
(use the variable TEST_DIR to indicate the directory where all the file containing tests are. Additionally, the variables names C_SRC, INC_DIRS, and CFLAGS may have to be modified according to your makefile.)

    TEST_DIR:=$(SRC_DIR)/tests
    include bao-tests/bao-test.mk
    C_SRC+=$(BAO_TEST_SRCS)
    INC_DIRS+=$(BAO_TEST_INC_DIR)
    CFLAGS += $(BAO_TEST_FLAGS)

3- add to your source the entry point (bao_test_entry()) to our framework, where you feel it is correct.


4- Create a .c file (or multiple) in the directory specified early, include bao_test.h and create tests according to the following example.

    BAO_TEST(SUITE_NAME, TEST_NAME){
        //CODE
        //EG
        EXPECTED_EQ(1,1);
    }
}

5- Build your system normally adding the following variable to your make command:
    BAO_TF=1 -> mandatory to use the framework, otherwise no test will be executed
    SUITES="suite1 suite2" -> to specify which suites need to be executed
    TESTS="test1 test2" -> to specify which tests are to bexecuted