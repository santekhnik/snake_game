#include "SnakeLogic.h"
#include <stdint.h>




uint8_t move_snake(uint8_t command, uint8_t frog_x, uint8_t frog_y, uint8_t *payload){

	static uint8_t temp_x = 1;
	static uint8_t temp_y = 2;
    static uint8_t snake_length = 4;						//початкові координати і довжина змійки
    static uint8_t x_buffer[128] = {10, 11, 12, 13};
    static uint8_t y_buffer[128] = {15, 15, 15, 15};


    for (int i = snake_length - 1; i > 0; i--) {
        x_buffer[i] = x_buffer[i - 1];
        y_buffer[i] = y_buffer[i - 1];
    }


    switch (command) {
        case 1: y_buffer[0]--; break;						//реалізація кнопок управління
        case 2: y_buffer[0]++; break;
        case 3: x_buffer[0]--; break;
        case 4: x_buffer[0]++; break;
        default: break;
    }


    if (x_buffer[0] == frog_x && y_buffer[0] == frog_y) {	//перевірка на з'їдене яблуко
        snake_length++;

    	for (uint8_t i = 0; i < snake_length; i+2) {
    	            if (x_buffer[i] == temp_x && y_buffer[i++] == temp_y) {
    	                uint8_t valid = 0;
    	            }
    	        }
        if (snake_length > 255) snake_length = 255;			//що?
    }


    for (int i = 0; i < snake_length; i++) {  				//функція створення масиву корисної інформації
        payload[2 * i] = x_buffer[i];
        payload[2 * i + 1] = y_buffer[i];
    }
}
