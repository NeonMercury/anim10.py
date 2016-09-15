#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum
import sys
import time
import pygame

from anim10 import Animation, Grid, Frame
from helpers import get_delta_time, process_events
from pygameframe import PyGameFrame

SCREEN_SIZE = (800, 600)


def display_text(canvas, message, x, y):
    font = pygame.font.SysFont('Courier New', 12)
    if len(message) > 0:
        canvas.blit(font.render(message, 1, (255, 255, 255)), (x, y))


class MoveDirection(Enum):
    left = 0
    right = 1
    up = 2
    down = 3


def main(argv):
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('anim10.py - witch')

    canvas = pygame.Surface((400, 300))
    player_x = canvas.get_width() // 2 - 16
    player_y = canvas.get_height() // 2 - 16
    player_speed = 100

    image = pygame.image.load('media/witch.png')

    grid = Grid(PyGameFrame, 32, 32, 384, 256)

    move = {
        MoveDirection.down: Animation(grid('1-3', 1, 2, 1), 0.15),
        MoveDirection.up: Animation(grid('1-3', 4, 2, 4), 0.15),
        MoveDirection.left: Animation(grid('1-3', 2, 2, 2), 0.15),
        MoveDirection.right: Animation(grid('1-3', 3, 2, 3), 0.15),
    }

    last_direction = MoveDirection.down

    terminated = False
    while not terminated:
        terminated = process_events()
        dt = get_delta_time()

        keyboard_state = pygame.key.get_pressed()

        moving = False

        if keyboard_state[pygame.K_UP]:
            last_direction = MoveDirection.up
            moving = True

        if keyboard_state[pygame.K_DOWN]:
            last_direction = MoveDirection.down
            moving = True

        if keyboard_state[pygame.K_LEFT]:
            last_direction = MoveDirection.left
            moving = True

        if keyboard_state[pygame.K_RIGHT]:
            last_direction = MoveDirection.right
            moving = True

        if moving:
            move[last_direction].update(dt)

            if last_direction == MoveDirection.down:
                player_y += player_speed * dt
            elif last_direction == MoveDirection.up:
                player_y -= player_speed * dt
            elif last_direction == MoveDirection.left:
                player_x -= player_speed * dt
            elif last_direction == MoveDirection.right:
                player_x += player_speed * dt

        screen.fill((0, 0, 0, 255))
        canvas.fill((0, 0, 0, 255))

        move[last_direction].draw(canvas, image, player_x, player_y)

        display_text(canvas, 'Press up/down/left/right arrows', 10, 10)
        display_text(canvas, 'to control the witch.', 10, 30)

        output = pygame.transform.scale(canvas, SCREEN_SIZE)
        screen.blit(output, (0, 0))

        pygame.display.update()
        time.sleep(0.001)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
