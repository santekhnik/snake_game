/*
 * SnakeLogic.h
 *
 *  Created on: Mar 10, 2025
 *      Authors: Dmytro Blashchak, Nazar Dotsenko, Stepan Bereza
 */
#include <stdint.h>
#ifndef INC_SNAKELOGIC_H_
#define INC_SNAKELOGIC_H_

void move_snake(uint8_t command, uint8_t *payload, uint8_t *frog_x, uint8_t *frog_y);

#endif /* INC_SNAKELOGIC_H_ */
