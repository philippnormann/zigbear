#include <stdio.h>
#include "board.h"
#include "hif.h"
#include "radio.h"
#include "timer.h"

#define MAX_BUFFER_SIZE (127)
#define MAX_RECEIVE_BUFFERS (32)
#define WAIT_AFTER_DUMP (MSEC(50))

typedef struct pcap
{
  uint8_t len;
  uint8_t frame[MAX_BUFFER_SIZE];
} pcap;

typedef struct pcap_pool
{
  volatile uint8_t ridx;
  volatile uint8_t widx;
  pcap pcaps[MAX_RECEIVE_BUFFERS];
} pcap_pool;

pcap_pool PcapPool;
uint8_t sending = 0;
time_t last_frame_dump = 0;

void write_bytes(uint8_t *buf, uint8_t len)
{
  uint8_t tmp;
  do
  {
    tmp = hif_put_blk(buf, len);
    buf += tmp;
    len -= tmp;
  } while (len > 0);
}

void wait_for_input(char input)
{
  char inchar;
  do
  {
    inchar = hif_getc();
  } while (inchar != input);
}

void send_packet(uint8_t len, char *frame)
{
  if (sending < 0xFF)
  {
    LED_TOGGLE(0);
    sending += 1;
    radio_set_state(STATE_TXAUTO);
    radio_send_frame(len, frame, 0);
    LED_TOGGLE(0);
  }
}

void init(uint8_t *rxbuf, uint8_t rxbufsz, uint8_t channel)
{
  LED_INIT();
  timer_init();
  hif_init(HIF_DEFAULT_BAUDRATE);
  radio_init(rxbuf, rxbufsz);
  sei();
  radio_set_param(RP_CHANNEL(channel));
  radio_set_state(STATE_RX);

  PcapPool.ridx = 0;
  PcapPool.widx = 0;

  // sync with serial client
  wait_for_input('\n');
  hif_putc('\n');
}

void dump_recieved_frame()
{
  pcap *recieved = &PcapPool.pcaps[PcapPool.ridx];
  uint8_t len = recieved->len;
  uint8_t *frame = recieved->frame;

  // send lenght + frame to client
  hif_putc(len);
  write_bytes(frame, len);

  // mark buffer as processed
  recieved->len = 0;
  PcapPool.ridx = (PcapPool.ridx + 1) % MAX_RECEIVE_BUFFERS;
}

int main(void)
{
  uint8_t channel = 25;
  uint8_t rxbuf[MAX_BUFFER_SIZE];
  time_t now = timer_systime();

  init(rxbuf, MAX_BUFFER_SIZE, channel);

  while (true)
  {
    now = timer_systime();
    if (PcapPool.widx != PcapPool.ridx && now - last_frame_dump > WAIT_AFTER_DUMP)
    {
      dump_recieved_frame();
      last_frame_dump = now;
    } else {
      // TODO: handle commands and send stuff
    }
  }
}

void usr_radio_tx_done(radio_tx_done_t status)
{
  switch (status)
  {
  case TX_OK:
    PRINT("TX_DONE: OK\n\r");
    break;
  case TX_CCA_FAIL:
    PRINT("TX_DONE: CCA_FAIL\n\r");
    break;
  case TX_NO_ACK:
    PRINT("TX_DONE: NO_ACK\n\r");
    ;
    break;
  case TX_FAIL:
    PRINT("TX_DONE: TX_FAIL\n\r");
    break;
  }
  sending -= 1;
}

uint8_t *usr_radio_receive_frame(uint8_t len, uint8_t *frm, uint8_t lqi, int8_t ed, uint8_t crc_fail)
{
  pcap *target_pcap = &PcapPool.pcaps[PcapPool.widx];
  uint8_t new_widx = (PcapPool.widx + 1) % MAX_RECEIVE_BUFFERS;

  if (!crc_fail && len > 0 && len <= MAX_BUFFER_SIZE && target_pcap->len == 0 && new_widx != PcapPool.ridx)
  {
    memcpy(target_pcap->frame, frm, len);
    target_pcap->len = len;
    PcapPool.widx = new_widx;
  }

  return frm;
}
