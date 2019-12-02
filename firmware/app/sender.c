#include <stdio.h>
#include "board.h"
#include "hif.h"
#include "radio.h"


int main(void)
{

#define FRAME_SIZE (49)
char packet[FRAME_SIZE] = "\x41\x88\x3b\x98\xad\xff\xff\x00\x00\x48\x02\xfd\xff\x89\xd9\x0b"  // 16 bytes
                          "\x4d\x28\x64\x55\x00\x00\x90\x0b\x04\xff\xff\x2e\x21\x00\x00\x4a"  // 32 bytes
                          "\xfd\x72\xc4\x10\xdd\xdf\x86\xab\x37\x95\x79\xa8\xa2\xfd\xa8\x0b"  // 48 bytes
                          "\x8c";                                                             // 49 bytes

char *plim;

    mcu_init();

    /* Prerequisite: Init radio */
    LED_INIT();
    radio_init(NULL, 0);
    MCU_IRQ_ENABLE();
    radio_set_param(RP_CHANNEL(15));
    radio_set_state(STATE_TX);

    plim = packet;

    PRINTF("sender:%s\n\r", BOARD_NAME);

    while(1)
    {
        /* finalize the buffer and transmit it */
        radio_set_state(STATE_TX);
        radio_send_frame(FRAME_SIZE, plim, 0);

        PRINT("sending frame...\n\r");
        /* wait after this run */
        LED_TOGGLE(0);
        DELAY_MS(500);
    }
}
