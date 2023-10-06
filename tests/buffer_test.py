import pytest
from epd_test.buffer import DisplayBuffer
import numpy as np


def test_buffer_dimmensions():
    display = DisplayBuffer(4, 4)
    assert display.WIDTH == 8 and display.HEIGHT == 4


@pytest.mark.parametrize('x, y', [(0, 0), (9, 2), (4, 4), (10, 1)])
def test_setter(x, y):
    display = DisplayBuffer(16, 9)
    display.draw_pixel(x, y)
    assert display.get_pixel_value(x, y) == 1

@pytest.mark.parametrize(
    "x, y, pixel_val",
    [
        (0, 0, 128),
        (0, 7, 128),
        (6, 0, 2),
        (11, 0, 16)
    ]
)
def test_buffer_pixel(x, y, pixel_val):
    display = DisplayBuffer(16, 9)
    display.draw_pixel(x, y)
    display.dump_raw_buffer()
    assert display.get_pixel_byte(x, y) == pixel_val


def test_serialization():
    # 8 bytes
    display = DisplayBuffer(8, 8)
    display.draw_group_pixels([(0, 0), (1, 0), (4, 0), (5, 0)]) # CC
    display.draw_group_pixels([(0, 1), (2, 1), (4, 1), (6, 1)]) # AA
    bs = display.serialize()
    display.dump_raw_buffer()
    assert bs[0] == np.uint8(0xCC)
    assert bs[1] == np.uint8(0xAA)

