import pygame
import sys
from settings import WIDTH, HEIGHT
from button import start_button, settings_button, exit_button
from uart import UARTConnection
from snake_play_screen import SnakePlayScreen
import threading
from notification_manager import NotificationManager


class MainMenu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.background = pygame.image.load("assets/images/background1.png")
        self.notification_manager = NotificationManager()
        self.running = True
        self.uart_conn = UARTConnection()


        self.connect_thread = threading.Thread(target=self.connect_to_stm, daemon=True)
        self.connect_thread.start()

    def connect_to_stm(self):
        """Автоматично підключається до STM при запуску гри"""
        print("тест")
        self.notification_manager.show("Виконується автопідключення до STM...", duration=3)
        connection_result = self.uart_conn.auto_connect()

        if connection_result["status"] == "success":
            self.notification_manager.show(f"{connection_result['message']}", duration=3)

        else:
            self.notification_manager.show(f"{connection_result['message']}", duration=3)

    def run(self):
        """Головний цикл меню"""
        while self.running:
            self.handle_events()
            self.draw()
            pygame.display.flip()

    def handle_events(self):
        """Обробка подій"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

            if event.type == pygame.USEREVENT:
                if event.button == exit_button:
                    self.quit_game()
                elif event.button == start_button:
                    self.start_game()

            for btn in [start_button, settings_button, exit_button]:
                btn.handle_event(event)

    def draw(self):
        """Малювання меню"""
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.background, (-400, -100))
        self.notification_manager.draw(self.screen)

        font = pygame.font.Font(None, 72)
        text_surface = font.render("Snake Game", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(WIDTH / 2, 100))
        self.screen.blit(text_surface, text_rect)

        for btn in [start_button, settings_button, exit_button]:
            btn.check_hover(pygame.mouse.get_pos())
            btn.draw(self.screen)

    def start_game(self):
        """Запуск гри, передача UART"""
        if not self.uart_conn:
            print("⚠️ Немає підключення до STM! Гра неможлива.")
            return

        game = SnakePlayScreen(self.uart_conn)
        game.run()


    def quit_game(self):
        """Вихід з гри"""
        self.running = False
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    menu = MainMenu()
    menu.run()
