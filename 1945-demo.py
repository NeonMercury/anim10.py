#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import time
import pygame

from anim10 import new_animation, new_grid
from helpers import get_delta_time, process_events
from pygameframe import PyGameFrame

SCREEN_SIZE = (800, 600)


def main(argv):
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('anim10.py - 1945')

    image = pygame.image.load('media/1945.png')

    g32 = new_grid(PyGameFrame, 32, 32, 1024, 768, 3, 3, 1)

    spinning = [
        new_animation(g32('1-8', 1), 0.1),
        new_animation(g32(18, '8-11', 18, '10-7'), 0.2),
        new_animation(g32('1-8', 2), 0.3),
        new_animation(g32(19, '8-11', 19, '10-7'), 0.4),
        new_animation(g32('1-8', 3), 0.5),
        new_animation(g32(20, '8-11', 20, '10-7'), 0.6),
        new_animation(g32('1-8', 4), 0.7),
        new_animation(g32(21, '8-11', 21, '10-7'), 0.8),
        new_animation(g32('1-8', 5), 0.9),
    ]

    g64 = new_grid(PyGameFrame, 64, 64, 1024, 769, 299, 101, 2)

    plane = new_animation(g64(1, '1-3'), 0.1)
    seaplane = new_animation(g64('2-4', 3), 0.1)

    gs = new_grid(PyGameFrame, 32, 98, 1024, 768, 366, 102, 1)
    submarine = new_animation(gs('7-1', 1, '2-7', 1), {
        1: 1,
        '2-7': 0.1,
        8: 1,
        '9-13': 0.1,
    })

    terminated = False
    while not terminated:
        terminated = process_events()
        dt = get_delta_time()

        for spin in spinning:
            spin.update(dt)
        plane.update(dt)
        seaplane.update(dt)
        submarine.update(dt)

        screen.fill((0, 0, 0, 255))
        for i, spin in enumerate(spinning):
            spin.draw(screen, image, i * 75, i * 50)

        plane.draw(screen, image, 100, 400)
        seaplane.draw(screen, image, 250, 432)

        submarine.draw(screen, image, 600, 100)

        pygame.display.update()
        time.sleep(0.001)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
