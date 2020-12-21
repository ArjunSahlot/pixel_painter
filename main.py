import pygame
from constants import *
from elements import *
from pad import Pad
from colors import Colors
from tkinter.filedialog import asksaveasfilename


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
    pygame.draw.rect(surf, WHITE, (5, 19, 40, 12))
    minus = ImgButton(1265, 565, 50, 50, surf)
    pygame.draw.rect(surf, WHITE, (19, 5, 12, 40))
    plus = ImgButton(1265, 500, 50, 50, surf)
    color = picker.get_rgb()
    row_res = TextInput((900, 50), (250, 50), WHITE, label="Row resolution", max_len=2)
    col_res = TextInput((900, 125), (250, 50), WHITE, label="Column resolution", max_len=2)
    export = ImgButton(1250, 50, 300, 80, pygame.font.SysFont("comicsans", 100).render("Export", 1, BLACK), 25, 5)
    update = ImgButton(950, 200, 150, 50, pygame.font.SysFont("comicsans", 100).render("Update", 1, BLACK), 25, 5)
    trans = Check(1225, 140, "White as transparent")
    res = Check(1225, 200, f"Export as {'x'.join(list(map(str, pad.resolution)))}")

    while True:
        clock.tick(FPS)
        window.fill(WHITE)
        events = pygame.event.get()
        pad.update(window, color)
        res.text = f"Export as {'x'.join(list(map(str, pad.resolution)))}"
        if picker.update(window):
            colors.selected = None
            color = picker.get_rgb()
        if (curr_col := colors.update(window, events)) is not None:
            color = curr_col
        if plus.update(window, events):
            if len(colors.colors) < 20:
                colors.colors.append(picker.get_rgb())
        if colors.selected is not None and minus.update(window, events):
            colors.colors.pop(colors.selected)
            colors.selected = None
        try:
            if row_res.draw(window, events) or col_res.draw(window, events) or update.update(window, events):
                pad.update_res([int(col_res.text), int(col_res.text)])
        except ValueError:
            pass
        if export.update(window, events):
            pad.export(asksaveasfilename(), window, color, trans.checked, res.checked)
        trans.update(window, events)
        res.update(window, events)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                colors.save()
                return
        pygame.display.update()


main(WINDOW)
