import numpy as np
from PIL import Image, ImageDraw
import logging


class Render:
    def __init__(self, width, height, data):
        """Initializes a Render object to work as a virtual display

        Args:
            width (int): Width of the image in pixels
            height (int): Height of the image in pixels
            data (np.array(np.uint8)): Array of data that describes the pixels in the screen (monochrome)
        """
        logging.debug(f'Creating a render object for a screen of {width}x{height} pixels.')
        logging.debug(f'Bytes received: {data.size} == {int(width * height / 8)}')
        self.WIDTH = width
        self.HEIGHT = height
        self._data = data
        if data.ndim != 1:
            raise ValueError(f'Incorrect array form: {data.shape}')
        if data.size != int(width * height / 8):
            raise ValueError(f'Incorrect number of data bytes. Expected {int(width * height / 8)} but got {data.size}')
        self._image = None

    def render(self):
        image = Image.new('1', (self.WIDTH, self.HEIGHT))
        pixels = image.load()
        # canvas = ImageDraw.Draw(image)
        masks = [0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01]
        for y in range(self.HEIGHT):
            past_lines = int((self.WIDTH / 8) * y)
            for x in range(self.WIDTH):
                bit = x % 8
                byte_offset = int(x / 8)
                byte_index = past_lines + byte_offset
                color = 1 if self._data[byte_index] & masks[bit] else 0
                # canvas.point((x, y), color)
                pixels[x, y] = color
        self._image = image

    def save(self, path: str):
        self._image.save(path)

    def show(self):
        self._image.show()
