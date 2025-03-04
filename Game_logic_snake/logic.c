#include <stdio.h>
#include <stdlib.h>
#include <conio.h>
#include <windows.h>

#define WIDTH 20
#define HEIGHT 10
#define MAX_LENGTH 100

typedef struct {
    int x, y;
} Point;

Point snake[MAX_LENGTH];
int snake_length;
Point apple;
char direction;
int game_over;
char choice;

void setup() {
    snake_length = 1;
    direction = 'd';
    game_over = 0;
    snake[0].x = WIDTH / 2;
    snake[0].y = HEIGHT / 2;

    do {
        apple.x = rand() % WIDTH;
        apple.y = rand() % HEIGHT;
    } while (apple.x == snake[0].x && apple.y == snake[0].y);

    printf("Game is ready. Press t key to start...\n");
    while (1) {
        choice = _getch();
        if (choice == 't') {
            break;        } 

        else if (choice == 27) { 
            return 0;
        }
    }
}

void draw() {
    system("cls");
    for (int i = 0; i < HEIGHT; i++) {
        for (int j = 0; j < WIDTH; j++) {
            int is_snake = 0;
            for (int k = 0; k < snake_length; k++) {
                if (snake[k].x == j && snake[k].y == i) {
                    printf(k == 0 ? "O" : "o");
                    is_snake = 1;
                    break;
                }
            }
            if (apple.x == j && apple.y == i) {
                printf("A");
            }
            else if (!is_snake) {
                printf(".");
            }
        }
        printf("\n");
    }
}

void log_snake() {
    printf("Snake state (length: %d): ", snake_length);
    for (int i = 0; i < snake_length; i++) {
        printf("(%d, %d) ", snake[i].x, snake[i].y);
    }
    printf("\n");
}

void update() {
    if (snake_length >= MAX_LENGTH) {
        game_over = 1;
        printf("You won! Maximum snake length reached!\n");
        return;
    }

    for (int i = snake_length; i > 0; i--) {
        snake[i] = snake[i - 1];
    }
    switch (direction) {
    case 'w': snake[0].y--; break;
    case 's': snake[0].y++; break;
    case 'a': snake[0].x--; break;
    case 'd': snake[0].x++; break;
    }
    if (snake[0].x < 0 || snake[0].x >= WIDTH || snake[0].y < 0 || snake[0].y >= HEIGHT) {
        game_over = 1;
        printf("Game over: snake hit the wall!\n");
        return;
    }
    for (int i = 1; i < snake_length; i++) {
        if (snake[0].x == snake[i].x && snake[0].y == snake[i].y) {
            game_over = 1;
            printf("Game over: snake hit itself!\n");
            return;
        }
    }
    if (snake[0].x == apple.x && snake[0].y == apple.y) {
        snake_length++;
        do {
            apple.x = rand() % WIDTH;
            apple.y = rand() % HEIGHT;
        } while (apple.x == snake[0].x && apple.y == snake[0].y);
        printf("Snake ate an apple! New apple position: (%d, %d)\n", apple.x, apple.y);
    }
    log_snake();
}

void input() {
    if (_kbhit()) {
        char key = _getch();
        if ((key == 'w' && direction != 's') ||
            (key == 's' && direction != 'w') ||
            (key == 'a' && direction != 'd') ||
            (key == 'd' && direction != 'a')) {
            direction = key;
        }
    }
}

int main() {
    while (1) {
        setup();
        while (!game_over) {
            draw();
            input();
            update();
            Sleep(100);
        }
        printf("Game over! Your score: %d\n", snake_length - 1);
        printf("Press 'r' to restart or any other key to exit...\n");

        while (1) {
            choice = _getch();
            if (choice == 'r') {
                break; 
            }
            else if (choice == 27) { 
                return 0;
            }
        }
    }
}
