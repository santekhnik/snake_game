import pygame
import sys
from settings import WIDTH, HEIGHT
from button import start_button, settings_button, exit_button

pygame.init()


def main_menu():
    main_background = pygame.image.load("assets/images/background1.png")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    running = True
    while running:
        screen.fill((0, 0, 0,))

        # Додаємо фон

        screen.blit(main_background, (-400, -100))

        font = pygame.font.Font(None, 72)
        text_surface = font.render("Snake Game", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(WIDTH / 2, 100))
        screen.blit(text_surface, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.USEREVENT and event.button == exit_button:
                running = False
                pygame.quit()
                sys.exit()

            for btn in [start_button, settings_button, exit_button]:
                btn.handle_event(event)

        for btn in [start_button, settings_button, exit_button]:
            btn.check_hover(pygame.mouse.get_pos())
            btn.draw(screen)

        pygame.display.flip()
