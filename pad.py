#
#  Pixel painter
#  A pygame gui that helps you draw in a certain resolution and export as png.
#  Copyright Arjun Sahlot 2021
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import pygame
from constants import *


class Pad:
    def __init__(self, rect):
        self.rect = rect
        self.resolution = [16, 16]
        self.colors = [[WHITE for _ in range(self.resolution[0])] for _ in range(self.resolution[1])]
        self.surface = pygame.Surface(rect[2:], pygame.SRCALPHA)

    def update(self, window, picker, events):
        width = self.rect[2] / self.resolution[0]
        height = self.rect[3] / self.resolution[1]
        start_x, start_y = self.rect[:2]
        self.draw(window, width, height, start_x, start_y)
        x, y = pygame.mouse.get_pos()
        if self.rect[0] < x < self.rect[0] + self.rect[2] and self.rect[1] < y < self.rect[1] + self.rect[3]:
            row = int((y - start_y) / (self.rect[3] / self.resolution[1]))
            col = int((x - start_x) / (self.rect[2] / self.resolution[0]))
            if pygame.mouse.get_pressed()[0]:
                self.colors[row][col] = picker
            elif pygame.mouse.get_pressed()[2]:
                self.colors[row][col] = WHITE
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                    return self.colors[row][col]

    def update_res(self, res):
        self.resolution = res
        self.colors = [[WHITE for _ in range(self.resolution[0])] for _ in range(self.resolution[1])]

    def draw(self, window, width, height, start_x, start_y):
        for i, row in enumerate(self.colors):
            for j, color in enumerate(row):
                pygame.draw.rect(self.surface, color, (j * width, i * height, width, height))

        window.blit(self.surface, self.rect[:2])

        if self.resolution[0] <= 100 and self.resolution[1] <= 100:
            for col in range(self.resolution[0] + 1):
                pygame.draw.line(window, BLACK, (start_x + col * width, start_y), (start_x + col * width, start_y + self.rect[3]))
            for row in range(self.resolution[1] + 1):
                pygame.draw.line(window, BLACK, (start_x, start_y + row * height), (start_x + self.rect[2], start_y + row * height))

    def export(self, path, window, picker, trans, res, events):
        if trans:
            for i in range(len(self.colors)):
                for j in range(len(self.colors[i])):
                    if sum(self.colors[i][j]) > 250*3:
                        self.colors[i][j] = (0, 0, 0, 0)
            self.update(window, picker, events)
        try:
            if res:
                pygame.image.save(pygame.transform.scale(self.surface, self.resolution), path)
            else:
                pygame.image.save(self.surface, path)
        except TypeError:
            pass
