#include "main.h"


uint8_t x, y = 1;
uint8_t body_x[128];			//массив значень координат X змійки
uint8_t body_y[128];			//массив значень координат Y змійки
uint8_t length;					//значення довжини змійки

/* Функція руху змійки */
uint8_t move_snake(uint8_t command,uint8_t frog_x, uint8_t frog_y) {

    if (body_x[0] == frog_x && body_y[0] == frog_y) {
        length++;
        randomize_apple();
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
