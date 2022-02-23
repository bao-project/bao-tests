#ifndef BAO_TEST_H
#define BAO_TEST_H

#include "stdio.h"

struct bao_test
{
    const char* suite_name;
    const char* test_name;
    void (*func_ptr)(void);
};

//static int failures, tests;

#define  RED() printf("\033[1;31m")
#define  GREEN()printf("\033[1;32m")
#define  YELLOW()printf("\033[1;33m")
#define  COLOR_RESET()printf("\033[0m")


#define EXPECTED_EQ(x, y) BAO_ASSERT_OP(x, y, ==)
#define EXPECTED_NE(x, y) BAO_ASSERT_OP(x, y, !=)

#define BAO_LOG_FAILURE() do {\
     RED(); \
     printf("[Failure] ");\
     COLOR_RESET(); \
     printf("File:%s Line:%u\n", __FILE__, __LINE__);\
	} while (0) \

#define BAO_LOG_NOT_SUCCESS() do {\
     RED(); \
     printf("[NOT SUCCESS] ");\
     COLOR_RESET(); \
     printf("Total:%d Passed:%d Failed:%d\n", __testframework_tests, __testframework_tests - __testframework_fails, __testframework_fails);\
	} while (0) \

#define BAO_LOG_SUCCESS() do {\
     GREEN(); \
     printf("[SUCCESS] ");\
     COLOR_RESET(); \
     printf("Total:%d Passed:%d Failed:%d\n", __testframework_tests, __testframework_tests - __testframework_fails, __testframework_fails);\
	} while (0) \

#define BAO_LOG_TESTS() do {            \
        YELLOW();                       \
        printf("\n[BAO-TF] Report\n");  \
        COLOR_RESET();                  \
        if(__testframework_fails)       \
            BAO_LOG_NOT_SUCCESS();      \
        else                            \
            BAO_LOG_SUCCESS();          \
	} while (0)                         \


// for now just compare int
#define BAO_ASSERT_OP(x, y, op) do {                        \
		if ( !(x op y)){                                    \
			(*failures)++;                                  \
			BAO_LOG_FAILURE();                              \
		}                                                   \
	} while (0)


/* TODO: Add a verbose define to print */
#define BAO_TEST(suite, test)                               \
    static void func_bao_test_##suite##_##test(unsigned char *);\
    static void func_bao_test_TBD_##suite##_##test(void){   \
        extern unsigned int __testframework_tests;          \
        extern unsigned int __testframework_fails;          \
        unsigned char failures = 0;                         \
        YELLOW();                                           \
        printf("[BAO-TF] Running "#suite"\t"#test"\n");     \
        COLOR_RESET();                                      \
        __testframework_tests++;                            \
        func_bao_test_##suite##_##test(&failures);          \
        if (failures)                                       \
            __testframework_fails++;                        \
    }                                                       \
    struct bao_test struct_bao_test_##suite##_##test        \
    __attribute__((section(".testframework."#suite))) = {   \
        .suite_name = #suite,                               \
        .test_name = #test,                                 \
        .func_ptr = func_bao_test_TBD_##suite##_##test      \
    };                                                      \
    static void func_bao_test_##suite##_##test(unsigned char * failures) 

// test framework Functions
void run_all();
void run_specific_test(char *suite, char *test);
int run_suite(char *suite);
void bao_test_entry(void);


#endif // BAO_TEST_H
