#include "main.h"

uint8_t length,x, y = 1;
uint8_t command = 4;
uint8_t apple_x, apple_y;
uint8_t body_x[100];
uint8_t body_y[100];



/* Функція руху змійки */
uint8_t snake(uint8_t command) {

    if (body_x[0] == apple_x && body_y[0] == apple_y) {
        length++;
        apple_x = rand() % 10;
        apple_y = rand() % 10;
    }
    for (int i = length; i > 0; i--) {
        body_x[i] = body_x[i - 1];
        body_y[i] = body_y[i - 1];
    }
switch (command) {
case 1:
    body_y[0]++;
    y++;
    break;
case 2:
    body_y[0]--;
    y--;
    break;
case 3:
    body_x[0]--;
    x--;
    break;
case 4:
    body_x[0]++;
    x++;
    break;
default:

    break;}

    uint8_t payload[length * 2];  // Масив для об'єднаних даних

    for (uint8_t i = 0; i < length; i++) {
        payload[i * 2] = body_x[i];      // Записуємо елементи з першого масиву
        payload[i * 2 + 1] = body_y[i];  // Записуємо елементи з другого масиву
    }
return payload;
}
