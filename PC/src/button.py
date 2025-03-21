import pygame
from settings import WIDTH

pygame.mixer.init()
pygame.font.init()

class ImageButton:
    def __init__(self, x, y, width, height, text, image_path, hover_image_path=None, sound_path=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.hover_image = self.image
        if hover_image_path:
            self.hover_image = pygame.image.load(hover_image_path)
            self.hover_image = pygame.transform.scale(self.hover_image, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.sound = None
        if sound_path:
            print(sound_path)
            self.sound = pygame.mixer.Sound(sound_path)
        self.is_hovered = False

    # Метод реалізації кнопки
    def draw(self, screen):
        current_image = self.hover_image if self.is_hovered else self.image
        screen.blit(current_image, self.rect.topleft)

        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    # Перевіряємо чи наведена нашa мишка на об'єкт
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.sound:
                self.sound.play()
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, button=self))


class CircleButton:
    def __init__(self, x, y, radius, text, color, hover_color, sound_path=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.sound = pygame.mixer.Sound(sound_path) if sound_path else None
        self.is_hovered = False

    def draw(self, screen):
        current_color = self.hover_color if self.is_hovered else self.color
        font = pygame.font.Font(None, 28)
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_width = text_surface.get_width()

        min_width = self.radius * 2
        padding = 10
        total_width = getattr(self, 'width', max(min_width, text_width + 2 * padding))

        if total_width > min_width:
            left_x = self.x - total_width // 2
            right_x = self.x + total_width // 2
            pygame.draw.circle(screen, current_color, (left_x, self.y), self.radius)
            pygame.draw.circle(screen, current_color, (right_x, self.y), self.radius)
            pygame.draw.rect(screen, current_color, (left_x, self.y - self.radius, total_width, self.radius * 2))
        else:
            pygame.draw.circle(screen, current_color, (self.x, self.y), self.radius)

        # Малюємо текст строго по центру кнопки
        text_rect = text_surface.get_rect(center=(self.x, self.y))
        screen.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        """Перевіряє, чи наведена миша"""
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        self.is_hovered = dx * dx + dy * dy <= self.radius * self.radius

    def handle_event(self, event):
        """Обробляє кліки"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.sound:
                self.sound.play()
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, button=self))

def arrange_buttons(ports_button, auto_button, quit_button, start_x, y, spacing):
    font = pygame.font.Font(None, 28)

    # ширини текстів
    ports_text_width = font.render(ports_button.text, True, (255, 255, 255)).get_width()
    auto_text_width = font.render(auto_button.text, True, (255, 255, 255)).get_width()

    padding = 20

    ports_width = ports_text_width + 2 * padding
    auto_width = auto_text_width + 2 * padding

    # позиція QUIT справа
    quit_button.x = start_x - quit_button.radius

    # AUTO — лівіше від QUIT
    auto_button.x = quit_button.x - quit_button.radius - spacing - auto_width // 2

    # PORTS — лівіше від AUTO
    ports_button.x = auto_button.x - auto_width // 2 - spacing - ports_width // 2

    # встановлюємо ширини (для малювання)
    ports_button.dynamic_width = ports_width
    auto_button.dynamic_width = auto_width

    menu_button.x = autoconnect_button.x
    menu_button.y = autoconnect_button.y


BUTTON_RADIUS = 30
BUTTON_SPACING = 20
START_X = WIDTH - 20

ports_button = CircleButton(0, 50, BUTTON_RADIUS, "PORTS", (50, 50, 50), (100, 100, 100))
autoconnect_button = CircleButton(0, 50, BUTTON_RADIUS, "AUTO", (0, 200, 0), (0, 255, 0))
menu_button = CircleButton(0, 50, BUTTON_RADIUS, "MENU", (0, 100, 255), (0, 150, 255))
quit_button = CircleButton(0, 50, BUTTON_RADIUS, "Х", (200, 0, 0), (255, 0, 0))

arrange_buttons(ports_button, autoconnect_button, quit_button, START_X, 50, BUTTON_SPACING)

top_right_buttons = [menu_button, quit_button]


# Центрована кнопка "NEW GAME"
start_button = ImageButton(
    WIDTH / 2 - (252 / 2), 515, 252, 60,
    "NEW GAME",
    "assets/images/greenNormal.png",
    "assets/images/greenDown.png",
    "assets/sound_effects/click.mp3.mp3"
)

continue_button = ImageButton(
    WIDTH / 2 - (252 / 2), 590, 252, 60,
    "CONTINUE",
    "assets/images/yellowNormal.png",
    "assets/images/yellowDown.png",
    "assets/sound_effects/click.mp3.mp3"
)
