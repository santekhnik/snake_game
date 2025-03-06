#ifndef PROTOCOL_H
#define PROTOCOL_H

#include "main.h"
#include <stdint.h>
#include <string.h>

#define START_BYTE 0x7E

// Обчислення CRC-16-CCITT для пакету змійки (поліном 0x1021, початкове значення 0xFFFF)
uint16_t crc16_ccitt_snake(const uint8_t *data, uint16_t len, uint8_t cmd, uint8_t frog_x, uint8_t frog_y);
// Обчислення CRC-16-CCITT для загальних випадків (поліном 0x1021, початкове значення 0xFFFF)
uint16_t crc16_ccitt(const uint8_t *data, uint16_t len, uint8_t cmd);

// Функція кодування пакету змійки.
// Структура пакету:
//   [0]         : START_BYTE
//   [1]         : CMD (тип пакету)
//   [2]         : довжина корисного навантаження (payload_len)
//   [3 .. ...]  : payload (payload_len байт)
//   [3+payload_len] : frog_x
//   [4+payload_len] : frog_y
//   [5+payload_len] : CRC (старший байт)
//   [6+payload_len] : CRC (молодший байт)
// Функція повертає загальну довжину сформованого пакету.
uint8_t encode_frame_snake(const uint8_t *payload, uint8_t payload_len, uint8_t *frame, uint8_t cmd_byte, uint8_t frog_x, uint8_t frog_y);

// Функція кодування пакету помилки.
// Структура пакету:
//   [0] : START_BYTE
//   [1] : CMD (тип пакету)
//   [2..3] : payload (2 байти)
//   [4] : CRC (старший байт)
//   [5] : CRC (молодший байт)
// Функція повертає довжину пакету (6 байт).
uint16_t encode_frame_err(const uint8_t *payload, uint8_t *frame, uint8_t cmd_byte);

// Функція кодування пакету завершення гри.
// Структура пакету:
//   [0]         : START_BYTE
//   [1]         : CMD (тип пакету)
//   [2]         : довжина корисного навантаження (payload_len, зазвичай 1 байт)
//   [3]         : payload (1 байт)
//   [4]         : CRC (старший байт)
//   [5]         : CRC (молодший байт)
// Функція повертає довжину пакету (payload_len + 5).
uint16_t encode_frame_end(const uint8_t *payload, uint8_t payload_len, uint8_t *frame, uint8_t cmd_byte);

// Функція розкодування пакету. Повертає 0, якщо все гаразд, або код помилки.
int decode_frame(const uint8_t *frame, uint8_t frame_len);

#endif
