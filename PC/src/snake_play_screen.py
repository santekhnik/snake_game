import pygame
import sys
from settings import WIDTH, HEIGHT, CELL_SIZE, GRID_WIDTH, GRID_HEIGHT, FIELD_OFFSET_X, FIELD_OFFSET_Y



class SnakePlayScreen:

    GRAY = (50, 50, 50)  # Сірий фон
    BLACK = (0, 0, 0)  # Чорне поле для гри
    WHITE = (255, 255, 255)  # Білий колір
    RED = (255, 0, 0)

    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.running = True
        self.clock = pygame.time.Clock()

    def run(self):
        """Головний цикл гри"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(10)  # FPS

    def handle_events(self):
        """Обробка подій"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

    def update(self):
        """Оновлення гри (поки що пуста функція)"""
        pass

    def draw(self):
        """Малювання гри"""
        self.screen.fill(self.GRAY)  # Чорний фон
        self.draw_grid()
        pygame.display.flip()

    def draw_grid(self):
        """Малюємо сітку для гри"""
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                rect = pygame.Rect(
                    FIELD_OFFSET_X + x * CELL_SIZE,
                    FIELD_OFFSET_Y + y * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(self.screen, self.BLACK, rect)  # Чорні квадрати
                pygame.draw.rect(self.screen, self.WHITE, rect, 1)  # Сітка (світліший сірий)

    def quit_game(self):
        """Вихід з гри"""
        self.running = False
        pygame.quit()
        sys.exit()
