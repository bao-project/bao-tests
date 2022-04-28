#include <bao_test.h>
#include <stdio.h>
#include <string.h>

unsigned int __testframework_tests;
unsigned int __testframework_fails;

#ifndef SUITES
#define SUITES ""
#endif

#ifndef TESTS
#define TESTS ""
#endif

void run_all()
{
    struct bao_test* ptr = (struct bao_test*)&__testframework_start;
    for (; ptr < (struct bao_test*)&__testframework_end; ptr++) {
        ptr->func_ptr();
    }
}

void run_specific_test(char* suite, char* test)
{
    struct bao_test* ptr = (struct bao_test*)&__testframework_start;
    for (; ptr < (struct bao_test*)&__testframework_end; ptr++) {
        if (!strcmp(ptr->suite_name, suite))
            if (!strcmp(ptr->test_name, test))
                ptr->func_ptr();
    }
}

int run_suite(char* suite)
{
    struct bao_test* ptr = (struct bao_test*)&__testframework_start;
    for (; ptr < (struct bao_test*)&__testframework_end; ptr++) {
        if (strcmp(ptr->suite_name, suite) == 0) {
            ptr->func_ptr();
        }
    }
}

void bao_test_entry(void)
{
    char suites[] = SUITES;
    char* end = suites + strlen(suites);
    char* ptr = suites;
    char suite[20];

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

    if (__testframework_tests > 0)
        BAO_LOG_TESTS();
    return;
}
