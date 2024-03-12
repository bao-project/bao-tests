#include "testf.h"
#include "cpu.h"

#define NUM_CPUS    5
size_t cpu_status[NUM_CPUS];

BAO_TEST(CPU_BOOT_CHECK, IS_CPU_UP)
{
    int cpu_id = get_cpuid();
    cpu_status[cpu_id] = 1;

    EXPECTED_NOT_EQUAL(cpu_id, -1);
}

BAO_TEST(CPU_BOOT_CHECK, CPUS_AVAILABLE)
{   
    if(cpu_is_master()){
        size_t num_cpu_up = 0;

        for(int i=0; i<NUM_CPUS; i++) {
            num_cpu_up += cpu_status[i];
        }

        EXPECTED_EQUAL(num_cpu_up, NUM_CPUS);
    }
}
