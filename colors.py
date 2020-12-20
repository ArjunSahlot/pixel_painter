import pygame
import pickle
import os
from constants import *


class Colors:
    def __init__(self, x, y, width, height):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.path = os.path.join(PARDIR, "colors.painter")
        try:
            self.colors = pickle.load(open(self.path, "rb"))
        except FileNotFoundError:
            self.colors = []
        self.selected = None

    def update(self, window, events):
        if len(self.colors) != 0:
            height = self.height / len(self.colors)
        else:
            height = self.height
        self.draw(window, height)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i in range(len(self.colors)):
                    if pygame.Rect(self.x, self.y + i * height, self.width, height).collidepoint(event.pos):
                        self.selected = i
                        return self.colors[i]

    def draw(self, window, height):
        for i, color in enumerate(self.colors):
            pygame.draw.rect(window, color, (self.x, self.y + i * height, self.width, height))
        if self.selected is not None:
            pygame.draw.rect(window, BLACK, (self.x, self.y + self.selected * height, self.width, height), 5)

    def save(self):
        pickle.dump(self.colors, open(self.path, "wb"))