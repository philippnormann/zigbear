#include <stdio.h>
#include "board.h"
#include "hif.h"
#include "radio.h"
#include "transceiver.h"
#include "timer.h"

const uint8_t channel = 15;
const uint8_t buffer_size = 255;
# define MAX_RECEIVE_BUFFER_ZSIZE (8)

typedef struct pcap_packet_tag {
  uint8_t len;
  time_stamp_t ts;
  uint8_t frame[MAX_FRAME_SIZE];
} pcap_packet_t;

typedef struct pcap_pool_tag {
  volatile uint8_t ridx;
  volatile uint8_t widx;
  pcap_packet_t packet[MAX_RECEIVE_BUFFER_ZSIZE];
} pcap_pool_t;

pcap_pool_t PcapPool;
uint8_t sending = 0;

int try_read_byte() {
  return hif_getc();
}

char read_byte() {
  int inchar;
  do {
    inchar = try_read_byte();
  } while (inchar == EOF);
  return inchar;
}

void read_bytes(uint8_t len, char * buf) {
  for (uint8_t i = 0; i < len; i++) {
    buf[i] = read_byte();
  }
}

void write_bytes(uint8_t len, char * buf) {
  for (uint8_t i = 0; i < len; i++) {
    PRINTF("%c", buf[i]);
  }
  PRINT("\n\r");
}

void send_packet(uint8_t len, char * frame) {
  if (sending != 0xFF) {
    LED_TOGGLE(0);
    sending += 1;
    radio_set_state(STATE_TX);
    radio_send_frame(len, frame, 0);
    LED_TOGGLE(0);
  }
}

void init() {
  LED_INIT();
  timer_init();
  hif_init(HIF_DEFAULT_BAUDRATE);
  radio_init(NULL, 0);
  sei();
  radio_set_param(RP_CHANNEL(channel));
  radio_set_state(STATE_RX);

  PcapPool.ridx = 0;
  PcapPool.widx = 0;
}

int main(void) {
  int length;
  uint8_t packet_length;
  char input_buffer[buffer_size + 2];
  uint8_t display = 0;

  init();
  read_byte();

  while(1) {
    length = try_read_byte();
    if (length != EOF && length != 0) {
      packet_length = (uint8_t) length;
      read_bytes(packet_length, input_buffer);
      send_packet(packet_length + 2, input_buffer);
    }
    if (sending == 0) {
      radio_set_state(STATE_RX);
    }

    if (PcapPool.widx != PcapPool.ridx) {
      uint8_t tmp, len, *p;
      pcap_packet_t *ppcap = &PcapPool.packet[PcapPool.ridx];
      len = ppcap->len+1;
      hif_putc(len);
      p = (uint8_t*)ppcap;
      do {
        tmp = hif_put_blk(p, len);
        p += tmp;
        len -= tmp;
      } while(len>0);
      /* mark buffer as processed */
      ppcap->len = 0;
      PcapPool.ridx++;
      PcapPool.ridx &= (MAX_RECEIVE_BUFFER_ZSIZE-1);
    }
  }
}

void usr_radio_tx_done(radio_tx_done_t status) {
  switch (status) {
  case TX_OK:
    break;
  case TX_CCA_FAIL:
    PRINT("transmission status: TX_CCA_FAIL\n\r");
    break;
  case TX_NO_ACK:
    PRINT("transmission status: TX_NO_ACK\n\r");;
    break;
  case TX_FAIL:
    PRINT("transmission status: TX_FAIL\n\r");
    break;
  }
  sending -= 1;
}

pcap_packet_t *ppcap_trx24 = NULL;

uint8_t * usr_radio_receive_frame(uint8_t len, uint8_t *frm, uint8_t lqi, int8_t ed, uint8_t crc_fail) {
  extern time_t systime;

  ppcap_trx24 = &PcapPool.packet[PcapPool.widx];

  if (ppcap_trx24->len == 0 && len <= MAX_FRAME_SIZE) {
    ppcap_trx24->ts.hw_ticks = TRX_TSTAMP_REG;
    ppcap_trx24->ts.sys_ticks = systime;
    memcpy(ppcap_trx24->frame, frm, len);
    ppcap_trx24->len = len + sizeof(time_stamp_t);

    PcapPool.widx++;
    PcapPool.widx &= (MAX_RECEIVE_BUFFER_ZSIZE-1);
  }
}
