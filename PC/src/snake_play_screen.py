import pygame
import sys
import threading
import time
from frame_codec import STMProtocol
from settings import WIDTH, HEIGHT, CELL_SIZE, GRID_WIDTH, GRID_HEIGHT, FIELD_OFFSET_X, FIELD_OFFSET_Y
from notification_manager import NotificationManager

protocol = STMProtocol()

class SnakePlayScreen:

    GRAY = (50, 50, 50)  # Сірий фон
    BLACK = (0, 0, 0)  # Чорне поле для гри
    WHITE = (255, 255, 255)  # Білий колір
    RED = (255, 0, 0)  # Червоний (змійка)

    KEY_MAP = {
        pygame.K_w: 1,  # W -> Вверх
        pygame.K_s: 2,  # S -> Вниз
        pygame.K_a: 3,  # A -> Вліво
        pygame.K_d: 4,  # D -> Вправо
        pygame.K_UP: 1,  # Стрілка вверх
        pygame.K_DOWN: 2,  # Стрілка вниз
        pygame.K_LEFT: 3,  # Стрілка вліво
        pygame.K_RIGHT: 4,  # Стрілка вправо
        pygame.K_SPACE: 5  # Пробіл (пауза)
    }

    def __init__(self, uart_conn):
        """Отримуємо підключення UART від головного меню"""
        self.uart_conn = uart_conn
        self.protocol = STMProtocol()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.running = True
        self.clock = pygame.time.Clock()

        self.notification_manager = NotificationManager()

        self.snake_positions = []  # Координати змійки
        self.frog_position = (0, 0)  # Координати жабки

        # **Стартуємо потік для читання UART**
        self.uart_thread = threading.Thread(target=self.read_uart_data, daemon=True)
        self.uart_thread.start()
        self.uart_conn.uart.write(protocol.encode_frame(3, 0))
        time.sleep(0.1)
        self.uart_conn.uart.write(protocol.encode_frame(3, 1))
        time.sleep(0.1)


    def read_uart_data(self):
        """Асинхронне отримання координат з UART, щоб не блокувати гру"""

        while self.running:

            data = self.uart_conn.read_packet()
            if data["status"] == "success":
                parsed_data = data["data"]
                self.snake_positions = parsed_data["payload"]
                self.frog_position = parsed_data["frog"]
                print(f"📩 Отримано дані: {parsed_data}")

            time.sleep(0.1)  # Маленька затримка для зменшення навантаження

    def run(self):
        """Головний цикл гри"""
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(10)  # FPS

    def handle_events(self):
        """Обробка подій"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

    def draw(self):
        """Малювання гри"""
        self.screen.fill(self.GRAY)  # Чорний фон
        self.draw_grid()
        self.draw_snake()
        self.draw_frog()
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
                pygame.draw.rect(self.screen, self.BLACK, rect)
                pygame.draw.rect(self.screen, self.WHITE, rect, 1)

    def draw_snake(self):
        """Малюємо змійку"""
        for segment in self.snake_positions:
            x, y = segment
            x = x - 1
            y = y - 1
            rect = pygame.Rect(
                FIELD_OFFSET_X + x * CELL_SIZE,
                FIELD_OFFSET_Y + y * CELL_SIZE,
                CELL_SIZE, CELL_SIZE
            )
            pygame.draw.rect(self.screen, self.RED, rect)

    def draw_frog(self):
        """Малюємо жабку"""
        x, y = self.frog_position
        x = x-1
        y = y-1
        rect = pygame.Rect(
            FIELD_OFFSET_X + x * CELL_SIZE,
            FIELD_OFFSET_Y + y * CELL_SIZE,
            CELL_SIZE, CELL_SIZE
        )
        pygame.draw.rect(self.screen, (0, 255, 0), rect)  # Жабка зелена

    def handle_events(self):
        """Обробка подій клавіатури для керування змійкою"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

            if event.type == pygame.KEYDOWN:
                if event.key in self.KEY_MAP:
                    command = self.KEY_MAP[event.key]
                    self.send_command_to_stm(command)

    def send_command_to_stm(self, command):
        """Відправка команди на STM"""
        if self.uart_conn and self.uart_conn.uart:
            self.uart_conn.uart.write(self.protocol.encode_frame(3, command))
            print(f"📤 Відправлено команду: {command}")

    def quit_game(self):
        """Вихід з гри"""
        self.running = False
        pygame.quit()
        sys.exit()
