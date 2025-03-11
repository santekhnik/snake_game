#include "main.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define MAX_LENGTH 100

/* Глобальні змінні */
extern UART_HandleTypeDef huart1;

uint8_t rxdata;
int x = 0, y = 0;  // Початкові координати змійки
uint8_t command = 4; // edited starting point
int length = 1;  // Початкова довжина змійки
int apple_x, apple_y;
int body_x[100];
int body_y[10];

/* Прототипи функцій */
void move_snake(uint8_t command);
void send_coordinates();
void spawn_apple();

/* Функція обробки прийому UART */


/* Функція відправки координат */
void send_coordinates() {
    char buffer[200];
    int len = sprintf(buffer, "H:%d,%d A:%d,%d L:%d B:", x, y, apple_x, apple_y, length);

    for (int i = 0; i < length; i++) {
        len += sprintf(buffer + len, "(%d,%d) ", body_x[i], body_y[i]);
    }

    strcat(buffer, "\r\n");
    HAL_UART_Transmit(&huart1, (uint8_t *)buffer, strlen(buffer), HAL_MAX_DELAY);
}

/* Генерація нового яблука */
void spawn_apple() {
    apple_x = rand() % 10;
    apple_y = rand() % 10;
}

/* Функція руху змійки */
void move_snake(uint8_t command) {

    if (body_x[0] == apple_x && body_y[0] == apple_y) {
        length++;
        spawn_apple();
    }
    for (int i = length; i > 0; i--) {
        body_x[i] = body_x[i - 1];
        body_y[i] = body_y[i - 1];
    }

    switch(command){
    	case(1):

    	body_y[0]++;

    	break;

    	case(2):

		body_y[0]--;

    	break;

    	case(3):

		body_x[0]--;

    	break;

    	case(4):

		body_x[0]++;

    	break;
}
}
