 #include <stdint.h>
#include <stdio.h>
#include <string.h>

#define START_BYTE 0x7E

// Функція обчислення CRC-16-CCITT (поліном 0x1021, початкове значення 0xFFFF)
uint16_t crc16_ccitt(const uint8_t *data, uint16_t len, uint8_t cmd, uint16_t frog_x, uint16_t frog_y) {
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
// Функція кодування кадру: створюється масив байтів за форматом:
// [START_BYTE][LENGTH][PAYLOAD][CRC_HIGH][CRC_LOW]
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
    return crc;
}

// Функція декодування кадру, яка перевіряє його правильність.
// Повертає 0, якщо кадр валідний, або негативне значення у випадку помилки.
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
    return (received_crc == computed_crc) ? 0 : -4;
}

int main(void) {
    // Приклад даних для передачі
    uint8_t payload[] = "hello1234!";
    uint8_t CMD = 2;
    uint8_t payload_len = (uint8_t)strlen((char*)payload);
    uint16_t frog_x = 10;
    uint16_t frog_y = 13;

    // Тут можна число збільшити при потребі
    uint8_t frame[255];

    // Кодування кадру
    uint16_t crc = encode_frame(payload, payload_len, frame, CMD, frog_x, frog_y);
    printf("Frame ready, CRC: 0x%04X\n", crc);

    // Загальна довжина кадру = 1 (START) + 1 (CMD) + 1 (LENGTH) + payload + 2 (FROG) + 2 (CRC)
    uint8_t frame_len = payload_len + 7;

    // Декодування та перевірка кадру
    int result = decode_frame(frame, frame_len);
    if (result == 0)
        printf("Valid. CRC ok.\n");
    else
        printf("Invalid, error: %d\n", result);

    return 0;
}