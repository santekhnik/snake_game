#include "SnakeLogic.h"
#include <stdint.h>
#include <stdlib.h>

void randomize_apple(uint8_t *frog_x, uint8_t *frog_y) {
    *frog_x = rand() % 16;
    *frog_y = rand() % 16;
}



uint8_t move_snake(uint8_t command, uint8_t *frog_x, uint8_t *frog_y, uint8_t *payload) {
    uint8_t snake_length = 4;
    static uint8_t legit = 1;
    static uint8_t x_buffer[128] = {10, 11, 12, 13};
    static uint8_t y_buffer[128] = {15, 15, 15, 15};

    // Рухаєм змійку
    for (int i = snake_length - 1; i > 0; i--) {
        x_buffer[i] = x_buffer[i - 1];
        y_buffer[i] = y_buffer[i - 1];
    }

    // Обробка команд
    switch (command) {
    	case 1: y_buffer[0]--; break;  // Вгору
        case 2: y_buffer[0]++; break;  // Вниз
        case 3: x_buffer[0]--; break;  // Вліво
        case 4: x_buffer[0]++; break;  // Вправо
        default: break;
    }

    for (int i = 0; i < snake_length; i++) {
    if (x_buffer[i] >= 17) x_buffer[i] = 1;
        else if (x_buffer[i] < 1) x_buffer[i] = 16;

    if (y_buffer[i] >= 17) y_buffer[i] = 1;
        else if (y_buffer[i] < 1) y_buffer[i] = 16;
    }

    // Перевірка на "з'їдання" яблука
    if (x_buffer[0] == *frog_x && y_buffer[0] == *frog_y) {	//перевірка на з'їдене яблуко
            snake_length++;
            legit = 0;
        	for (uint8_t i = 0; i < snake_length; i++) {
        		i++;
        		do {
        			randomize_apple(frog_x, frog_y);
        		    legit = 1;
        		    if (frog_x == 0||frog_y == 0)legit = 0;
        		    for (uint8_t i = 0; i < snake_length; i++) {
        		        if (x_buffer[i] == *frog_x && y_buffer[i] == *frog_y) {
        		            legit = 0;
        		            break;
        		        }
        		    }
        		} while (!legit);
        	        }
            if (snake_length > 255) snake_length = 255;
    }

    for (int i = 1; i < snake_length; i++) {
      if (x_buffer[0] == x_buffer[i] && y_buffer[0] == y_buffer[i]) {
            return 8;  // Змійка зіткнулась сама з собою
         }
      }

    // Формуємо payload для відображення змійки
    for (int i = 0; i < snake_length; i++) {
        payload[2 * i] = x_buffer[i];
        payload[2 * i + 1] = y_buffer[i];
    }

    return 0;
}
