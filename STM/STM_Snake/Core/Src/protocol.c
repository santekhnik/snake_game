#include <main.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <protocol.h>



// Функція обчислення CRC-16-CCITT для пакету змійки (поліном 0x1021, початкове значення 0xFFFF)
// Обчислення CRC-16-CCITT для пакету змійки
uint16_t crc16_ccitt_snake(const uint8_t *data, uint8_t len, uint8_t cmd, uint8_t frog_x, uint8_t frog_y) {
    uint16_t crc = 0xFFFF;
    crc ^= ((uint16_t)cmd << 8);
    crc ^= (((uint16_t)frog_x << 8) | frog_y);
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
uint8_t encode_frame_snake(const uint8_t *payload, uint8_t payload_len, uint8_t *tx_buffer, uint8_t cmd_byte, uint8_t frog_x, uint8_t frog_y) {

	tx_buffer[0] = START_BYTE;
	tx_buffer[1] = cmd_byte;
	tx_buffer[2] = payload_len;

    for (uint8_t i = 0; i < payload_len; i++) {
    tx_buffer[3 + i] = payload[i];
    }

    tx_buffer[3 + payload_len] = frog_x;
    tx_buffer[4 + payload_len] = frog_y;

   uint16_t crc = crc16_ccitt_snake(payload, payload_len, cmd_byte, frog_x, frog_y);
   	tx_buffer[5 + payload_len] = (crc >> 8) & 0xFF;
    tx_buffer[6 + payload_len] = crc & 0xFF;

    return (7+payload_len);
}


//функція кодування пакету помилки
uint16_t encode_frame_err(const uint8_t *payload, uint8_t *tx_buffer, uint8_t cmd_byte) {
	tx_buffer[0] = START_BYTE;
	tx_buffer[1] = cmd_byte;
    // Очікуємо, що payload містить рівно 2 байти
    memcpy(&tx_buffer[2], payload, 2);
    uint16_t crc = crc16_ccitt(payload, 2, cmd_byte);
    tx_buffer[4] = (crc >> 8) & 0xFF;
    tx_buffer[5] = crc & 0xFF;

    return 6;  // Структура пакету має 6 байт
}

//функція кодування пакету закінчення гри
uint16_t encode_frame_end(const uint8_t *payload, uint8_t payload_len, uint8_t *tx_buffer, uint8_t cmd_byte) {
	tx_buffer[0] = START_BYTE;                  				// Початковий байт
	tx_buffer[1] = cmd_byte;                    				// Байт комади
    memcpy(&tx_buffer[2], payload, payload_len);				// копіюємо пейлоад
    uint16_t crc = crc16_ccitt(payload, 1, cmd_byte);    	// Додавання CRC (старший байт перший)
    tx_buffer[3 + payload_len] = (crc >> 8) & 0xFF; 			// crc high
    tx_buffer[4 + payload_len] = crc & 0xFF;        			// crc low
    return 5;
}

int decode_frame(const uint8_t *frame, uint8_t frame_len) {
	// Кадр занадто короткий
    if (frame_len < 5){
    	return -1;
    }
    // Невірний стартовий байт
    if (frame[0] != START_BYTE){
    		return -2;
    }

    uint8_t cmd_byte = frame[1];
   	uint8_t payload = frame[2];
   	// Невідповідність довжини кадру
   	if (frame_len != 5) {
    			return -3;
    }

    uint16_t received_crc = (frame[3] << 8) | frame[4];				// Отримання переданого CRC
    uint16_t computed_crc = crc16_ccitt(&frame[2], 1, cmd_byte);    // Обчислення CRC на основі PAYLOAD
    return (received_crc == computed_crc) ? 0 : -4;
}

