import pygame
import sys
import threading
import time
from frame_codec import STMProtocol
from settings import WIDTH, HEIGHT, CELL_SIZE, GRID_WIDTH, GRID_HEIGHT, FIELD_OFFSET_X, FIELD_OFFSET_Y
from button import back_button
from notification_manager import NotificationManager

protocol = STMProtocol()

class SnakePlayScreen:

    GRAY = (50, 50, 50)  # Темно-зелений фон
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

        self.frog_image = pygame.image.load("assets/images/apple.png").convert_alpha() #Додаємо фото жабок
        self.frog_image = pygame.transform.scale(self.frog_image, (1.1 * CELL_SIZE, 1.1 * CELL_SIZE))


        self.back_button = back_button

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
        self.back_button.draw(self.screen) # Додаємо кнопку для повернення назад у main menu
        pygame.display.flip()

    def draw_grid(self):
        """Малюємо ігрове поле і білу обводку"""
        dark_green = (50, 50, 20)

        # Малюємо темно-зелене поле
        field_rect = pygame.Rect(
            FIELD_OFFSET_X,
            FIELD_OFFSET_Y,
            GRID_WIDTH * CELL_SIZE,
            GRID_HEIGHT * CELL_SIZE
        )
        pygame.draw.rect(self.screen, dark_green, field_rect)

        # Малюємо білу обводку (рамку) навколо ігрового поля
        border_thickness = 3  # Товщина рамки в пікселях
        pygame.draw.rect(self.screen, self.WHITE, field_rect, border_thickness)

    def draw_snake(self):
        """Малюємо змійку з градієнтом і закругленими прямокутниками"""
        total_segments = len(self.snake_positions)
        for idx, segment in enumerate(self.snake_positions):
            x, y = segment
            x = x - 1
            y = y - 1

            # Створюємо прямокутник для кожного сегмента
            rect = pygame.Rect(
                FIELD_OFFSET_X + x * CELL_SIZE,
                FIELD_OFFSET_Y + y * CELL_SIZE,
                CELL_SIZE, CELL_SIZE
            )

            # Градієнт кольору (червоний → жовтий)
            if total_segments == 1:
                green_value = 0
            else:
                halfway = (total_segments - 1) / 2
                if idx <= halfway:
                    green_value = int(165 * idx / halfway)
                else:
                    green_value = int(165 + 90 * (idx - halfway) / halfway)

            green_value = max(0, min(255, green_value))
            color = (255, green_value, 0)

            # Малюємо прямокутник з заокругленими кутами
            pygame.draw.rect(self.screen, color, rect, border_radius=10)

    def draw_frog(self):
        """Малюємо жабку-картинку"""
        x, y = self.frog_position
        x = x - 1
        y = y - 1
        position = (
            FIELD_OFFSET_X + x * CELL_SIZE,
            FIELD_OFFSET_Y + y * CELL_SIZE
        )
        self.screen.blit(self.frog_image, position)

    def handle_events(self):
        """Обробка подій клавіатури для керування змійкою"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.back_button.rect.collidepoint(event.pos):
                    self.back_to_menu()

            if event.type == pygame.KEYDOWN:
                if event.key in self.KEY_MAP:
                    command = self.KEY_MAP[event.key]
                    self.send_command_to_stm(command)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

            self.back_button.handle_event(event)

            if event.type == pygame.USEREVENT:
                if event.button == self.back_button:
                    self.back_to_menu()

            if event.type == pygame.KEYDOWN:
                if event.key in self.KEY_MAP:
                    command = self.KEY_MAP[event.key]
                    self.send_command_to_stm(command)

    def back_to_menu(self):
        self.running = False
        from main import MainMenu
        menu = MainMenu(existing_uart=self.uart_conn, existing_notif_manager=self.notification_manager)
        menu.run()

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
