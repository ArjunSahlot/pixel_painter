import pygame
from constants import *
from elements import *
from pad import Pad
from colors import Colors


# Window Management
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Painter")


def main(window):
    pygame.init()
    clock = pygame.time.Clock()
    pad = Pad((50, 50, 800, 800))
    picker = ColorPicker((900, 500), 150, (1210, 500), (50, 300), False, False, 5, (900, 810), (360, 50))
    colors = Colors(1330, 500, 225, 360)
    surf = pygame.Surface((50, 50), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.rect(surf, WHITE, (19, 5, 12, 40))
    pygame.draw.rect(surf, WHITE, (5, 19, 40, 12))
    button = ImgButton(1265, 500, 50, 50, surf)
    color = picker.get_rgb()

    while True:
        clock.tick(FPS)
        window.fill(WHITE)
        events = pygame.event.get()
        pad.update(window, color)
        if picker.update(window):
            colors.selected = None
            color = picker.get_rgb()
        if (curr_col := colors.update(window, events)) is not None:
            color = curr_col
        if button.update(window, events):
            if len(colors.colors) < 20:
                colors.colors.append(picker.get_rgb())
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        pygame.display.update()


main(WINDOW)
