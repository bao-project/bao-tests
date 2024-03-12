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
#include <spinlock.h>

extern spinlock_t print_lock;

extern unsigned int testframework_start, testframework_end;

#define RED()         printf("\033[1;31m")
#define GREEN()       printf("\033[1;32m")
#define YELLOW()      printf("\033[1;33m")
#define COLOR_RESET() printf("\033[0m")

#define INFO_TAG()                  \
    YELLOW();                       \
    printf("[INFO] ");              \
    COLOR_RESET();

#define FAIL_TAG()                  \
    RED();                          \
    printf("[FAILURE] ");           \
    COLOR_RESET();

#define SUCC_TAG()                  \
    GREEN();                        \
    printf("[SUCCESS] ");           \
    COLOR_RESET();

#define START_TAG()                 \
    spin_lock(&print_lock);         \
    printf("[TESTF-C] START\n");    \
    spin_unlock(&print_lock);

#define END_TAG()                   \
    spin_lock(&print_lock);         \
    printf("[TESTF-C] END\n");      \
    spin_unlock(&print_lock);

#if (TESTF_LOG_LEVEL > 0)
#define LOG_FAILURE()                                                 \
    do {                                                              \
        spin_lock(&print_lock);                                       \
        FAIL_TAG();                                                   \
        printf("\n    File: %s\n    Line: %u\n", __FILE__, __LINE__); \
        spin_unlock(&print_lock);                                     \
    } while (0)
#else
#define LOG_FAILURE()
#endif

#define LOG_NOT_SUCCESS()                                                    \
    do {                                                                     \
        FAIL_TAG();                                                          \
        printf("Total:%u Passed:%u Failed:%u\n", testframework_tests,        \
            testframework_tests - testframework_fails, testframework_fails); \
    } while (0)

#define LOG_SUCCESS()                                                        \
    do {                                                                     \
        SUCC_TAG();                                                          \
        printf("Total:%u Passed:%u Failed:%u\n", testframework_tests,        \
            testframework_tests - testframework_fails, testframework_fails); \
    } while (0)

#define LOG_TESTS()                                                              \
    do {                                                                         \
        if (TESTF_LOG_LEVEL > 1) {                                               \
            spin_lock(&print_lock);                                              \
            printf("\n");                                                        \
            INFO_TAG();                                                          \
            printf("Final Report\n");                                            \
            if (testframework_fails)                                             \
                LOG_NOT_SUCCESS();                                               \
            else                                                                 \
                LOG_SUCCESS();                                                   \
            spin_unlock(&print_lock);                                            \
        }                                                                        \
        spin_lock(&print_lock);                                                  \
        printf("[TESTF-C] TOTAL#%u SUCCESS#%u FAIL#%u\n\n", testframework_tests, \
            testframework_tests - testframework_fails, testframework_fails);     \
        spin_unlock(&print_lock);                                                \
    } while (0)

#define BAO_TEST(suite, test)                            \
    void test_##suite##_##test(unsigned char*);          \
    void entry_test_##suite##_##test(void)               \
    {                                                    \
        extern unsigned int testframework_tests;         \
        extern unsigned int testframework_fails;         \
        unsigned char failures = 0;                      \
        if (TESTF_LOG_LEVEL > 1) {                       \
            spin_lock(&print_lock);                      \
            printf("\n");                                \
            INFO_TAG();                                  \
            printf("Running " #suite "\t" #test "\n");   \
            spin_unlock(&print_lock);                    \
        }                                                \
        testframework_tests++;                           \
        test_##suite##_##test(&failures);                \
        if (failures) {                                  \
            testframework_fails++;                       \
            if (TESTF_LOG_LEVEL > 1) {                   \
                spin_lock(&print_lock);                  \
                FAIL_TAG();                              \
                printf(#suite "\t" #test " failed! \n"); \
                spin_unlock(&print_lock);                \
            }                                            \
        } else {                                         \
            if (TESTF_LOG_LEVEL > 1) {                   \
                spin_lock(&print_lock);                  \
                SUCC_TAG();                              \
                printf(#suite "\t" #test " passed! \n"); \
                spin_unlock(&print_lock);                \
            }                                            \
        }                                                \
    }                                                    \
    void test_##suite##_##test(unsigned char* failures)

void testf_entry(void);

#endif // TESTF_H
