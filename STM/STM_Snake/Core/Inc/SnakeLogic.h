/*
 * SnakeLogic.h
 *
 *  Created on: Mar 10, 2025
 *      Authors: Dmytro Blashchak, Nazar Dotsenko, Stepan Bereza
 */
#include <stdint.h>
#ifndef INC_SNAKELOGIC_H_
#define INC_SNAKELOGIC_H_

uint8_t move_snake(uint8_t command, uint8_t *frog_x, uint8_t *frog_y, uint8_t *payload);

extern uint8_t snake_length;

void randomize_apple();
#endif /* INC_SNAKELOGIC_H_ */
