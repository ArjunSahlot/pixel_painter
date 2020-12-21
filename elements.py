import pygame
import numpy as np
from colorsys import rgb_to_hsv, hsv_to_rgb
import os
from constants import *
pygame.init()


class ColorPicker:
    def __init__(self, wheel_pos, wheel_rad, slider_pos, slider_size, slider_horiz, slider_invert, cursor_rad, display_rect_loc, display_rect_size=(150, 150)):
        self.wheel_pos, self.wheel_rad = wheel_pos, wheel_rad
        self.slider_pos, self.slider_size, self.slider_horiz, self.slider_invert = slider_pos, slider_size, slider_horiz, slider_invert
        self.cursor_rad = cursor_rad
        self.display_rect_loc, self.display_rect_size = display_rect_loc, display_rect_size
        self.wheel_cursor, self.slider_cursor = np.array((wheel_rad,)*2), np.array((slider_size[0]//2, 1))
        self.slider_surf = pygame.Surface(slider_size)
        self.wheel_surf = pygame.transform.scale(
            pygame.image.load(os.path.join(os.path.realpath(os.path.dirname(__file__)), "assets", "color_picker.png")), (wheel_rad * 2,) * 2)
        self.cursor_surf = pygame.Surface((self.cursor_rad*2,)*2, pygame.SRCALPHA)
        self.wheel_darken = pygame.Surface((wheel_rad * 2,) * 2, pygame.SRCALPHA)
        self._create_wheel()
        self._create_slider()
        self.update_wheel()

    def draw(self, window):
        pygame.draw.rect(window, self.get_rgb(), (*self.display_rect_loc, *self.display_rect_size))
        window.blit(self.slider_surf, self.slider_pos)
        self._draw_cursor(window, np.array(self.slider_pos) + np.array(self.slider_cursor))
        window.blit(self.wheel_surf, self.wheel_pos)
        window.blit(self.wheel_darken, self.wheel_pos)
        self._draw_cursor(window, np.array(self.wheel_pos) + np.array(self.wheel_cursor))

    def update(self, window):
        self.draw(window)
        if any(pygame.mouse.get_pressed()):
            x, y = pygame.mouse.get_pos()
            if ((self.wheel_pos[0] + self.wheel_rad - x) ** 2 + (self.wheel_pos[1] + self.wheel_rad - y) ** 2)**0.5 < self.wheel_rad - 2:
                self.wheel_cursor = (x - self.wheel_pos[0], y - self.wheel_pos[1]) if pygame.mouse.get_pressed()[0] else (self.wheel_rad,)*2
                return True
            elif self.slider_pos[0] < x < self.slider_pos[0] + self.slider_size[0] and self.slider_pos[1] < y < self.slider_pos[1] + self.slider_size[1]:
                self.slider_cursor[1] = y - self.slider_pos[1] if pygame.mouse.get_pressed()[0] else 1
                self.update_wheel()
                return True

    def get_rgb(self):
        wrgb = self.wheel_surf.get_at(self.wheel_cursor)
        srgb = self.slider_surf.get_at(self.slider_cursor)
        whsv = rgb_to_hsv(*(np.array(wrgb)/255)[:3])
        shsv = rgb_to_hsv(*(np.array(srgb)/255)[:3])
        hsv = (whsv[0], whsv[1], shsv[2])
        rgb = np.array(hsv_to_rgb(*hsv))*255
        return rgb

    def get_hsv(self):
        rgb = (np.array(self.get_rgb())/255)[:3]
        return np.array(rgb_to_hsv(*rgb))*255

    def update_wheel(self):
        pygame.draw.circle(self.wheel_darken, (0, 0, 0, np.interp(
            self.get_hsv()[2], (0, 255), (255, 0))), (self.wheel_rad,)*2, self.wheel_rad)

    def _create_wheel(self):
        pygame.draw.circle(self.wheel_surf, (0, 0, 0),
                           (self.wheel_rad,)*2, self.wheel_rad, 2)

    def _create_slider(self):
        w, h = self.slider_size
        if self.slider_horiz:
            for x in range(w):
                if self.slider_invert:
                    value = np.interp(x, (0, w), (0, 255))
                else:
                    value = np.interp(x, (0, w), (255, 0))
                pygame.draw.rect(self.slider_surf, (value,)*3, (x, 0, 1, h))

        else:
            for y in range(h):
                if self.slider_invert:
                    value = np.interp(y, (0, h), (0, 255))
                else:
                    value = np.interp(y, (0, h), (255, 0))
                pygame.draw.rect(self.slider_surf, (value,)*3, (0, y, w, 1))
        pygame.draw.rect(self.slider_surf, (0, 0, 0), (0, 0, w, h), 1)

    def _draw_cursor(self, window, pos):
        pygame.draw.circle(window, (255, 255, 255), pos, self.cursor_rad)
        pygame.draw.circle(window, (0, 0, 0), pos, self.cursor_rad, 2)


class TextInput:
    def __init__(self,
                 loc,
                 size,
                 bg_col,
                 border_width=5,
                 border_col=(0, 0, 0),
                 initial_text="",
                 label="",
                 font=pygame.font.SysFont("comicsans", 35),
                 text_col=(0, 0, 0),
                 cursor_col=(0, 0, 1),
                 repeat_initial=400,
                 repeat_interval=35,
                 max_len=-1,
                 password=False,
                 editing=False):

        self.password_field = password

        self.loc, self.size = loc, size

        self.editing = editing

        self.text_col = text_col
        self.password = password
        self.text = initial_text
        self.label = label
        self.max_len = max_len

        self.rect = pygame.Rect(*loc, *size)
        self.bg_col = bg_col
        self.border_col, self.border_width = border_col, border_width

        self.font = font

        self.surface = pygame.Surface((1, 1))
        self.surface.set_alpha(0)

        self.key_repeat_counters = {}
        self.key_repeat_initial = repeat_initial
        self.key_repeat_interval = repeat_interval

        self.cursor_surf = pygame.Surface(
            (int(font.get_height() / 20 + 1), font.get_height()))
        self.cursor_surf.fill(cursor_col)
        self.cursor_pos = len(initial_text)
        self.cursor_visible = True
        self.cursor_switch = 500
        self.cursor_counter = 0

        self.clock = pygame.time.Clock()

    def draw(self, window, events):
        pygame.draw.rect(window, self.bg_col, self.rect)
        if self.border_width:
            pygame.draw.rect(window, self.border_col,
                             self.rect, self.border_width)

        text_pos = (int(self.loc[0] + self.size[0]//2 - self.surface.get_width()/2),
                   int(self.loc[1] + self.size[1]//2 - self.surface.get_height()/2))
        window.blit(self.surface, text_pos)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.editing = True
                else:
                    self.editing = False

            if not self.text:
                self.password = False
                self.text = self.label

            if self.editing and self.text == self.label:
                self.clear_text()
                self.password = True if self.password_field else False

            if event.type == pygame.KEYDOWN:
                self.cursor_visible = True

                if event.key not in self.key_repeat_counters:
                    if not event.key == pygame.K_RETURN:
                        self.key_repeat_counters[event.key] = [0, event.unicode]

                if self.editing:
                    if event.key == pygame.K_BACKSPACE:
                        self.text = (
                                self.text[:max(self.cursor_pos - 1, 0)]
                            + self.text[self.cursor_pos:]
                        )

                        self.cursor_pos = max(self.cursor_pos - 1, 0)
                    elif event.key == pygame.K_DELETE:
                        self.text = (
                                self.text[:self.cursor_pos]
                            + self.text[self.cursor_pos + 1:]
                        )

                    elif event.key == pygame.K_RETURN:
                        return True

                    elif event.key == pygame.K_RIGHT:
                        self.cursor_pos = min(
                            self.cursor_pos + 1, len(self.text))

                    elif event.key == pygame.K_LEFT:
                        self.cursor_pos = max(self.cursor_pos - 1, 0)

                    elif event.key == pygame.K_END:
                        self.cursor_pos = len(self.text)

                    elif event.key == pygame.K_HOME:
                        self.cursor_pos = 0

                    elif len(self.text) < self.max_len or self.max_len == -1:
                        self.text = (
                                self.text[:self.cursor_pos]
                            + event.unicode
                            + self.text[self.cursor_pos:]
                        )
                        self.cursor_pos += len(event.unicode)

            elif event.type == pygame.KEYUP:
                if event.key in self.key_repeat_counters:
                    del self.key_repeat_counters[event.key]

        for key in self.key_repeat_counters:
            self.key_repeat_counters[key][0] += self.clock.get_time()

            if self.key_repeat_counters[key][0] >= self.key_repeat_initial:
                self.key_repeat_counters[key][0] = (
                    self.key_repeat_initial
                    - self.key_repeat_interval
                )

                event_key, event_unicode = key, self.key_repeat_counters[key][1]
                pygame.event.post(pygame.event.Event(
                    pygame.KEYDOWN, key=event_key, unicode=event_unicode))

        string = self.text
        if self.password:
            string = "*" * len(self.text)
        if self.text:
            self.surface = self.font.render(str(string), 1, self.text_col)
        else:
            self.surface = pygame.Surface(self.cursor_surf.get_size(), pygame.SRCALPHA)
            self.surface.fill((0, 0, 0, 0))

        self.cursor_counter += self.clock.get_time()
        if self.cursor_counter >= self.cursor_switch:
            self.cursor_counter %= self.cursor_switch
            self.cursor_visible = not self.cursor_visible

        if self.cursor_visible:
            cursor_y = self.font.size(self.text[:self.cursor_pos])[0]
            if self.cursor_pos > 0:
                cursor_y -= self.cursor_surf.get_width()
            if self.editing:
                self.surface.blit(self.cursor_surf, (cursor_y, 0))

        self.clock.tick()
        return False

    def get_cursor_pos(self):
        return self.cursor_pos

    def set_text_color(self, color):
        self.text_col = color

    def set_cursor_color(self, color):
        self.cursor_surf.fill(color)

    def clear_text(self):
        self.text = ""
        self.cursor_pos = 0

    def __repr__(self):
        return self.text


class ImgButton:
    bg = (110, 110, 110)
    hover = (130, 130, 130)

    def __init__(self, x, y, width, height, image, paddingx=3, paddingy=3):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.image = pygame.transform.scale(image, (width - paddingx*2, height - paddingy*2))

    def update(self, window, events):
        x, y = pygame.mouse.get_pos()
        clicked = False
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = pygame.Rect(self.x, self.y, self.width, self.height).collidepoint(x, y)

        color = self.bg
        if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height and not clicked:
            color = self.hover
        pygame.draw.rect(window, color, (self.x, self.y, self.width, self.height))
        window.blit(self.image, (self.x + self.width/2 - self.image.get_width()/2, self.y + self.height/2 - self.image.get_height()/2))
        
        return clicked


class Check:
    width = height = 50

    def __init__(self, x, y, text):
        self.x, self.y = x, y
        self.checked = True
        self.surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.surf.fill((0, 0, 0, 0))
        pygame.draw.polygon(self.surf, BLACK, [(9.7, 19.8), (3.4, 29.3), (21.5, 38.2), (45.3, 16.4), (38.6, 9.9), (22.5, 26.9)])
        self.text = text

    def update(self, window, events):
        self.draw(window)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(self.x, self.y, self.width, self.height).collidepoint(event.pos):
                    self.checked = not self.checked

    def draw(self, window):
        text_surf = pygame.font.SysFont("comicsans", self.height - 8).render(self.text, 1, BLACK)
        pygame.draw.rect(window, BLACK, (self.x, self.y, self.width, self.height), 5)
        if self.checked:
            window.blit(self.surf, (self.x, self.y))
        window.blit(text_surf, (self.x + self.width + 8, self.y + self.height/2 - text_surf.get_height()/2))
