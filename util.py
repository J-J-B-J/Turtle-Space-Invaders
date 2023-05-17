"""Utility functions to be used by many games"""
import time


def optimised_coord_funcs(width, height, original_width, original_height):
    """Scale the screen size to make it the biggest ratio of 16:9 possible
    with the current window size (basically makes the game compatible with
    every screen size)"""
    relative_width = width * original_width
    relative_height = height * original_height

    def coord(original_dimension: int, design_size: int, production_size: int):
        """Scale a coordinate to the correct size for the screen"""
        return (original_dimension / design_size) * production_size

    if relative_width > relative_height:
        # The screen is slightly wider than wanted, so the left and right edges
        # will be unused
        x = lambda num: coord(num, original_width,
                              (height / original_height) * original_width)
        y = lambda num: coord(num, original_height, height)
    elif relative_height > relative_width:
        # The screen is slightly taller than wanted, so the top and bottom
        # edges will be unused
        x = lambda num: coord(num, original_width, width)
        y = lambda num: coord(num, original_height,
                              (width / original_width) * original_height)
    else:
        # The screen is exactly 16:9, so all edges will be exactly 16:9
        x = lambda num: coord(num, original_width, width)
        y = lambda num: coord(num, original_height, height)

    pos = lambda x_pos, y_pos: (x(x_pos), y(y_pos))

    return x, y, pos


def time_ms():
    """Get the time in milliseconds"""
    return time.time_ns()/1_000_000


def wait_ms(ms: int, screen):
    """Wait a certian number of milliseconds while updating the screen"""
    start_time = time_ms()
    target_time = start_time + ms
    while time_ms() < target_time:
        screen.update()
