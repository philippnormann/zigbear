#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


#include "app_timer.h"
#include "boards.h"
#include "sdk_config.h"

#include "nrf_802154_const.h"
#include "nrf_802154.h"
#include "nrf_cli.h"
#include "nrf_cli_cdc_acm.h"
#include "nrf_cli_types.h"
#include "nrf_delay.h"
#include "nrf_log.h"

#include "app_usbd.h"
#include "app_usbd_cdc_acm.h"
#include "app_usbd_core.h"
#include "app_usbd_serial_num.h"
#include "app_usbd_string_desc.h"
#include "nrf_cli_cdc_acm.h"
#include "nrf_drv_usbd.h"


#define FCF_CHECK_OFFSET           (PHR_SIZE + FCF_SIZE)
#define PANID_CHECK_OFFSET         (DEST_ADDR_OFFSET)
#define SHORT_ADDR_CHECK_OFFSET    (DEST_ADDR_OFFSET + SHORT_ADDRESS_SIZE)
#define EXTENDED_ADDR_CHECK_OFFSET (DEST_ADDR_OFFSET + EXTENDED_ADDRESS_SIZE)
#define NRF_802154_FRAME_PARSER_INVALID_OFFSET 0xff

static bool frame_type_and_version_filter(uint8_t frame_type, uint8_t frame_version)
{
    bool result;

    switch (frame_type)
    {
        case FRAME_TYPE_BEACON:
        case FRAME_TYPE_DATA:
        case FRAME_TYPE_ACK:
        case FRAME_TYPE_COMMAND:
            result = (frame_version != FRAME_VERSION_3);
            break;

        case FRAME_TYPE_MULTIPURPOSE:
            result = (frame_version == FRAME_VERSION_0);
            break;

        case FRAME_TYPE_FRAGMENT:
        case FRAME_TYPE_EXTENDED:
            result = true;
            break;

        default:
            result = false;
    }

    return result;
}

static bool dst_addressing_may_be_present(uint8_t frame_type)
{
    bool result;

    switch (frame_type)
    {
        case FRAME_TYPE_BEACON:
        case FRAME_TYPE_DATA:
        case FRAME_TYPE_ACK:
        case FRAME_TYPE_COMMAND:
        case FRAME_TYPE_MULTIPURPOSE:
            result = true;
            break;

        case FRAME_TYPE_FRAGMENT:
        case FRAME_TYPE_EXTENDED:
            result = false;
            break;

        default:
            result = false;
    }

    return result;
}

static nrf_802154_rx_error_t dst_addressing_end_offset_get(const uint8_t * p_psdu,
                                                           uint8_t       * p_num_bytes,
                                                           uint8_t         frame_type,
                                                           uint8_t         frame_version)
{
    nrf_802154_rx_error_t result = NRF_802154_RX_ERROR_NONE;

    switch (frame_version)
    {
        case FRAME_VERSION_0:
        case FRAME_VERSION_1:
            //result = dst_addressing_end_offset_get_2006(p_psdu, p_num_bytes, frame_type);
            break;

        case FRAME_VERSION_2:
            //result = dst_addressing_end_offset_get_2015(p_psdu, p_num_bytes, frame_type);
            break;

        default:
            result = NRF_802154_RX_ERROR_INVALID_FRAME;
    }

    return result;
}

nrf_802154_rx_error_t nrf_802154_filter_frame_part(const uint8_t * p_psdu, uint8_t * p_num_bytes) {
  nrf_802154_rx_error_t result        = NRF_802154_RX_ERROR_INVALID_FRAME;
    uint8_t               frame_type    = p_psdu[FRAME_TYPE_OFFSET] & FRAME_TYPE_MASK;
    uint8_t               frame_version = p_psdu[FRAME_VERSION_OFFSET] & FRAME_VERSION_MASK;

    switch (*p_num_bytes)
    {
        case FCF_CHECK_OFFSET:
            if (p_psdu[0] < IMM_ACK_LENGTH || p_psdu[0] > MAX_PACKET_SIZE)
            {
                result = NRF_802154_RX_ERROR_INVALID_LENGTH;
                break;
            }

            if (!frame_type_and_version_filter(frame_type, frame_version))
            {
                result = NRF_802154_RX_ERROR_INVALID_FRAME;
                break;
            }

            if (!dst_addressing_may_be_present(frame_type))
            {
                result = NRF_802154_RX_ERROR_NONE;
                break;
            }

            result = dst_addressing_end_offset_get(p_psdu, p_num_bytes, frame_type, frame_version);
            break;

        default:
            result = NRF_802154_RX_ERROR_NONE;
            break;
    }
    return result;
}


static void buffer_add(nrf_fprintf_ctx_t * const p_ctx, char c)
{
#if NRF_MODULE_ENABLED(NRF_FPRINTF_FLAG_AUTOMATIC_CR_ON_LF)
    if (c == '\n')
    {
        buffer_add(p_ctx, '\r');
    }
#endif
    p_ctx->p_io_buffer[p_ctx->io_buffer_cnt++] = c;

    if (p_ctx->io_buffer_cnt >= p_ctx->io_buffer_size)
    {
        nrf_fprintf_buffer_flush(p_ctx);
    }
}

int sscan_uint8(const char *p_bp, uint8_t *p_u8) {
  uint16_t u16;

  if (!sscanf(p_bp, "%hd", &u16)) {
    return 0;
  }

  *p_u8 = (uint8_t)u16;

  return 1;
}

uint8_t hexToByte(char c) {
  switch (c) {
  case '0':
    return 0;
  case '1':
    return 1;
  case '2':
    return 2;
  case '3':
    return 3;
  case '4':
    return 4;
  case '5':
    return 5;
  case '6':
    return 6;
  case '7':
    return 7;
  case '8':
    return 8;
  case '9':
    return 9;
  case 'A':
  case 'a':
    return 10;
  case 'B':
  case 'b':
    return 11;
  case 'C':
  case 'c':
    return 12;
  case 'D':
  case 'd':
    return 13;
  case 'E':
  case 'e':
    return 14;
  case 'F':
  case 'f':
    return 15;
  }
  return 0;
}

char byteToHex(uint8_t i) {
  switch (i) {
  case 0:
    return '0';
  case 1:
    return '1';
  case 2:
    return '2';
  case 3:
    return '3';
  case 4:
    return '4';
  case 5:
    return '5';
  case 6:
    return '6';
  case 7:
    return '7';
  case 8:
    return '8';
  case 9:
    return '9';
  case 10:
    return 'a';
  case 11:
    return 'b';
  case 12:
    return 'c';
  case 13:
    return 'd';
  case 14:
    return 'e';
  case 15:
    return 'f';
  }
  return '\0';
}

void hexToBytes(char *c, uint8_t *res) {
  for (uint8_t i = 0; c[i] != '\0'; i++) {
    if (i % 2 == 0) {
      res[i / 2] = hexToByte(c[i]) << 4;
    } else {
      res[i / 2] = res[i / 2] + hexToByte(c[i]);
    }
  }
}

void bytesToHex(uint8_t *b, uint8_t length, char *res) {
  for (uint16_t i = 0; i < length; i++) {
    res[i * 2] = byteToHex((b[i] >> 4) & 15);
    res[i * 2 + 1] = byteToHex(b[i] & 15);
  }
  res[(length * 2)] = '\0';
}

void app_error_fault_handler(uint32_t id, uint32_t pc, uint32_t info) {
  //NRF_LOG_ERROR("received a fault! id: 0x%08x, pc: 0x&08x\r\n", id, pc);
  NVIC_SystemReset();
}

/**
 * @brief Enable power USB detection
 *
 * Configure if example supports USB port connection
 */
#ifndef USBD_POWER_DETECTION
#define USBD_POWER_DETECTION true
#endif

static void usbd_user_ev_handler(app_usbd_event_type_t event) {
  switch (event) {
  case APP_USBD_EVT_STOPPED:
    app_usbd_disable();
    break;
  case APP_USBD_EVT_POWER_DETECTED:
    if (!nrf_drv_usbd_is_enabled()) {
      app_usbd_enable();
    }
    break;
  case APP_USBD_EVT_POWER_REMOVED:
    app_usbd_stop();
    break;
  case APP_USBD_EVT_POWER_READY:
    app_usbd_start();
    break;
  default:
    break;
  }
}

static void usbd_init(void) {
  ret_code_t ret;
  static const app_usbd_config_t usbd_config = {
      .ev_handler = app_usbd_event_execute,
      .ev_state_proc = usbd_user_ev_handler};

  app_usbd_serial_num_generate();

  ret = app_usbd_init(&usbd_config);
  APP_ERROR_CHECK(ret);

  app_usbd_class_inst_t const *class_cdc_acm =
      app_usbd_cdc_acm_class_inst_get(&nrf_cli_cdc_acm);
  ret = app_usbd_class_append(class_cdc_acm);
  APP_ERROR_CHECK(ret);

  if (USBD_POWER_DETECTION) {
    ret = app_usbd_power_events_enable();
    APP_ERROR_CHECK(ret);
  } else {
    //NRF_LOG_INST_INFO(m_log.p_log, "No USB power detection enabled\r\nStarting USB now");

    app_usbd_enable();
    app_usbd_start();
  }

  /* Give some time for the host to enumerate and connect to the USB CDC port */
  nrf_delay_ms(1000);
}

#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#include "nrf_802154.h"

#define MAX_MESSAGE_SIZE 255
#define CHANNEL 15

#define CLI_EXAMPLE_LOG_QUEUE_SIZE (4)
NRF_CLI_CDC_ACM_DEF(m_cli_cdc_acm_transport);
NRF_CLI_DEF(m_cli_cdc_acm,
    "",
    &m_cli_cdc_acm_transport.transport,
    '\r',
    CLI_EXAMPLE_LOG_QUEUE_SIZE);

static volatile uint8_t message[MAX_MESSAGE_SIZE];

uint8_t extended_address[] = {0x01, 0x23, 0x45, 0x67, 0x89, 0xab, 0xcd, 0xef};
uint8_t short_address[] = {0x05, 0x06};
uint8_t pan_id[] = {0x03, 0x04};

int main(int argc, char *argv[]) {
  ret_code_t ret;
  (void)argc;
  (void)argv;

  ret = nrf_drv_clock_init();
  APP_ERROR_CHECK(ret);
  nrf_drv_clock_lfclk_request(NULL);

  ret = nrf_cli_init(&m_cli_cdc_acm, NULL, true, true, NRF_LOG_SEVERITY_ERROR);
  APP_ERROR_CHECK(ret);

  usbd_init();

  ret = nrf_cli_start(&m_cli_cdc_acm);
  APP_ERROR_CHECK(ret);

  nrf_802154_init();

  nrf_802154_short_address_set(short_address);
  nrf_802154_extended_address_set(extended_address);
  nrf_802154_pan_id_set(pan_id);

  nrf_802154_channel_set(CHANNEL);

  nrf_802154_receive();

  while (1) {
    nrf_cli_process(&m_cli_cdc_acm);
  }

  return 0;
}

void nrf_802154_transmitted_raw(const uint8_t *p_frame,
    uint8_t *p_ack,
    int8_t power,
    uint8_t lqi) {
  (void)p_frame;
  (void)power;
  (void)lqi;

  //m_tx_done = true;

  if (p_ack != NULL) {
    nrf_cli_print(&m_cli_cdc_acm, "Sended %u", &p_ack);
    nrf_cli_print(&m_cli_cdc_acm, "Frame %u", &p_frame);
    nrf_802154_buffer_free_raw(p_ack);
  }
}

void nrf_802154_received_raw(uint8_t *p_data, int8_t power, uint8_t lqi) {
  if (p_data[0] <= MAX_MESSAGE_SIZE) {
    char m[MAX_MESSAGE_SIZE * 2 + 2];
    uint16_t length = p_data[0]-2;
    bytesToHex(p_data+1, length, m);
    m[length*2] = '\n';
    m[length*2+1] = '\0';

    nrf_cli_fprintf(&m_cli_cdc_acm, NRF_CLI_DEFAULT, "received: power: %d lqi: %u data: ", power, lqi);

    for(uint8_t i = 0; i < strlen(m); i++) {
      buffer_add((&m_cli_cdc_acm)->p_fprintf_ctx, m[i]);
    }
    nrf_fprintf_buffer_flush((&m_cli_cdc_acm)->p_fprintf_ctx);
  }

  nrf_802154_buffer_free_raw(p_data);

  return;
}

void nrf_802154_receive_failed(nrf_802154_rx_error_t error) {
  if (error != NRF_802154_RX_ERROR_NONE) {
      nrf_cli_print(&m_cli_cdc_acm, "Receive error %u", error);
  };
}

void nrf_802154_tx_started(const uint8_t *p_frame) {
    //nrf_cli_print(&m_cli_cdc_acm, "tx started %u", *p_frame);
}

void nrf_cli_cmd_send(nrf_cli_t const *p_cli, size_t argc, char **argv) {
  if (argc == 2) {
    hexToBytes(argv[1], (message + 1));
    uint8_t i = 0;
    for (; argv[1][i] != '\0'; i++) {
      if (i % 2 == 0) {
        message[i / 2 + 1] = hexToByte(argv[1][i]);
      } else {
        message[i / 2 + 1] = (message[i / 2 + 1] << 4) + hexToByte(argv[1][i]);
      }
    }

    message[0] = strlen(argv[1]) / 2 + 2;
    nrf_802154_transmit_raw(message, true);
    nrf_cli_print(p_cli, "Sending %u bytes", i / 2);
  }
}

void nrf_cli_cmd_channel(nrf_cli_t const *p_cli, size_t argc, char **argv) {
  if (argc == 2) {
    uint8_t channel;
    if (!sscan_uint8(argv[1], &channel)) {
      nrf_cli_print(p_cli, "Invalid channel");
    } else if ((channel < 11) || (channel > 26)) {
      nrf_cli_print(p_cli, "Only channels from 11 to 26 are supported");
    } else {
      nrf_802154_channel_set(channel);
    }
  } else {
    nrf_cli_print(p_cli, "Channel: %u", nrf_802154_channel_get());
  }
}

NRF_CLI_CMD_REGISTER(send, NULL, "IEEE 802.15.4 send", nrf_cli_cmd_send);
NRF_CLI_CMD_REGISTER(channel, NULL, "IEEE 802.15.4 channel", nrf_cli_cmd_channel);
