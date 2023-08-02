#include "testf_conn.h"

#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#define C_INIT_MSG      "[TESTF-C] init"
#define C_RUN_MSG       "[TESTF-C] run"
#define PY_INIT_MSG     "[TESTF-PY] init"
#define PY_RUN_MSG      "[TESTF-PY] run"

#define CMD_BITS_LENGHT     5
#define CMD_MASK            (1 << CMD_BITS_LENGHT)-1
#define NUM_WARMUPS  (1000)

//Serial Port Variables
volatile char cmd_buffer[CMD_MASK] = {0};


void warmup(int num_warmups)
{
    int it=0;
    while (it < num_warmups)
        it++;
}

void rx_message(char* buffer)
{
    reset_buffer(buffer, CMD_MASK);
    int rx_index = 0;
    char rx_c = uart_getchar();
    
    if(rx_c=='[')
    {
        buffer[rx_index] = rx_c;
        rx_index++;
        while(!(rx_c=='\n' || rx_c=='\r'))
        {
            rx_c = uart_getchar();
            buffer[rx_index] = rx_c;
            rx_index++;
            rx_index &= CMD_MASK;
        }
    }
}

void reset_buffer(char* buffer, int8_t buffer_size)
{
    memset(buffer, 0, buffer_size);
}


void testf_connect_platform(void)
{
    bool is_connected = false;
    bool is_ready = false;
    
    warmup(NUM_WARMUPS);

    while (!is_connected)
    {
        rx_message(cmd_buffer);
        
        if(strstr(cmd_buffer, PY_INIT_MSG) != NULL)
        {
            is_connected = true;
            printf("%s\r\n", C_INIT_MSG);

            while (!is_ready)
            {
                rx_message(cmd_buffer);

                if(strstr(cmd_buffer, PY_RUN_MSG) != NULL)
                {
                    is_ready = true;
                }
            }
        }
    }
}