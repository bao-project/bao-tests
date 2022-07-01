/*
 * Copyright (c) 2021-2023, Bao Project (www.bao-project.com). All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#ifndef BAO_TEST_H
#define BAO_TEST_H

#ifndef TESTF_LOG_LEVEL
#define TESTF_LOG_LEVEL 2
#endif

#ifndef SUITES
#define SUITES ""
#endif

#ifndef TESTS
#define TESTS ""
#endif

#include "testf_assert.h"
#include <stdio.h>

extern unsigned int testframework_start, testframework_end;

struct bao_test {
    void (*func_ptr)(void);
    const char* suite_name;
    const char* test_name;
};


#define RED()             printf("\033[1;31m")
#define GREEN()           printf("\033[1;32m")
#define YELLOW()          printf("\033[1;33m")
#define COLOR_RESET()     printf("\033[0m")

#define BAO_INFO_TAG() \
    YELLOW();          \
    printf("[INFO] "); \
    COLOR_RESET();

#define BAO_FAIL_TAG()    \
    RED();                \
    printf("[FAILURE] "); \
    COLOR_RESET();

#define BAO_SUCC_TAG()    \
    GREEN();              \
    printf("[SUCCESS] "); \
    COLOR_RESET();

#if (TESTF_LOG_LEVEL > 0)
#define BAO_LOG_FAILURE()                                             \
    do {                                                              \
        BAO_FAIL_TAG();                                               \
        printf("\n    File: %s\n    Line: %u\n", __FILE__, __LINE__); \
    } while (0)
#else
#define BAO_LOG_FAILURE()
#endif

#define BAO_LOG_NOT_SUCCESS()                                                \
    do {                                                                     \
        BAO_FAIL_TAG();                                                      \
        printf("Total:%u Passed:%u Failed:%u\n", testframework_tests,        \
            testframework_tests - testframework_fails, testframework_fails); \
    } while (0)

#define BAO_LOG_SUCCESS()                                                    \
    do {                                                                     \
        BAO_SUCC_TAG();                                                      \
        printf("Total:%u Passed:%u Failed:%u\n", testframework_tests,        \
            testframework_tests - testframework_fails, testframework_fails); \
    } while (0)

#define BAO_LOG_TESTS()                                                     \
    do {                                                                    \
        if (TESTF_LOG_LEVEL > 1) {                                          \
            BAO_INFO_TAG();                                                 \
            printf("Final Report\n");                                       \
            if (testframework_fails)                                        \
                BAO_LOG_NOT_SUCCESS();                                      \
            else                                                            \
                BAO_LOG_SUCCESS();                                          \
        }                                                                   \
        printf("[TESTF-C] TOTAL#%u SUCCESS#%u FAIL#%u\n\n",                 \
            testframework_tests, testframework_tests - testframework_fails, \
            testframework_fails);                                           \
    } while (0)

#define BAO_TEST(suite, test)                                         \
    static void func_bao_test_##suite##_##test(unsigned char*);       \
    static void func_bao_test_TBD_##suite##_##test(void)              \
    {                                                                 \
        extern unsigned int testframework_tests;                      \
        extern unsigned int testframework_fails;                      \
        unsigned char failures = 0;                                   \
        if (TESTF_LOG_LEVEL > 1) {                                    \
            BAO_INFO_TAG();                                           \
            printf("Running " #suite "\t" #test "\n");                \
        }                                                             \
        testframework_tests++;                                        \
        func_bao_test_##suite##_##test(&failures);                    \
        if (failures)                                                 \
            testframework_fails++;                                    \
    }                                                                 \
    struct bao_test struct_bao_test_##suite##_##test __attribute__((  \
        section(".testframework." #suite))) = { .suite_name = #suite, \
        .test_name = #test,                                           \
        .func_ptr = func_bao_test_TBD_##suite##_##test };             \
    static void func_bao_test_##suite##_##test(unsigned char* failures)

static inline void run_all();
static inline int run_specific_test(char* suite, char* test);
static inline int run_suite(char* suite);
void bao_test_entry(void);

#endif // BAO_TEST_H
