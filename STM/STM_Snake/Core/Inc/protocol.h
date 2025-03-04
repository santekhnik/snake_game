#include <main.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define START_BYTE 0x7E

// Функція обчислення CRC-16-CCITT (поліном 0x1021, початкове значення 0xFFFF)
uint16_t crc16_ccitt(const uint8_t *data, uint16_t len, uint8_t cmd, uint8_t frog_x, uint8_t frog_y) {
    uint16_t crc = 0xFFFF;
    crc ^= ((uint16_t)cmd << 8);
    crc ^= ((uint16_t)frog_x << 8) | frog_y;

    for (uint16_t i = 0; i < len; i++) {
        crc ^= ((uint16_t)data[i] << 8);
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x8000)
                crc = (crc << 1) ^ 0x1021;
            else
                crc <<= 1;
        }
    }
    return crc;
}
uint16_t encode_frame(const uint8_t *payload, uint8_t payload_len, uint8_t *frame, uint8_t cmd_byte, uint8_t frog_x, uint8_t frog_y) {
    frame[0] = START_BYTE;                  // Початковий байт
    frame[1] = cmd_byte;                    // Байт комади
    frame[2] = payload_len;                 // Довжина корисного навантаження
    memcpy(&frame[3], payload, payload_len);//копіюємо пейлоад
    frame[3 + payload_len] = frog_x;        //x жабки
    frame[4 + payload_len] = frog_y;        //y жабки

    uint16_t crc = crc16_ccitt(payload, payload_len, cmd_byte, frog_x, frog_y);    // Додавання CRC (старший байт перший)
    //frame[4] ^= 0x02; //тестові приколи щоб все зламати
    //frame[3] ^= 0x03; //тестові приколи щоб все зламати
    frame[5 + payload_len] = (crc >> 8) & 0xFF; //crc high
    frame[6 + payload_len] = crc & 0xFF;        //crc low
    printf("RAW crc: 0x%04X\n", crc);
    printf("RAW frame: ");
    for (uint8_t i = 0; i < (payload_len + 7); i++) {
        printf("%02X", frame[i]);
    }
    printf("\n");
    printf("Frame structure: ");
    for (uint8_t i = 0; i < (payload_len + 7); i++) {
        printf("%02X ", frame[i]);
    }
    printf("\n");
    return crc;
}
int decode_frame(const uint8_t *frame, uint8_t frame_len) {
    // Мінімальна довжина: 1 байт (START) + 1 байт комади (CMD) + 1 байт (LENGTH) + 0 (PAYLOAD)+ 2 байти (frog)  + 2 байти (CRC) = 7 байтів

    if (frame_len < 7)
        return -1; // Кадр занадто короткий
    if (frame[0] != START_BYTE)
        return -2; // Невірний стартовий байт

    uint8_t cmd_byte = frame[1];
    uint8_t payload_len = frame[2];
    if (frame_len != (uint8_t)(payload_len + 7))
        return -3; // Невідповідність довжини кадру

    uint8_t frog_x = frame[3 + payload_len];
    uint8_t frog_y = frame[4 + payload_len];

    // Отримання переданого CRC (big-endian)

    uint16_t received_crc = (frame[5 + payload_len] << 8) | frame[6 + payload_len];
    // Обчислення CRC на основі PAYLOAD
    uint16_t computed_crc = crc16_ccitt(&frame[3], payload_len, cmd_byte, frog_x, frog_y);
    printf("Received CRC: 0x%04X, Computed CRC: 0x%04X\n", received_crc, computed_crc);
    return (received_crc == computed_crc) ? 0 : -4;
}
