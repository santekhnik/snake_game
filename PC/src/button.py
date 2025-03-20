import pygame
from settings import WIDTH

pygame.mixer.init()

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


# Центрована кнопка "NEW GAME"
start_button = ImageButton(
    WIDTH / 2 - (252 / 2), 515, 252, 60,
    "NEW GAME",
    "assets/images/greenNormal.png",
    "assets/images/greenDown.png",
    "assets/sound_effects/click.mp3.mp3"
)

""""
# Кнопка "PORTS" у правому верхньому куті
settings_button = ImageButton(
    WIDTH - 252 + 170,  # x = ширина екрана - ширина кнопки - відступ
    15,                # y = відступ зверху
    75, 75,
    "",
    "assets/images/settings_button.png",
    "",
    "assets/sound_effects/click.mp3.mp3"
)
"""
# Центрована кнопка "EXIT"
exit_button = ImageButton(
    WIDTH / 2 - (252 / 2), 600, 252, 60,
    "EXIT",
    "assets/images/redNormal.png",
    "assets/images/redDown.png",
    "assets/sound_effects/click.mp3.mp3"
)

back_button = ImageButton(
    WIDTH - 252 + 170,  # x = ширина екрана - ширина кнопки - відступ
    15,                # y = відступ зверху
    80, 60,
    "BACK",
    "assets/images/yellowNormal.png",
    "",
    "assets/sound_effects/click.mp3.mp3"

)