/*
 * Copyright (c) Bao Project and Contributors. All rights reserved
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#ifndef TESTF_H
#define TESTF_H

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

#define RED()         printf("\033[1;31m")
#define GREEN()       printf("\033[1;32m")
#define YELLOW()      printf("\033[1;33m")
#define COLOR_RESET() printf("\033[0m")

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

#define BAO_TEST(suite, test)                          \
    void bao_test_##suite##_##test(unsigned char*);    \
    void entry_test_##suite##_##test(void)             \
    {                                                  \
        extern unsigned int testframework_tests;       \
        extern unsigned int testframework_fails;       \
        unsigned char failures = 0;                    \
        if (TESTF_LOG_LEVEL > 1) {                     \
            BAO_INFO_TAG();                            \
            printf("Running " #suite "\t" #test "\n"); \
        }                                              \
        testframework_tests++;                         \
        bao_test_##suite##_##test(&failures);          \
        if (failures)                                  \
            testframework_fails++;                     \
    }                                                  \
    void bao_test_##suite##_##test(unsigned char* failures)

void testf_entry(void);

#endif // TESTF_H
