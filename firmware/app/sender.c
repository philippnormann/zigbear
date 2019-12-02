#include <stdio.h>
#include "board.h"
#include "hif.h"
#include "radio.h"

const uint8_t channel = 15;
const uint8_t buffer_size = 255;

char read_byte() {
  char inchar;
  do {
    inchar = hif_getc();
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
  LED_TOGGLE(0);
  radio_set_state(STATE_TX);
  radio_send_frame(len, frame, 0);
  LED_TOGGLE(0);
}

void init() {
  LED_INIT();
  hif_init(HIF_DEFAULT_BAUDRATE);
  radio_init(NULL, 0);
  sei();
  radio_set_param(RP_CHANNEL(channel));
  radio_set_state(STATE_TX);
}

int main(void) {
  uint8_t packet_length;
  char input_buffer[buffer_size];

  init();
  read_byte();

  while (1) {
    PRINT("enter packet length\n\r");
    packet_length = (uint8_t) read_byte();
    if (packet_length > buffer_size) {
      PRINTF("error: packet length %d > max length %d\n\r", packet_length, buffer_size);
    } else {
      PRINTF("reading %d bytes\n\r", packet_length);
      read_bytes(packet_length, input_buffer);
      PRINTF("transmitting\n\r", input_buffer);
      PRINT("frame: ");
      write_bytes(packet_length, input_buffer);
      send_packet(packet_length, input_buffer);
      DELAY_MS(100);
    }
  }
}

void usr_radio_tx_done(radio_tx_done_t status) {
  switch (status) {
  case TX_OK:
    PRINT("transmission status: TX_OK\n\r");
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
}