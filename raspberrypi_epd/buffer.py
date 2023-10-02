import numpy as np
import logging
from bdfparser import Font


class DisplayBuffer:
    """
    Class to act as an abstraction of a display
    """

    def __init__(self, width, height, bg=1, fg=0):
        """
        Initializes the display buffer. Each pixel is modeled in one bit, the default color is "white" background and
        "black" foreground
        :param width: Width of the display this buffer models
        :param height: Height of the display this buffer models
        :param bg: Background value (default is 1=white)
        :param fg: Foreground value (default is 0=black)
        """
        # Pad the buffer to have whole bytes
        self.WIDTH = width if width % 8 == 0 else (int(width / 8) + 1) * 8
        self.HEIGHT = height
        self._BYTE_WIDTH = self.WIDTH / 8
        self._BYTE_HEIGHT = self.HEIGHT / 8
        self._buffer = np.zeros((self.WIDTH * self.HEIGHT), dtype=np.uint8)
        self._out_of_bounds_error = False
        self._foreground = fg
        self._background = bg
        self._rotation = 0
        self.x_length = self.WIDTH
        self.y_length = self.HEIGHT

    def rotate(self, degrees: int):
        """Virtually rotates the display to draw in different modes. The
        rotation is specified in degrees with the values: 0, 90, 180, 270

        :param int degrees: The rotation angle
        """
        if degrees not in [0, 90, 180, 270]:
            logging.warning("Invalid rotation.")
            return
        if degrees == 90 or degrees == 270:
            self.x_length = self.HEIGHT
            self.y_length = self.WIDTH
        elif degrees == 0 or degrees == 180:
            self.x_length = self.WIDTH
            self.y_length = self.HEIGHT
        self._rotation = degrees

    def draw_pixel(self, x: int, y: int, value: np.uint8):
        """
        Draw a single pixel in (x, y) with the indicated value
        :param int x: X coordinate of the pixel to draw
        :param int y: Y Coordinate of the pixel to draw
        :param np.uint8 value: Value to set the pixel to (1 or 0)
        :return: none
        """
        if not self._valid_coords(x, y):
            return
        xr, yr = self.rotate_coords(x, y)
        start, end, bit = self._get_slice(xr, yr)
        self._buffer[start + bit] = value

    def draw_pixels(self, pixels: list, value: np.uint8):
        """
        Draws the pixels specified in a list of 2-tuples with the value specified
        :param list pixels: List of 2-tuples that indicate each pixel, the tuples are in the form (x, y)
        :param np.uint8 value: The value to set the pixels to
        """
        for pixel in pixels:
            self.draw_pixel(pixel[0], pixel[1], value)

    def set_pixel(self, x, y):
        """Draws a single pixel by setting its representing bit in the buffer to the foreground value
        :param int x: X coordinate of the pixel
        :param int y: Y coordinate of the pixel
        """
        if not self._valid_coords(x, y):
            return
        s, e, b = self._get_slice(x, y)
        self._buffer[s + b] = self._foreground

    def set_background(self, value: np.uint8):
        """
        Sets the value used as the background (0 or 1). When a pixel is cleared is set to
        this value
        :param np.uint8 value: The value to be used as background
        :return: None
        """
        self._background = value

    def set_foreground(self, value: np.uint8):
        """
        Sets the value used as foreground (0 or 1). When a pixel is set, its value its set to this
        :param value: The value to be used as foreground
        :return: None
        """
        self._foreground = value

    def set_group_pixels(self, list_of_pixels):
        """Sets the pixels in the given list
        :param list list_of_pixels: List of 2-tuples with the points (x, y)
        """
        for pixel in list_of_pixels:
            self.set_pixel(pixel[0], pixel[1])

    def clear_pixel(self, x, y):
        """Erases a pixel on the display by clearing its representing bit in the buffer
        :param int x: X coordinate of the pixel to erase
        :param int y: Y coordinate of the pixel to erase
        """
        if not self._valid_coords(x, y):
            return
        s, e, b = self._get_slice(x, y)
        self._buffer[s + b] = self._background

    def clear_group_pixels(self, list_of_pixels: list):
        """Clears the pixels/bits in the buffer
        :param list list_of_pixels: A list of 2-tuples with the points (x, y)
        """
        for pixel in list_of_pixels:
            self.clear_pixel(pixel[0], pixel[1])

    def clear_screen(self, value=0):
        """Sets all the pixels in the screen to the same value
        :param int value: the value to fill the screen with (0 or 1)
        """
        if value == 1 or value == 0:
            self._buffer.fill(np.uint8(value))
        else:
            logging.warning(f"Incorrect color value {value}")

    def get_pixel_value(self, x, y):
        """Reads the value of the given point (x, y)
        :param int x: X coordinate of the point
        :param int y: Y Coordinate of the point
        :return np.uint8: The bit as it exists in the buffer
        """
        if not self._valid_coords(x, y):
            return np.uint8(0x00)
        s, e, b = self._get_slice(x, y)
        return self._buffer[s + b]

    def get_pixel_byte(self, x, y):
        """Extracts the byte from the buffer that contains the bit of the given pixel
        :param int x: X coordinate of the pixel to read
        :param int y: Y coordinate of the pixel to read
        :return np.uint8: A single byte representation containing the pixel
        """
        # Calculate x1 and x2 to get the slice from the buffer
        x1, x2, _ = self._get_slice(x, y)
        # logging.debug(f'Slicing buffer[{x1}:{x2}]')
        pixel_byte = DisplayBuffer.create_byte_from_array(self._buffer[x1:x2])
        return pixel_byte

    def draw_line(self, x1, y1, x2, y2, value: np.uint8):
        """Implements the Bresenham algorithm to draw a line from (x1, y1) to (x2, y2)
        :param int x1: Starting x component
        :param int y1: Starting y component
        :param int x2: Final x component
        :param int y2: Final y component
        :param int value: Value (color) to set the bit to
        """
        dx = x2 - x1
        dy = y2 - y1

        if dy >= 0:
            y_incr = 1
        else:
            dy = -dy
            y_incr = -1

        if dx >= 0:
            x_incr = 1
        else:
            dx = -dx
            x_incr = -1

        if dx >= dy:
            y_incr_s = 0
            x_incr_s = x_incr
        else:
            y_incr_s = y_incr
            x_incr_s = 0
            # Switch dX and dY
            k = dx
            dx = dy
            dy = k

        x = x1
        y = y1
        a = 2 * dy
        b = a - dx
        p = b - dx
        while True:
            self.draw_pixel(x, y, value)
            if b >= 0:
                x = x + x_incr
                y = y + y_incr
                b = b + p
            else:
                x = x + x_incr_s
                y = y + y_incr_s
                b = b + a
            if x == x2 and y == y2:
                break
        self.draw_pixel(x, y, value)

    def draw_circle(self, xc: int, yc: int, r: int, value: np.uint8):
        """Draws a circle with the Midpoint Algorithm
        :param int xc: X coordinate of the circle's center
        :param int yc: Y coordinate of the circle's center
        :param int r: Circle's radius
        :param np.uint8 value: Value to set the bit in the buffer
        """
        if r == 0:
            self.draw_pixel(xc, yc, value)
            return

        xk, yk = (r, 0)
        pk = 1 - r
        self.draw_pixels(
            [
                (xk + xc, yk + yc),
                (-xk + xc, yk + yc),
                (xk + xc, -yk + yc),
                (-xk + xc, -yk + yc),
            ],
            value,
        )
        self.draw_pixels([(xc, yc + r), (xc, yc - r)], value)
        while xk > yk:
            yk = yk + 1
            if pk <= 0:
                pk = pk + 2 * yk + 1
            else:
                xk -= 1
                pk = pk + 2 * yk - 2 * xk + 1

            if xk < yk:
                break

            # self.draw_pixel(xk + xc, yk + yc)
            self.draw_pixels(
                [
                    (xk + xc, yk + yc),
                    (-xk + xc, yk + yc),
                    (xk + xc, -yk + yc),
                    (-xk + xc, -yk + yc),
                ],
                value,
            )
            if xk != yk:
                self.draw_pixels(
                    [
                        (yk + xc, xk + yc),
                        (-yk + xc, xk + yc),
                        (yk + xc, -xk + yc),
                        (-yk + xc, -xk + yc),
                    ],
                    value,
                )

    def draw_bitmap(self, bitmap: np.array, x: int, y: int, w: int, h: int, value: np.uint8):
        """Draws a bitmap on the buffer. The bitmap starts at the upper left corner (x, y)
        and the lower right corner is (x+w, y+h)
        :param np.array bitmap: A 1-dimmensional array of bytes, has to have at least shape of (w, h)
        :param int x: X coordinate where to start drawing the bitmap
        :param int y: Y coordinate where to start drawing the bitmap
        :param int w: Width of the bitmap
        :param int h: Height of the bitmap
        :param np.uint8 value: Value to set in the buffer
        """
        x_p = 0
        y_p = 0
        for byte in bitmap:
            bitmasks = np.array(
                [0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01], dtype=np.uint8
            )
            bit = 0
            for mask in bitmasks:
                if mask & byte:
                    self.draw_pixel(x_p + x, y_p + y, value)
                bit = bit + 1
                x_p = x_p + 1
            if x_p == w:
                y_p = y_p + 1
                x_p = 0

    def draw_text(self, text: str, font: Font, x: int, y: int, value: np.uint8):
        """
        Render a bitmap of the text with the provided font and draw it in the buffer
        :param text: The string to render
        :param font: The Font object to use
        :param x: X coordinate of the upper left corner of the bitmap
        :param y: Y Coordinate of the upper left corner of the bitmap
        :param value: Value to set the pixels in the buffer to
        :return: None
        """
        text_bitmap = font.draw(text)
        array, width, height = self._bitmap_to_bytearray(text_bitmap.todata(4))
        self.draw_bitmap(array, x, y, width, height, value)

    def draw_rectangle(self, x: int, y: int, w: int, h: int, value: np.uint8):
        """
        Draws a rectangle with 1-px wide lines, and no fill
        :param int x: X Coordinate of the upper left corner
        :param int y: Y Coordinate of the upper left corner
        :param int w: Rectangle's width
        :param int h: Rectangle's height
        :param np.uint8 value: Value to set the pixels to
        :return: None
        """
        self.draw_line(x, y, x + w, y, value)
        self.draw_line(x + w, y, x + w, y + h, value)
        self.draw_line(x + w, y + h, x, y + h, value)
        self.draw_line(x, y + h, x, y, value)

    def _get_slice(self, x, y):
        """
        Locates the slice of the buffer that contains a whole byte given x and y coordinates
        :param int x: X coordinate of the pixel
        :param int y: Y coordinate of the pixel
        :return tuple: start position, end position, bit offset
        """
        start = (y * self.WIDTH) + int(x / 8) * 8
        end = start + 8
        bit = x % 8
        return start, end, bit

    def pixel_address(self, x: int, y: int):
        """
        Obtains the byte addr that contains the bit representing the pixel at (x, y)
        :param int x: X coordinate of the point of interest
        :param int y: Y coordinate of the point of interest
        :return: The 0-based address (offset) of the byte
        """
        s, e, b = self._get_slice(x, y)
        return s

    def _valid_coords(self, x, y):
        """
        Validates that the given coordinates are within the display (and buffer) bounds.

        :param int x: X coordinate
        :param int y: Y coordinate

        :raises ValueError: If the flag DisplayBuffer._out_of_bounds_error is set to True and
                            the coordinates are outside of the visible screen

        :returns bool: True if they are valid (visible) coordinates, False otherwise
        """
        within_x = 0 <= x <= self.x_length
        within_y = 0 <= y <= self.y_length
        if within_x and within_y:
            return True
        else:
            if self._out_of_bounds_error:
                raise ValueError("Coordinates out of bounds")
        return False

    def rotate_coords(self, x: int, y: int):
        """
        Does a tramslation according to the current rotation

        :param int x: X Coordinate to transform
        :param int y: Y Coordinate to transform

        :return tuple:  The coordinate pair of the base buffer that corresponds to the input
        """
        xn, yn = (0, 0)
        if self._rotation == 90:
            xn = (self.WIDTH - 1) - y
            yn = x
        elif self._rotation == 180:
            xn = (self.WIDTH - 1) - x
            yn = (self.HEIGHT - 1) - y
        elif self._rotation == 270:
            xn = y
            yn = (self.HEIGHT - 1) - x
        else:
            xn = x
            yn = y

        return xn, yn

    def serialize(self):
        """
        Converts the internal buffer to an array of bytes

        :returns np.array[np.uint8]: The internal buffer as an array of bytes
        """
        bytelist = []
        total_pixels = self.WIDTH * self.HEIGHT
        logging.debug(f"The size of serialized buffer is {total_pixels}")
        for byte in range(int(total_pixels / 8)):
            start = byte * 8
            byte_nbr = self.create_byte_from_array(self._buffer[start : start + 8])
            bytelist.append(np.uint8(byte_nbr))
        logging.debug(f"Final size of list: {len(bytelist)}")
        return np.array(bytelist, dtype=np.uint8)

    def serialize_area(self, x: int, y: int, width: int, height: int):
        """
        Serializes an area of the screen
        :param int x: X Coordinate of the upper left corner
        :param int y: Y Coordinate of the upper left corner
        :param int width: Area width
        :param int height: Area height
        :returns: The array of bytes
        :rtype np.array[np.uint8]
        """
        if not self._valid_coords(x, y) or not self._valid_coords(
            x + width, y + height
        ):
            logging.warning(f"The specified coordinates are invalid")
            return
        slice_start, _, _ = self._get_slice(x, y)
        _, slice_end, _ = self._get_slice(x + width, y + height)
        logging.debug(
            f"Serializing the area ({x}, {y}, {width}, {height}) at [{slice_start}:{slice_end}]"
        )
        total_bytes = int((slice_end - slice_start) / 8)
        logging.debug(f"Expecting {total_bytes} bytes")
        byte_list = []
        byte_offset = int(slice_start / 8)
        for byte in range(byte_offset, byte_offset + total_bytes):
            start = byte * 8
            byte_value = self.create_byte_from_array(self._buffer[start : start + 8])
            byte_list.append(byte_value)
        return np.array(byte_list, dtype=np.uint8)

    @staticmethod
    def create_byte_from_array(bitarray: np.array):
        """
        Converts a binary array (1s and 0s only) into a byte

        :param np.array bitarray: An array of size 8 containing only 1s and 0s

        :raises ValueError: if the array size isn't exactly 8

        :returns: The byte representation
        :rtype np.uint8
        """
        # logging.debug(f'Bit array: {bitarray}')
        if len(bitarray) != 8:
            raise ValueError(
                f"Incorrect array size. Array needs to be exactly 8 but got {len(bitarray)}"
            )
        number = 0
        for b in bitarray:
            number = (2 * number) + b
        return np.uint8(number)

    def effective_area(self, x: int, y: int, width: int, height: int):
        """
        Calculate the intersection of the supplied rectangular area and the available screen space
        :param int x: Starting X coordinate (left side of the area)
        :param int y: Starting Y coordinate (top side of the area)
        :param int width: Width of the area
        :param int height: Height of the area
        :return: 4-tuple with (x, y, width, height) inside the boundaries of the screen
        """
        if width < 0 or height < 0:
            return 0, 0, 0, 0
        if (x < 0 and (x + width) < 0) or (x > self.WIDTH):
            return 0, 0, 0, 0
        if (y < 0 and (y + height) < 0) or (y > self.HEIGHT):
            return 0, 0, 0, 0
        x1 = 0 if x < 0 else x
        y1 = 0 if y < 0 else y
        x2 = self.WIDTH if x + width > self.WIDTH else x + width
        y2 = self.HEIGHT if y + height > self.HEIGHT else y + height
        return x1, y1, x2 - x1, y2 - y1

    def dump_raw_buffer(self):
        """
        Prints the buffer in a matrix of WIDTH*HEIGHT
        """
        for y in range(self.HEIGHT):
            line_offset = y * self.WIDTH
            logging.debug(self._buffer[line_offset : line_offset + self.WIDTH])

    # █●
    def render(self, on_pixel="█", off_pixel=" "):
        """
        Generates a ASCII art representation of this buffer
        :param str on_pixel: Character to represent a "set bit"
        :param str off_pixel: Character to represent a "cleared bit"

        :returns: An ASCII art string
        :rtype str
        """
        lines = []
        for line in range(self.HEIGHT):
            line_offset = line * self.WIDTH
            sliced_buffer = self._buffer[line_offset : line_offset + self.WIDTH]
            ascii_list = [on_pixel if p == 1 else off_pixel for p in sliced_buffer]
            ascii_line = "".join(ascii_list)
            lines.append(ascii_line)
        return "\n".join(lines)

    @staticmethod
    def _bitmap_to_bytearray(bitmap: list):
        """
        Converts a bitmap from a font into a bitmap

        :param list bitmap: A list of hex strings, each one represents a line

        :returns: np.array(np.uint8): The byte array
                int: The width in bits (pixels) of the bitmap as it might be padded to complete a byte
                int: The height in bits (pixels) of the bitmap
        """
        byte_list = []
        bytes_per_line = 0
        for line in bitmap:
            nibbles = len(line)
            bytes_per_line = 0
            for byte in range(int(nibbles / 2)):
                first_nibble = line[byte * 2]
                if byte == nibbles:
                    second_nibble = 0
                else:
                    second_nibble = line[byte * 2 + 1]
                hex_byte = first_nibble + second_nibble
                byte_value = np.uint8(int(hex_byte, base=16))
                byte_list.append(byte_value)
                bytes_per_line = bytes_per_line + 1
        return np.array(byte_list), bytes_per_line * 8, len(bitmap)
