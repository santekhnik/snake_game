
import pygame
import sys
import threading
import time

from frame_codec import STMProtocol
from settings import WIDTH, HEIGHT, CELL_SIZE, GRID_WIDTH, GRID_HEIGHT, FIELD_OFFSET_X, FIELD_OFFSET_Y
from notification_manager import NotificationManager
from button import top_right_buttons



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
    }

    def __init__(self, uart_conn, main_menu):
        """Отримуємо підключення UART від головного меню"""
        self.uart_conn = uart_conn
        self.protocol = STMProtocol()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.running = True
        self.game_over = False
        self.clock = pygame.time.Clock()
        self.main_menu = main_menu  # Зберігаємо посилання на головне меню
        self.notification_manager = NotificationManager()

        self.snake_positions = []  # Координати змійки
        self.frog_position = (0, 0)  # Координати жабки

        # **Стартуємо потік для читання UART**
        self.uart_thread = threading.Thread(target=self.read_uart_data, daemon=True)
        self.uart_thread.start()
        self.uart_conn.uart.write(self.protocol.encode_frame(3, 0))
        self.score = 0
        self.pause = self.protocol.pause


    def read_uart_data(self):
        """Асинхронне отримання координат з UART, щоб не блокувати гру"""

        while self.running:
            data = self.uart_conn.read_packet()

            if data["status"] == "success":
                parsed_data = data["data"]
                if "payload" in parsed_data and "frog" in parsed_data:
                    self.snake_positions = parsed_data["payload"]
                    self.frog_position = parsed_data["frog"]
                    self.score = max(len(self.snake_positions) - 4, 0)  # Оновлюємо очки, мінімум 0
                    print(f"📩 Отримано дані: {parsed_data}")

                elif parsed_data["status"] == "end":  # ✅ Перевіряємо тільки коли гра реально йде
                    print("🟥 GAME OVER!")
                    self.game_over = True
                    print("⚡ Викликаємо show_game_over_banner()")

            time.sleep(0.1)  # Маленька затримка для зменшення навантаження


    def run(self):
        """Головний цикл гри"""
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(10)  # FPS

    def draw(self):
        """Малювання гри"""

        self.screen.fill(self.GRAY)
        self.draw_grid()
        self.draw_snake()
        self.draw_frog()

        # Відображення рахунку біля правого краю поля
        font_small = pygame.font.Font(None, 50)
        score_text = font_small.render(f"Score: {self.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(midleft=(FIELD_OFFSET_X + GRID_WIDTH * CELL_SIZE + 20, HEIGHT // 2))

        self.screen.blit(score_text, score_rect)  # Додаємо рахунок біля поля

        if self.game_over:
            self.draw_game_over_banner()


        for button in top_right_buttons:
            button.draw(self.screen)

        pygame.display.flip()

    def draw_game_over_banner(self):
        """Просто малює банер GAME OVER з кнопками"""
        font = pygame.font.Font(None, 200)
        text_game_over = font.render("GAME OVER", True, (255, 0, 0))
        rect_game_over = text_game_over.get_rect(center=(WIDTH // 2, HEIGHT // 3))

        new_game_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 1.5, 200, 50)
        menu_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 1.3, 200, 50)

        self.screen.blit(text_game_over, rect_game_over)

        pygame.draw.rect(self.screen, (0, 255, 0), new_game_button)
        pygame.draw.rect(self.screen, (255, 255, 0), menu_button)

        font_button = pygame.font.Font(None, 40)
        text_new_game = font_button.render("NEW GAME", True, (0, 0, 0))
        text_menu = font_button.render("MENU", True, (0, 0, 0))

        self.screen.blit(text_new_game, new_game_button.move(20, 10))
        self.screen.blit(text_menu, menu_button.move(50, 10))

        # Відображення очок
        font_small = pygame.font.Font(None, 100)
        text_score = font_small.render(f"Score: {self.score}", True, (255, 255, 255))
        rect_score = text_score.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        self.screen.blit(text_game_over, rect_game_over)
        self.screen.blit(text_score, rect_score)  # Додаємо рахунок

    def handle_events(self):
        """Обробка подій клавіатури та кнопок"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

            if self.game_over:
                new_game_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 1.5, 200, 50)
                menu_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 1.3, 200, 50)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if new_game_button.collidepoint(event.pos):
                        print("🟢 NEW GAME натиснуто")
                        self.game_over = False
                        self.uart_conn.uart.write(self.protocol.encode_frame(3, 0))

                    if menu_button.collidepoint(event.pos):
                        print("🟡 MENU натиснуто")
                        self.game_over = False
                        self.running = False
                        self.main_menu.run()
                continue

            mouse_pos = pygame.mouse.get_pos()
            for button in top_right_buttons:
                button.check_hover(mouse_pos)
                button.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:

                    if not self.protocol.pause:
                        self.uart_conn.uart.write(self.protocol.encode_frame(3,5))

                    else:
                        self.uart_conn.uart.write(self.protocol.encode_frame(3,5))

                    print(f"⏸ Пауза: {self.protocol.pause}")
                elif event.key in self.KEY_MAP:

                    command = self.KEY_MAP[event.key]
                    self.send_command_to_stm(command)

            if event.type == pygame.USEREVENT:
                if event.button.text == "Х":
                    self.quit_game()

                elif event.button.text == "MENU":
                    if self.protocol.pause:
                        self.uart_conn.uart.write(self.protocol.encode_frame(3,5))
                    else:
                        print("⏸ Ставимо гру на паузу через кнопку MENU", self.protocol.pause)
                        self.uart_conn.uart.write(self.protocol.encode_frame(3,5))



                    confirm = self.confirm_exit_to_menu()
                    if confirm:
                        self.running = False
                        self.main_menu.run()
                    else:
                        print("↩️ Вихід скасовано — повертаємося в гру")

    def confirm_exit_to_menu(self):
        """Виводить підтвердження перед виходом у меню"""
        font = pygame.font.Font(None, 60)
        text = font.render("Do you really want to exit to menu?", True, (255, 255, 255))
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 3))

        yes_button = pygame.Rect(WIDTH // 2 - 110, HEIGHT // 2, 100, 50)
        no_button = pygame.Rect(WIDTH // 2 + 10, HEIGHT // 2, 100, 50)

        while True:
            self.screen.fill((30, 30, 30))
            self.screen.blit(text, rect)

            pygame.draw.rect(self.screen, (0, 255, 0), yes_button)
            pygame.draw.rect(self.screen, (255, 0, 0), no_button)

            font_btn = pygame.font.Font(None, 40)
            yes_text = font_btn.render("YES", True, (0, 0, 0))
            no_text = font_btn.render("NO", True, (0, 0, 0))
            self.screen.blit(yes_text, yes_button.move(25, 10))
            self.screen.blit(no_text, no_button.move(30, 10))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if yes_button.collidepoint(event.pos):
                        return True
                    if no_button.collidepoint(event.pos):
                        return False


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

