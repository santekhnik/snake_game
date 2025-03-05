#ifndef PROTOCOL_H
#define PROTOCOL_H
#include <main.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define START_BYTE 0x7E

// Функція обчислення CRC-16-CCITT для пакету змійки (поліном 0x1021, початкове значення 0xFFFF)
uint16_t crc16_ccitt_snake(const uint8_t *data, uint16_t len, uint8_t cmd, uint8_t frog_x, uint8_t frog_y);
// Функція обчислення CRC-16-CCITT (поліном 0x1021, початкове значення 0xFFFF)
uint16_t crc16_ccitt(const uint8_t *data, uint16_t len, uint8_t cmd);

//функція кодування пакету змії
uint16_t encode_frame_snake(const uint8_t *payload, uint8_t payload_len, uint8_t *frame, uint8_t cmd_byte, uint8_t frog_x, uint8_t frog_y);

//функція кодування пакету помилки
uint16_t encode_frame_err(const uint8_t *payload, uint8_t *frame, uint8_t cmd_byte) ;

//функція кодування пакету закінчення гри
uint16_t encode_frame_end(const uint8_t *payload, uint8_t payload_len, uint8_t *frame, uint8_t cmd_byte);

//функція розкодування пакету
int decode_frame(const uint8_t *frame, uint8_t frame_len) ;

#endif
