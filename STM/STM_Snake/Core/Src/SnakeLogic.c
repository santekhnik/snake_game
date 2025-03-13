#include "SnakeLogic.h"
#include <stdint.h>

uint8_t move_snake(uint8_t command, uint8_t frog_x, uint8_t frog_y, uint8_t *payload){

    static uint8_t snake_length = 4;
    static uint8_t x_buffer[128] = {10, 11, 12, 13};
    static uint8_t y_buffer[128] = {15, 15, 15, 15};

    for (int i = snake_length - 1; i > 0; i--) {
        x_buffer[i] = x_buffer[i - 1];
        y_buffer[i] = y_buffer[i - 1];
    }

    //от я просто хочу здохнути від вашого програмування бляха
    switch (command) {
        case 1: y_buffer[0]--; break;
        case 2: y_buffer[0]++; break;
        case 3: x_buffer[0]--; break;
        case 4: x_buffer[0]++; break;
        default: break;
    }


    if (x_buffer[0] == frog_x && y_buffer[0] == frog_y) {
        snake_length++;
        if (snake_length > 128) snake_length = 128;
    }


    for (int i = 0; i < snake_length; i++) {
        payload[2 * i] = x_buffer[i];
        payload[2 * i + 1] = y_buffer[i];
    }
}
