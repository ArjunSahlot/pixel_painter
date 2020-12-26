import pygame
from constants import *
from elements import *
from pad import Pad
from colors import Colors
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter import Tk
Tk().withdraw()

# Window Management
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Painter")


def on_import(rows, cols, path, pad):
    width, height = cols, rows
    image = pygame.transform.scale(pygame.image.load(path), (width, height))
    for row in range(rows):
        for col in range(cols):
            pad.colors[row][col] = image.get_at((col, row))
    
    return path.split("/")[-1]


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
    row_res = TextInput((900, 50), (250, 50), WHITE, label="Row resolution", max_len=3)
    col_res = TextInput((900, 125), (250, 50), WHITE, label="Column resolution", max_len=3)
    export = ImgButton(1250, 50, 300, 80, pygame.font.SysFont("comicsans", 100).render("Export", 1, BLACK), 25, 5)
    imp = ImgButton(925, 330, 200, 70, pygame.font.SysFont("comicsans", 100).render("Import", 1, BLACK), 15, 5)
    update = ImgButton(950, 200, 150, 50, pygame.font.SysFont("comicsans", 100).render("Update", 1, BLACK), 10, 5)
    trans = Check(1225, 140, "White as transparent")
    res = Check(1250, 200, f"Export as {'x'.join(list(map(str, pad.resolution)))}")
    import_name = "No file imported"

    while True:
        clock.tick(FPS)
        window.fill(WHITE)
        events = pygame.event.get()
        if (pad_update := pad.update(window, color, events)) is not None:
            if len(colors.colors) < 20:
                colors.colors.append(pad_update)
                colors.selected = len(colors.colors) - 1
            color = pad_update
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
            colors.selected = 0
        try:
            if row_res.draw(window, events) or col_res.draw(window, events) or update.update(window, events):
                pad.update_res([int(col_res.text), int(row_res.text)])
        except ValueError:
            pass
        if export.update(window, events):
            pad.export(asksaveasfilename(), window, color, trans.checked, res.checked, events)
        trans.update(window, events)
        res.update(window, events)
        if imp.update(window, events):
            try:
                import_name = on_import(int(row_res.text), int(col_res.text), askopenfilename(), pad)
            except (ValueError, pygame.error, TypeError):
                pass

        text = pygame.font.SysFont("comicsans", 50).render(import_name, 1, BLACK)
        window.blit(text, (imp.x + imp.width + 10, imp.y + imp.height/2 - text.get_height()/2))
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                colors.save()
                return
        pygame.display.update()


main(WINDOW)
