import time

import pygame
import sys
from settings import WIDTH, HEIGHT
from button import start_button, ports_button, quit_button, autoconnect_button, arrange_buttons, continue_button
from uart import UARTConnection
from snake_play_screen import SnakePlayScreen
import threading
from notification_manager import NotificationManager
from frame_codec import STMProtocol




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
        self.protocol = STMProtocol()



    def connect_to_stm(self):
        self.notification_manager.show("Виконується автопідключення до STM...", duration=3)
        connection_result = self.uart_conn.auto_connect()

        if connection_result["status"] == "success":
            connected_port = self.uart_conn.port
            ports_button.text = f"{connected_port}"
            self.notification_manager.show(connection_result['message'], duration=3)
            self.uart = True
        else:
            ports_button.text = "PORTS"
            self.notification_manager.show(connection_result['message'], duration=3)
            self.uart = False

        # Додаємо повторний виклик arrange_buttons після зміни тексту:
        arrange_buttons(ports_button, autoconnect_button, quit_button, WIDTH - 10, 50, 10)

    def run(self):
        """Головний цикл меню"""
        while self.running:
            self.handle_events()
            self.draw()
            pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

            if event.type == pygame.USEREVENT:
                if event.button == quit_button:
                    self.quit_game()
                elif event.button == start_button:
                    self.start_game()
                elif event.button == autoconnect_button:
                    # тут явно запускаємо автоконект
                    if self.uart_conn.uart and self.uart_conn.uart.is_open:
                        self.uart_conn.uart.close()
                    self.connect_to_stm()
                elif event.button == ports_button:
                    # тут викликаємо ручний вибір порту
                    self.notification_manager.show("Cкоро буде ...", duration=3)

            for btn in [start_button, ports_button, autoconnect_button, quit_button]:
                btn.handle_event(event)

    def show_ports_list(self):
        available_ports = self.uart_conn.create_dict_for_available_ports()

        print("Доступні COM-порти:")
        for port_num, device in sorted(available_ports.items()):
            print(f"{port_num}: {device}")

        try:
            port_number = int(input("Введіть номер порту: "))
            selected_port = available_ports.get(port_number, None)

            if selected_port:
                connection_result = self.uart_conn.check_port(selected_port)

                if connection_result["status"] == "success":
                    self.notification_manager.show(connection_result["message"], duration=3)
                    ports_button.text = selected_port.device  # Оновлюємо текст кнопки PORTS
                    self.uart = True
                else:
                    self.notification_manager.show(connection_result["message"], duration=3)
                    self.uart = False
            else:
                self.notification_manager.show("Порт не знайдено!", duration=3)

        except ValueError:
            self.notification_manager.show("Введіть число!", duration=3)


    def draw(self):
        """Малювання меню"""
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.background, (-400, -100))
        self.notification_manager.draw(self.screen)

        font = pygame.font.Font(None, 72)
        text_surface = font.render("Snake Game", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(WIDTH / 2, 100))
        self.screen.blit(text_surface, text_rect)

        for btn in [start_button, ports_button, autoconnect_button, quit_button]:
            btn.check_hover(pygame.mouse.get_pos())
            btn.draw(self.screen)

    def start_game(self):
        """Запуск гри, передача UART"""
        if not self.uart_conn:
            print("Немає підключення до STM! Гра неможлива.")
            pass
        if self.uart_conn:
            self.uart_conn.uart.write(self.protocol.encode_frame(3, 0))
            game = SnakePlayScreen(self.uart_conn, self)
            game.run()


    def quit_game(self):
        """Вихід з гри"""
        self.running = False
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    menu = MainMenu()
    menu.run()
