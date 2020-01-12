#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "board.h"
#include "hif.h"
#include "radio.h"
#include "timer.h"

/*  ----------  Constants  ----------  */

#define MAX_FRAME_LENGTH (127)
#define MAX_RECEIVE_BUFFERS (32)
#define MAX_DIGITS_LENGTH (3)
#define WAIT_AFTER_DUMP (MSEC(50))
#define DEFAULT_CHANNEL (25)

/*  ----------  Types  ----------  */

typedef struct pcap
{
  uint8_t len;
  uint8_t ed;
  uint8_t frame[MAX_FRAME_LENGTH];
} pcap;

typedef struct pcap_pool
{
  volatile uint8_t ridx;
  volatile uint8_t widx;
  pcap pcaps[MAX_RECEIVE_BUFFERS];
} pcap_pool;

pcap_pool PcapPool;

/*  ----------  Globals  ----------  */

uint8_t sending = 0;
time_t last_frame_dump = 0;

/*  ----------  IO Helpers  ----------  */

void wait_until(char delim)
{
  char inchar;
  do
  {
    inchar = hif_getc();
  } while (inchar != delim);
}

uint8_t read_until(char delim, uint8_t *buf, uint8_t maxlen)
{
  int inchar;
  uint8_t idx = 0;
  do
  {
    inchar = hif_getc();
    if (inchar == delim)
    {
      return idx;
    }
    if (inchar != EOF)
    {
      buf[idx] = inchar;
      idx++;
    }
  } while (idx < maxlen);
  return idx;
}

void hex_dump(uint8_t *buf, uint8_t len)
{
  int i;
  for (i = 0; i < len; i++)
  {
    PRINTF("%02X", buf[i]);
  }
  PRINT("\n\r");
}

/*  ----------  Transmitting  ----------  */

void transmit_frame(char *frame, uint8_t len)
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

void handle_frame_transmission()
{
  uint8_t n;
  uint8_t length = 0;
  uint8_t bytes_read = 0;
  uint8_t digitbuf[MAX_DIGITS_LENGTH + 1];
  uint8_t hexbuf[MAX_FRAME_LENGTH * 2];
  uint8_t txbuf[MAX_FRAME_LENGTH + 2];

  wait_until(':'); // skip first delimiter (:) after cmd
  bytes_read = read_until(':', digitbuf, MAX_DIGITS_LENGTH);
  digitbuf[MAX_DIGITS_LENGTH] = '\0';
  
  length = strtol(digitbuf, NULL, 10);
  if (length > 0 && length < MAX_FRAME_LENGTH - 2)
  {
    bytes_read = read_until('\n', hexbuf, length * 2);
    if (bytes_read == length * 2)
    {
      // all checks passed, decode hex and send frame
      for (int i = 0; i < length; i++)
      {
        sscanf(hexbuf + 2 * i, "%2X", &n);
        txbuf[i] = (char)n;
      }
      transmit_frame(txbuf, length + 2);
    }
    else
    {
      // report error to client
      PRINT("T:LEN_MISMATCH\n\r");
    }
  }
  else
  {
    // report error to client
    PRINT("T:LEN_FAIL\n\r");
  }
}

void usr_radio_tx_done(radio_tx_done_t status)
{
  switch (status)
  {
  case TX_OK:
    PRINT("T:OK\n\r");
    break;
  case TX_CCA_FAIL:
    PRINT("T:CCA_FAIL\n\r");
    break;
  case TX_NO_ACK:
    PRINT("T:NO_ACK\n\r");
    ;
    break;
  case TX_FAIL:
    PRINT("T:FAIL\n\r");
    break;
  }
  sending -= 1;
}

/*  ------  Channel Switching  ------  */

void handle_channel_switch()
{
  uint8_t channel = 0;
  uint8_t bytes_read = 0;
  uint8_t digitbuf[MAX_DIGITS_LENGTH + 1];

  wait_until(':'); // skip first delimiter (:) after cmd
  bytes_read = read_until('\n', digitbuf, MAX_DIGITS_LENGTH);
  digitbuf[MAX_DIGITS_LENGTH] = '\0';

  channel = strtol(digitbuf, NULL, 10);
  if (channel >= 11 && channel <= 26)
  {
    // set channel and confirm to client
    radio_set_param(RP_CHANNEL(channel));
    PRINTF("S:%d:OK\n\r", channel);
  }
  else
  {
    // report error to client
    PRINTF("S:%d:FAIL\n\r", channel);
  }
}

/*  ----------  Recieving  ----------  */

uint8_t *usr_radio_receive_frame(uint8_t len, uint8_t *frm, uint8_t lqi, int8_t ed, uint8_t crc_fail)
{
  LED_TOGGLE(1);
  pcap *target_pcap = &PcapPool.pcaps[PcapPool.widx];
  uint8_t new_widx = (PcapPool.widx + 1) % MAX_RECEIVE_BUFFERS;

  if (!crc_fail && len > 0 && len <= MAX_FRAME_LENGTH && target_pcap->len == 0 && new_widx != PcapPool.ridx)
  {
    memcpy(target_pcap->frame, frm, len);
    target_pcap->len = len;
    target_pcap->ed = ed;
    PcapPool.widx = new_widx;
  }
  LED_TOGGLE(1);
  return frm;
}

void dump_recieved_frame()
{
  pcap *recieved = &PcapPool.pcaps[PcapPool.ridx];
  uint8_t len = recieved->len;
  uint8_t ed = recieved->ed;
  uint8_t *frame = recieved->frame;

  PRINTF("R:%d:%d:", len, ed);
  hex_dump(frame, len);
  PRINT("\n\r");

  // mark buffer as processed
  recieved->len = 0;
  PcapPool.ridx = (PcapPool.ridx + 1) % MAX_RECEIVE_BUFFERS;
}

/*  ----------  Initialization  ----------  */

void init(uint8_t *rxbuf, uint8_t rxbufsz)
{
  LED_INIT();
  timer_init();
  hif_init(HIF_DEFAULT_BAUDRATE);
  radio_init(rxbuf, rxbufsz);
  radio_set_state(STATE_RX);
  radio_set_param(RP_CHANNEL(DEFAULT_CHANNEL));
  sei();

  PcapPool.ridx = 0;
  PcapPool.widx = 0;

  // sync with client
  wait_until('\n');
  hif_putc('\n');
}

/*  ----------  Main Loop  ----------  */

int main(void)
{
  int cmd = EOF;
  uint8_t rxbuf[MAX_FRAME_LENGTH];

  time_t now = timer_systime();

  init(rxbuf, MAX_FRAME_LENGTH);

  while (true)
  {
    now = timer_systime();

    if (PcapPool.widx != PcapPool.ridx && now - last_frame_dump > WAIT_AFTER_DUMP && sending == 0)
    {
      dump_recieved_frame();
      last_frame_dump = now;
    }
    else
    {
      cmd = hif_getc();
      switch ((char)cmd)
      {
      case 'T':
        handle_frame_transmission();
        break;
      case 'S':
        handle_channel_switch();
        break;
      }
    }

    if (sending == 0)
    {
      radio_set_state(STATE_RX);
    }
  }
}
