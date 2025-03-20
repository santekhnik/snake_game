/*
 * SnakeLogic.h
 *
 *  Created on: Mar 10, 2025
 *      Authors: Dmytro Blashchak, Stepan Bereza, Nazar Dotsenko
 */

#include <stdint.h>
#ifndef INC_SNAKELOGIC_H_
#define INC_SNAKELOGIC_H_
extern uint8_t snake_length;
extern uint8_t dead_inside;



uint8_t move_snake(uint8_t command, uint8_t *frog_x, uint8_t *frog_y, uint8_t *payload);

void reset_game(uint8_t *frog_x, uint8_t *frog_y);

void randomize_apple();




#endif /* INC_SNAKELOGIC_H_ */
