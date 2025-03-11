/*
 * SnakeLogic.h
 *
 *  Created on: Mar 10, 2025
 *      Authors: Dmytro Blashchak, Nazar Dotsenko, Stepan Bereza
 */

#ifndef INC_SNAKELOGIC_H_
#define INC_SNAKELOGIC_H_

void send_preload_arrays(uint8_t *body_x, uint8_t *body_y, uint8_t length);

void spawn_apple();

void move_snake(uint8_t command);

void send_coordinates();

#endif /* INC_SNAKELOGIC_H_ */
