#include "bao_tf.h"
#include <stdio.h>
#include <string.h>

extern unsigned int __testframework_start, __testframework_end;
unsigned int  __testframework_tests  = 0;
unsigned int  __testframework_fails  = 0;


void run_all(){
    __testframework_tests = 0;
    __testframework_fails = 0;
    struct bao_test *ptr = (struct bao_test *) &__testframework_start;  
    for(; ptr < &__testframework_end; ptr++){
        ptr->func_ptr();
    }
    BAO_LOG_TESTS();    
}

void run_specific_test(char *suite, char *test){
    struct bao_test *ptr = (struct bao_test *) &__testframework_start;  
    for(; ptr < &__testframework_end; ptr++){
        if(!strcmp(ptr->suite_name, suite))
            if(!strcmp(ptr->test_name, test))
                ptr->func_ptr();
    }
    BAO_LOG_TESTS();   
}

void run_suite(char *suite){
    struct bao_test *ptr = (struct bao_test *) &__testframework_start;  
    //printf("__testframework_tests: %d, __testframework_fails: %d\n", __testframework_tests, __testframework_fails);
    __testframework_tests = 0;
    __testframework_fails = 0;
    
    for(; ptr < &__testframework_end; ptr++){
        if(strcmp(ptr->suite_name, suite) == 0)
                ptr->func_ptr();
    }
        
    BAO_LOG_TESTS();   
}


