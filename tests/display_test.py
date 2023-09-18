from raspberrypi_epd.buffer import DisplayBuffer


def test_buffer():
    buffer = DisplayBuffer(4, 4)
    assert buffer.WIDTH == 8
