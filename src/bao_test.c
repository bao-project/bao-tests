#include "inc/bao_test.h"
#include <stdio.h>
#include <string.h>

#ifndef SUITES
#define SUITES ""
#endif

#ifndef TESTS
#define TESTS ""
#endif

const int total_chars = 20;
unsigned int testframework_tests;
unsigned int testframework_fails;

void run_all()
{
    struct bao_test* ptr = (struct bao_test*)&testframework_start;
    while (ptr != (struct bao_test*)&testframework_end) {
        (ptr++)->func_ptr();
    }
}

void run_specific_test(char* suite, char* test)
{
    struct bao_test* ptr = (struct bao_test*)&testframework_start;
    while (ptr != (struct bao_test*)&testframework_end) {
        if (!strcmp(ptr->suite_name, suite)) {
            if (!strcmp(ptr->test_name, test)) {
                ptr->func_ptr();
            }
        }
        ptr++;
    }
}

int run_suite(char* suite)
{
    struct bao_test* ptr = (struct bao_test*)&testframework_start;
    while (ptr != (struct bao_test*)&testframework_end) {
        if (strcmp(ptr->suite_name, suite) == 0) {
            ptr->func_ptr();
        }
        ptr++;
    }
}

void bao_test_entry(void)
{
    char suites[] = SUITES;
    char* end = suites + strlen(suites);
    char* ptr = suites;
    char suite[total_chars];

    if (strcmp(suites, "all") == 0) {
        run_all();
        BAO_LOG_TESTS();
        return;
    }

    if (strcmp(TESTS, "all") == 0) {
        run_all();
        BAO_LOG_TESTS();
        return;
    }

    while (ptr <= end) {
        sscanf(ptr, "%19s", suite);
        ptr += strlen(suite) + 1;
        run_suite(suite);
    }

    if (testframework_tests > 0) {
        BAO_LOG_TESTS();
    }
    return;
}
