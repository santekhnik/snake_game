import pygame
import time


class NotificationManager:
    """Менеджер сповіщень у грі"""

    FONT_COLOR = (0, 255, 0)  # Зелений колір тексту
    BG_COLOR = (46, 46, 46)  # Темно-сірий фон

    def __init__(self):
        self.notifications = []  # Список активних сповіщень
        self.font = pygame.font.Font(None, 25)  # Шрифт сповіщень

    def show(self, message, duration=2):
        """Додає сповіщення, яке зникне через duration секунд"""
        self.notifications.append({"message": message, "start_time": time.time(), "duration": duration})

    def draw(self, screen):
        """Малює сповіщення на екрані"""
        current_time = time.time()
        self.notifications = [n for n in self.notifications if current_time - n["start_time"] < n["duration"]]

        for index, notification in enumerate(self.notifications):
            text_surface = self.font.render(notification["message"], True, self.FONT_COLOR)
            text_rect = text_surface.get_rect(center=(screen.get_width() // 6, 40 + index * 25))

            pygame.draw.rect(screen, self.BG_COLOR, text_rect.inflate(20, 10))
            screen.blit(text_surface, text_rect)


