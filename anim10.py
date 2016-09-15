# -*- coding: utf-8 -*-
"""An animation library for python.

"""
from enum import Enum
import math
import re

__version__ = '2.3.0'
__author__ = 'Eremin Dmitry (mail@eremindmitry.ru)'


_NUMBER_TYPES = (int, float)


class Status:
    """Describes animation status.

    Attributes:
        playing (int): The animation is playing now.
        paused (int): The animation is not playing now.

    """
    playing = 0
    paused = 1


class Frame:
    """Describes the image frame.

    Attributes:
        x (int): Frame offset from the left.
        y (int): Frame offset from the top.
        width (int): Frame width.
        height (int): Frame height.

        image_width (int): Full image width. Required for compatibility.
        image_height (int): Full image height. Required for compatibility.

        quad: Keeps a low-level frame object. Required for drawing.

    """
    def __init__(self, x, y, width, height, sw, sh):
        """Initialize frame object.

        Args:
            x (int): Frame offset from the left.
            y (int): Frame offset from the top.
            width (int): Frame width.
            height (int): Frame height.

            sw (int): Full image width. Required for compatibility.
            sh (int): Full image height. Required for compatibility.

        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.image_width = sw
        self.image_height = sh

        self.quad = self.create_frame(self.width, self.height)

    def get_viewport(self):
        """Return the frame viewport.

        Returns:
            tuple: A tuple four int elements, which means the frame viewport.

        """
        return self.x, self.y, self.width, self.height

    def create_frame(self):
        """Abstract method. This method must be overloaded.

        Returns:
            A low-level frame object which will be stored in the quad attr.

        Example:
            def create_frame(self, width, height):
                return pygame.Surface((width, height))

        """
        raise NotImplementedError('Implement "create_frame()" before using.')

    def draw(self):
        """Abstract method. This method must be overloaded.

        Args:
            Pass any argument what you need to draw an image.

        Example:
            def draw(self, canvas, image, x, y):
                rect = (self.x, self.y, self.width, self.height)
                self.quad.blit(image, (0, 0), rect)
                canvas.blit(self.quad, (x, y))
        """
        raise NotImplementedError('Implement "draw()" before using.')


class Grid:
    """Grids have only one purpose: To build groups of quads of the same size
    as easily as possible. Grids are just a convenient way of getting frames
    from a sprite. Frames are assumed to be distributed in rows and columns.
    Frame 1,1 is the one in the first row, first column.

    Attributes:
        FrameType (class): Derived class from the Frame
            with overloaded methods.

        frame_width (int): Width of the animation frame.
        frame_height (int): Height of the animation frame.
        image_width (int): Width of the image where all the frames are.
        image_height (int): Height of the image where all the frames are.

        left (int, optional): The left coordinate of the point in the image
            where you want to put the origin of coordinate of the grid.
            Defaults to 0.
        top (int, optional): The top coordinate of the point in the image
            where you want to put the origin of coordinate of the grid.
            Defaults to 0.
        border (int, optional): Allows you to define "gaps" between your frames
            int the image. Defaults to 0.

        width (int): The number of cells in the image by x-axis.
        height (int): The number of cells in the image by y-axis.

        frames (dict): The grid frames dictionary. For example:
            Left-top frame of the image (1, 1): self.frames[0][0]
            The frame with the coordinates[3, 8]: self.frames[2][7]

    """
    def __init__(self, FrameType,
                 frame_width, frame_height, image_width, image_height,
                 left=0, top=0, border=0):
        """Initialize the grid object.

        Args:
            FrameType (class): Derived class from the Frame
                with overloaded methods.

            frame_width (int): Width of the animation frame.
            frame_height (int): Height of the animation frame.
            image_width (int): Width of the image where all the frames are.
            image_height (int): Height of the image where all the frames are.

            left (int, optional): The left coordinate of the point in the image
                where you want to put the origin of coordinate of the grid.
                Defaults to 0.
            top (int, optional): The top coordinate of the point in the image
                where you want to put the origin of coordinate of the grid.
                Defaults to 0.
            border (int, optional): Allows you to define "gaps" between your
                frames int the image. Defaults to 0.

        """
        self.FrameType = FrameType

        self.frame_width = frame_width
        self.frame_height = frame_height
        self.image_width = image_width
        self.image_height = image_height

        self.left = left
        self.top = top
        self.border = border

        self.width = math.floor(self.image_width / self.frame_width)
        self.height = math.floor(self.image_height / self.frame_height)

        self.frames = {}

    def get_frames(self, *args):
        """Accepts an arbitrary number of parameters. They can be either
        numbers or strings.
            * Each two numbers are interpreted as quad coordinates. This way,
              self.get_frames(3, 4) will return the frame in column 3, row 4 of
              the grid. There can be more than just two:
              self.get_frames(1, 1, 1, 2, 1, 3) will return the frames in
              {1, 1}, {1, 2} and {1, 3} respectively.
            * Using numbers for long rows is tedious - so grids also accept
              strings. The previous row of 3 elements, for example, can be also
              expressed like this: self.get_frames(1, '1-3') . Again,
              there can be more than one string
              (self.get_frames(1,'1-3', '2-4', 3)) and it's also possible
              to combine them with numbers (self.get_frames(1, 4, 1, '1-3'))

        Returns:
            The list with the frames.

        Examples:
            grid.get_frames('1-5', 1)
            grid.get_frames('1-3', 5, 2, 5) # Ping-pong animation type. Will
                # return the frames in {1, 3}, {2, 3}, {3, 3}, {2, 3}.

        """
        result = []

        for i in range(0, len(args), 2):
            min_x, max_x, step_x = _parse_interval(args[i])
            min_y, max_y, step_y = _parse_interval(args[i + 1])
            for y in range(min_y, max_y, step_y):
                for x in range(min_x, max_x, step_x):
                    result.append(self._get_or_create_frame(x, y))

        return result

    def __call__(self, *args, **kwargs):
        """An alias for the get_frames function."""
        return self.get_frames(*args, **kwargs)

    def _get_or_create_frame(self, x, y):
        """Return the frame in the given coordinates or create the new frame,
        if it is not exists. The coordinates starts from (0, 0)

        Args:
            x (int): The x-coordinate of the required frame.
            y (int): The y-coordinate of the required frame.

        Returns:
            The frame object.

        """
        assert type(x) == int and x >= 0 and x < self.width
        assert type(y) == int and y >= 0 and y < self.height

        if x not in self.frames:
            self.frames[x] = {}
        if y not in self.frames[x]:
            self.frames[x][y] = self._create_frame(x, y)

        return self.frames[x][y]

    def _create_frame(self, x, y):
        """Create the new frame at the given coordinates.
        Args:
            x (int): The x-coordinate of the new frame.
            y (int): The y-coordinate of the new frame.

        Returns:
            The new frame object.

        """
        frame_x = self.left + x * self.frame_width + (x + 1) * self.border
        frame_y = self.top + y * self.frame_height + (y + 1) * self.border
        return self.FrameType(frame_x, frame_y,
                              self.frame_width, self.frame_height,
                              self.image_width, self.image_height)


class Animation:
    """Animations are groups of frames that are interchanged
    every now and then.

    Attributes:
        durations (dict): A dictionary of the each frame duration.
        intervals (list): A list each element of which marks the start time
            of the next frame.
        total_duration (number): The total duration of the animation.
        on_loop (function): it will be called every time an animation "loops".

        frames (list): An array of frames
            (which you can get by calling the Grid.get_frames function).
        timer (int): The current time of the animation.
        position (int): The current animation frame number.
        status (Status): The current animation status.

        flipped_h (bool): Compatibility argument. Does not using yet.
        flipped_v (bool): Compatibility argument. Does not using yet.

    Examples:
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

    """
    def __init__(self, frames, durations, on_loop=lambda loops: None):
        """Initialize the animation object.

        Args:
            frames (list): An array of frames
                (which you can get by calling the Grid.get_frames function).
            durations (int, float, list ,dictionary):
                * When it's a number, it represents the duration of all frames
                  in the animation.
                * When it's a dictionary, it can represent different durations
                  for different frames. You can specify durations
                  for ranges: {'3-5': 0.2}.
                * When it's a list, you must specify a duration of the each
                frame individually, like this: [0.2, 1, 0.3, 0.3, 0.3, 0.6]
            on_loop (function, optional): it will be called every time
                an animation "loops". Default to an empty lambda.

        """
        self.durations = _parse_durations(durations, len(frames))
        self.intervals, self.total_duration = _parse_intervals(self.durations)
        self.on_loop = on_loop

        self.frames = frames[:]
        self.timer = 0
        self.position = 0
        self.status = Status.playing

        self.flipped_h = False
        self.flipped_v = False

    def update(self, dt):
        """Use this function to change frames according to the time
        that has passed.

        Args:
            dt (float): Delta-time between two frames.

        """
        if self.status != Status.playing:
            return

        self.timer += dt
        loops = math.floor(self.timer / self.total_duration)
        if loops != 0:
            self.timer -= self.total_duration * loops
            self.on_loop(loops)

        self.position = self._seek_frame_index(self.intervals, self.timer)

    def draw(self, *args, **kwargs):
        """Draw the current frame.
        Args:
            You can specify any arguments, that you want. All of it will be
            passed to the current frame Frame.draw() method.

        """
        frame = self.get_frame_info()
        frame.draw(*args, **kwargs)

    def clone(self):
        """Creates a new animation identical to the current one.
        The only difference is that its internal counter is reset to 0
        (it's on the first frame).

        Returns:
            The new animation object.

        """
        new_animation = Animation(self.frames, self.durations. self.on_loop)
        new_animation.flipped_h = self.flipped_h
        new_animation.flipped_v = self.flipped_v
        return new_animation

    def get_frame_info(self):
        """Return the currently active frame for the animation."""
        frame = self.frames[self.position]
        return frame

    def goto_frame(self, position):
        """Move the animation to a given frame.

        Args:
            position (int): The frame index (starts from 0).

        """
        self.position = position
        self.timer = self.intervals[self.position]

    def pause(self):
        """Stop the animation from updating."""
        self.status = Status.paused

    def pause_at_end(self):
        """Move the animation to its last frame and then pause it."""
        self.position = len(self.frames) - 1
        self.timer = self.total_duration
        self.pause()

    def pause_at_start(self):
        """Move the animation to its first frame and then pause it."""
        self.position = 0
        self.timer = 0
        self.pause()

    def resume(self):
        """Unpause the animation."""
        self.status = Status.playing

    def flip_h(self):
        """Flip an animation horizontally (left goes to right and viceversa).
        This means that the frames are simply drawn differently, nothing more.

        Note:
            This method does not create a new animation.
            If you want to create a new one, use the clone method.

        Returns:
            The animation, so you can do things like:
                a = Animation(g(1,'1-10'), 0.1).flipV()

        """
        self.flipped_h = not self.flipped_h
        return self

    def flip_v(self):
        """Flips an animation vertically.
        The same rules that apply to flip_h also apply here.

        """
        self.flipped_v = not self.flipped_v
        return self

    @staticmethod
    def _seek_frame_index(intervals, timer):
        """Find out the current animation frame index based on
        the animation time.

        Args:
            intervals (list): A list each element of which marks the start time
                of the next frame.
            timer (int): The current time of the animation.

        Returns:
            The frame index based on the gived arguments.

        """
        for i in range(len(intervals) - 1, -1, -1):
            if timer > intervals[i]:
                return i
        return len(intervals) - 1


def new_grid(*args, **kwargs):
    """An alias for the Grid constructor."""
    return Grid(*args, **kwargs)


def new_animation(*args, **kwargs):
    """An alias for the Animation constructor."""
    return Animation(*args, **kwargs)


def _parse_interval(s):
    """Parse the given interval.

    Args:
        s (int, str): It can be or just int, or interval (str) like '1-5'.

    Returns:
        A tuple of:
            * minimal interval value;
            * maximal interval value;
            * step.
        The tuple can be passed to the range function.

    >>> _parse_interval(4)
    (3, 4, 1)
    >>> _parse_interval('1-8')
    (0, 8, 1)
    >>> _parse_interval('7-2')
    (6, 0, -1)

    """
    if type(s) == int:
        return s - 1, s, 1
    s = re.sub(r'\s+', '', s)
    match = re.match(r'^(\d+)-(\d+)$', s)

    assert match is not None, 'Could not parse interval from "{0}"'.format(s)

    min_ = int(match.group(1))
    max_ = int(match.group(2))
    step = 1 if max_ >= min_ else -1

    if step > 0:
        min_ -= 1
    elif step < 0:
        min_ -= 1
        max_ -= 2

    return min_, max_, step


def _parse_intervals(durations):
    """Parse the given durations.

    Args:
        durations (dict): A dictionary of the each frame duration.

    Returns:
        A tuple of:
            * A list each element of which marks the start time
              of the next frame.
            * The total animation length.

    """
    result, time_ = [], 0
    for _, duration in durations.items():
        time_ += duration
        result.append(time_)
    return result, time_


def _parse_durations(durations, frames_count):
    """Converts durations of many types to the durations list.

    Args:
        durations (int, float, list ,dictionary):
            * When it's a number, it represents the duration of all frames
              in the animation.
            * When it's a dictionary, it can represent different durations
              for different frames. You can specify durations
              for ranges: {'3-5': 0.2}.
            * When it's a list, you must specify a duration of the each
            frame individually, like this: [0.2, 1, 0.3, 0.3, 0.3, 0.6]
        frames_count (int): The number of the frames.

    Returns:
        Durations list like [0.2, 1, 0.3, 0.3, 0.3, 0.6].

    """
    result = {}

    if isinstance(durations, _NUMBER_TYPES):
        for i in range(frames_count):
            result[i] = durations
    elif type(durations) == list:
        for i, duration in enumerate(durations):
            result[i] = duration
    elif type(durations) == dict:
        for key, duration in durations.items():
            min_, max_, step = _parse_interval(key)
            for i in range(min_, max_, step):
                result[i] = duration

    if len(result) != frames_count:
        raise RuntimeError()

    return result


if __name__ == '__main__':
    import doctest
    doctest.testmod()
