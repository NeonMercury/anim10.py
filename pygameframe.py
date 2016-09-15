# -*- coding: utf-8 -*-
import pygame

from anim10 import Frame


class PyGameFrame(Frame):
    def create_frame(self, width, height):
        return pygame.Surface((width, height))

    def draw(self, canvas, image, x, y):
        rect = (self.x, self.y, self.width, self.height)
        self.quad.blit(image, (0, 0), rect)

        canvas.blit(self.quad, (x, y))
