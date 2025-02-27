#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define START_BYTE 0x7E

// Функція обчислення CRC-16-CCITT (поліном 0x1021, початкове значення 0xFFFF)
uint16_t crc16_ccitt(const uint8_t *data, uint16_t len) {
    uint16_t crc = 0xFFFF;
    for (uint16_t i = 0; i < len; i++) {
        // Дані байтом "втягуються" у верхній байт CRC
        crc ^= ((uint16_t)data[i] << 8);
        // Обробка кожного біта
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x8000)
                crc = (crc << 1) ^ 0x1021;
            else
                crc <<= 1;
        }
    }
    return crc;
}

// Функція кодування кадру: створюється масив байтів за форматом:
// [START_BYTE][LENGTH][PAYLOAD][CRC_HIGH][CRC_LOW]
uint16_t encode_frame(const uint8_t *payload, uint8_t payload_len, uint8_t *frame) {
    frame[0] = START_BYTE;      // Початковий байт
    frame[1] = payload_len;     // Довжина корисного навантаження
    memcpy(&frame[2], payload, payload_len); // Копіювання даних
    // Обчислення CRC для PAYLOAD
    uint16_t crc = crc16_ccitt(payload, payload_len);
    // Додавання CRC (старший байт перший)
    //frame[2] ^= 0x02;
    //frame[3] ^= 0x03;
    frame[2 + payload_len]     = (crc >> 8) & 0xFF;
    frame[2 + payload_len + 1] = crc & 0xFF;
    printf("RAW crc: 0x%04X\n", frame);
    printf("RAW frame: ");
    for (uint8_t i = 0; i < (payload_len + 4); i++) {
        printf("%02X", frame[i]);
    }
    printf("\n");
    return crc;
}

// Функція декодування кадру, яка перевіряє його правильність.
// Повертає 0, якщо кадр валідний, або негативне значення у випадку помилки.
int decode_frame(const uint8_t *frame, uint8_t frame_len) {
    // Мінімальна довжина: 1 байт (START) + 1 байт (LENGTH) + 0 (PAYLOAD) + 2 байти (CRC) = 4 байти
    if (frame_len < 4)
        return -1; // Кадр занадто короткий
    if (frame[0] != START_BYTE)
        return -2; // Невірний стартовий байт
    uint8_t payload_len = frame[1];
    if (frame_len != (uint8_t)(payload_len + 4))
        return -3; // Невідповідність довжини кадру
    // Отримання переданого CRC (big-endian)
    uint16_t received_crc = (frame[2 + payload_len] << 8) | frame[2 + payload_len + 1];
    // Обчислення CRC на основі PAYLOAD
    uint16_t computed_crc = crc16_ccitt(&frame[2], payload_len);
    return (received_crc == computed_crc) ? 0 : -4;
}

int main(void) {
    // Приклад даних для передачі
    uint8_t payload[] = "hello";
    uint8_t payload_len = (uint8_t)strlen((char*)payload);
    // Туту можна число збільшити при потребі
    uint8_t frame[255];

    // Кодування кадру
    uint16_t crc = encode_frame(payload, payload_len, frame);
    printf("Frame ready, CRC: 0x%04X\n", crc);

    // Загальна довжина кадру = 1 (START) + 1 (LENGTH) + payload_len + 2 (CRC)
    uint8_t frame_len = payload_len + 4;

    // Декодування та перевірка кадру
    int result = decode_frame(frame, frame_len);
    if (result == 0)
        printf("Valid. CRC ok.\n");
    else
        printf("Invalid, error: %d\n", result);

    return 0;
}

