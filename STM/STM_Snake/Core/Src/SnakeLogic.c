#include "SnakeLogic.h"
#include <stdint.h>
#include <stdlib.h>

uint8_t snake_length = 4;
static uint8_t x_buffer[128] = {10, 11, 12, 13};
static uint8_t y_buffer[128] = {15, 15, 15, 15};

// Оголошуємо статичні змінні для збереження напрямку та допоміжної логіки
static uint8_t last_command = 0;  // 0 — змійка стоїть
static uint8_t legit = 1;

void randomize_apple(uint8_t *frog_x, uint8_t *frog_y) {
    *frog_x = (rand() % 16) + 1;
    *frog_y = (rand() % 16) + 1;
}

void reset_game(uint8_t *frog_x, uint8_t *frog_y) {
    snake_length = 4;
    uint8_t start_x = 10;
    uint8_t start_y = 15;
    x_buffer[0] = start_x;
    y_buffer[0] = start_y;
    for (int i = 1; i < snake_length; i++) {
        x_buffer[i] = start_x - i;
        y_buffer[i] = start_y;
    }
    randomize_apple(frog_x, frog_y);
    // Скидаємо напрямок змійки
    last_command = 0;
}

uint8_t move_snake(uint8_t command, uint8_t *frog_x, uint8_t *frog_y, uint8_t *payload) {
    // Оновлюємо напрямок лише для команд 1-4
    if (command >= 1 && command <= 4) {
        // Забороняємо рух у протилежну сторону
        if (!((command == 1 && last_command == 2) ||
              (command == 2 && last_command == 1) ||
              (command == 3 && last_command == 4) ||
              (command == 4 && last_command == 3))) {
            last_command = command;
        }
    }
    // Якщо змійка має рухатися, пересуваємо всі сегменти
    if (last_command != 0) {
        for (int i = snake_length; i > 0; i--) {
            x_buffer[i] = x_buffer[i - 1];
            y_buffer[i] = y_buffer[i - 1];
        }
        // Оновлюємо координати голови залежно від напрямку
        switch (last_command) {
            case 1: y_buffer[0]--; break;  // Вгору
            case 2: y_buffer[0]++; break;  // Вниз
            case 3: x_buffer[0]--; break;  // Вліво
            case 4: x_buffer[0]++; break;  // Вправо
            default: break;
        }
    }
    // Перехід через границі поля
    for (int i = 0; i < snake_length; i++) {
        if (x_buffer[i] >= 17) x_buffer[i] = 1;
        else if (x_buffer[i] < 1) x_buffer[i] = 16;
        if (y_buffer[i] >= 17) y_buffer[i] = 1;
        else if (y_buffer[i] < 1) y_buffer[i] = 16;
    }
    // Перевірка на "з'їдання" яблука
    if (x_buffer[0] == *frog_x && y_buffer[0] == *frog_y) {
        // Дублюємо останній сегмент і збільшуємо довжину змійки
        x_buffer[snake_length] = x_buffer[snake_length - 1];
        y_buffer[snake_length] = y_buffer[snake_length - 1];
        snake_length++;
        legit = 0;
        // Генеруємо нову позицію яблука, поки воно не опиниться поза тілом змійки
        for (uint8_t j = 0; j < snake_length; j++) {
            do {
                randomize_apple(frog_x, frog_y);
                legit = 1;
                for (uint8_t k = 0; k < snake_length; k++) {
                    if (x_buffer[k] == *frog_x && y_buffer[k] == *frog_y) {
                        legit = 0;
                        break;
                    }
                }
            } while (!legit);
        }
        if (snake_length > 255)
            snake_length = 255;
    }
    // Перевірка на зіткнення голови з тілом
    for (int i = 1; i < snake_length; i++) {
        if (x_buffer[0] == x_buffer[i] && y_buffer[0] == y_buffer[i]) {
            dead_inside = 8;  // Зіткнення
        }
    }
    // Формуємо payload для відображення координат змійки
    for (int i = 0; i < snake_length; i++) {
        payload[2 * i] = x_buffer[i];
        payload[2 * i + 1] = y_buffer[i];
    }
    return 0;
}
