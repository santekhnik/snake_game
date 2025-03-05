#include <main.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <protocol.h>

// Функція обчислення CRC-16-CCITT для пакету змійки (поліном 0x1021, початкове значення 0xFFFF)
uint16_t crc16_ccitt_snake(const uint8_t *data, uint16_t len, uint8_t cmd, uint8_t frog_x, uint8_t frog_y) {
    uint16_t crc = 0xFFFF;									//початкове значення
    crc ^= ((uint16_t)cmd << 8);							//команда cmd
    crc ^= ((uint16_t)frog_x << 8) | frog_y;				//ставимо жабку
    for (uint16_t i = 0; i < len; i++) {
        crc ^= ((uint16_t)data[i] << 8);					//записуємо корисні дані
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x8000)
                crc = (crc << 1) ^ 0x1021;					//поліном
            else
                crc <<= 1;
        }
    }
    return crc;
}
// Функція обчислення CRC-16-CCITT (поліном 0x1021, початкове значення 0xFFFF)
uint16_t crc16_ccitt(const uint8_t *data, uint16_t len, uint8_t cmd) {
    uint16_t crc = 0xFFFF;									//початкове значення
    crc ^= ((uint16_t)cmd << 8);							//команда cmd

    for (uint16_t i = 0; i < len; i++) {
        crc ^= ((uint16_t)data[i] << 8);
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x8000)
                crc = (crc << 1) ^ 0x1021;					//поліном
            else
                crc <<= 1;
        }
    }
    return crc;
}

//функція кодування пакету змії
uint16_t encode_frame_snake(const uint8_t *payload, uint8_t payload_len, uint8_t *frame, uint8_t cmd_byte, uint8_t frog_x, uint8_t frog_y) {
    frame[0] = START_BYTE;                  				// Початковий байт
    frame[1] = cmd_byte;                    				// Байт комади
    frame[2] = payload_len;                 				// Довжина корисного навантаження
    memcpy(&frame[3], payload, payload_len);				// копіюємо пейлоад
    frame[3 + payload_len] = frog_x;        				// x жабки
    frame[4 + payload_len] = frog_y;        				// y жабки
    uint16_t crc = crc16_ccitt_snake(payload, payload_len, cmd_byte, frog_x, frog_y);    // Додавання CRC (старший байт перший)
    frame[5 + payload_len] = (crc >> 8) & 0xFF; 			// crc high
    frame[6 + payload_len] = crc & 0xFF;        			// crc low
    return frame;
}

//функція кодування пакету помилки
uint16_t encode_frame_err(const uint8_t *payload, uint8_t *frame, uint8_t cmd_byte) {
    frame[0] = START_BYTE;                  				// Початковий байт
    frame[1] = cmd_byte;                    				// Байт комади
    memcpy(&frame[2], payload, 2);							// копіюємо пейлоад
    uint16_t crc = crc16_ccitt(payload, 2, cmd_byte);    	// Додавання CRC (старший байт перший)
    frame[4] = (crc >> 8) & 0xFF; //crc high
    frame[5] = crc & 0xFF;        							// crc low
    return frame;
}

//функція кодування пакету закінчення гри
uint16_t encode_frame_end(const uint8_t *payload, uint8_t payload_len, uint8_t *frame, uint8_t cmd_byte) {
    frame[0] = START_BYTE;                  				// Початковий байт
    frame[1] = cmd_byte;                    				// Байт комади
    memcpy(&frame[3], payload, payload_len);								// копіюємо пейлоад
    uint16_t crc = crc16_ccitt(payload, 1, cmd_byte);    	// Додавання CRC (старший байт перший)
    frame[3 + payload_len] = (crc >> 8) & 0xFF; 			// crc high
    frame[4 + payload_len] = crc & 0xFF;        			// crc low
    return frame;
}


int decode_frame(const uint8_t *frame, uint8_t frame_len) {

    if (frame_len < 5)
        return -1; 											// Кадр занадто короткий
    if (frame[0] != START_BYTE)
        return -2; 											// Невірний стартовий байт
    uint8_t cmd_byte = frame[1];
    uint8_t payload_len = frame[2];
    if (frame_len != 5)
        return -3; 													// Невідповідність довжини кадру
    uint16_t received_crc = (frame[3] << 8) | frame[4];				// Отримання переданого CRC
    uint16_t computed_crc = crc16_ccitt(&frame[3], 5, cmd_byte);    // Обчислення CRC на основі PAYLOAD
    return (received_crc == computed_crc) ? 0 : -4;
}

