# -*- coding: utf-8 -*-
import time
import pygame


def process_events():
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            return True
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                return True
    return False


def get_delta_time():
    if not hasattr(get_delta_time, 'timestamp'):
        setattr(get_delta_time, 'timestamp', time.time())

    timestamp = getattr(get_delta_time, 'timestamp')

    current_timestamp = time.time()
    dt = current_timestamp - timestamp

    setattr(get_delta_time, 'timestamp', current_timestamp)

    return dt
