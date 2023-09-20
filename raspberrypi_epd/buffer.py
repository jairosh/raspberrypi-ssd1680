import numpy as np
import logging


class DisplayBuffer:
    """
    Class to act as an abstraction of a display
    """

    def __init__(self, width, height):
        # Pad the buffer to have whole bytes
        self.WIDTH = width if width % 8 == 0 else (int(width / 8) + 1) * 8
        self.HEIGHT = height
        self._BYTE_WIDTH = self.WIDTH / 8
        self._BYTE_HEIGHT = self.HEIGHT / 8
        self._buffer = np.zeros((self.WIDTH * self.HEIGHT), dtype=np.uint8)
        self._out_of_bounds_error = False

    def draw_pixel(self, x, y):
        """Draws a single pixel by setting its representing bit in the buffer

        Args:
            x (int): X coordinate of the pixel
            y (int): Y coordinate of the pixel
        """
        if not self._valid_coords(x, y):
            return
        s, e, b = self._get_slice(x, y)
        self._buffer[s + b] = 1

    def draw_group_pixels(self, list_of_pixels):
        """Sets the pixels in the given list

        Args:
            list_of_pixels (list): List of 2-tuples with the points (x, y)
        """
        for pixel in list_of_pixels:
            self.draw_pixel(pixel[0], pixel[1])

    def clear_pixel(self, x, y):
        """Erases a pixel on the display by clearing its representing bit in the buffer

        Args:
            x (int): X coordinate of the pixel to erase
            y (int): Y coordinate of the pixel to erase
        """
        if not self._valid_coords(x, y):
            return
        s, e, b = self._get_slice(x, y)
        self._buffer[s + b] = 0

    def clear_group_pixels(self, list_of_pixels: list):
        """Clears the pixels/bits in the buffer

        Args:
            list_of_pixels (list): A list of 2-tuples with the points (x, y)
        """
        for pixel in list_of_pixels:
            self.clear_pixel(pixel[0], pixel[1])

    def clear_screen(self, value=0):
        """Sets all the pixels in the screen to the same value

        :param value: the value to fill the screen with
        """
        if value == 1 or value == 0:
            self._buffer.fill(np.uint8(value))

    def get_pixel_value(self, x, y):
        """Reads the value of the given point (x, y)

        Args:
            x (int): X coordinate of the point
            y (int): Y Coordinate of the point

        Returns:
            np.uint8: The bit as it exists in the buffer
        """
        if not self._valid_coords(x, y):
            return np.uint8(0x00)
        s, e, b = self._get_slice(x, y)
        return self._buffer[s + b]

    def get_pixel_byte(self, x, y):
        """Extracts the byte from the buffer that contains the bit of the given pixel

        Args:
            x (int): X coordinate of the pixel to read
            y (int): Y coordinate of the pixel to read

        Returns:
            _type_: _description_
        """
        # Calculate x1 and x2 to get the slice from the buffer
        x1, x2, _ = self._get_slice(x, y)
        # logging.debug(f'Slicing buffer[{x1}:{x2}]')
        pixel_byte = DisplayBuffer.create_byte_from_array(self._buffer[x1:x2])
        return pixel_byte

    def draw_line(self, x1, y1, x2, y2):
        """Implements the Bresenham algorithm to draw a line from (x1, y1) to (x2, y2)

        Args:
            x1 (int): Starting x component
            y1 (int): Starting y component
            x2 (int): Final x component
            y2 (int): Final y component
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
            self.draw_pixel(x, y)
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
        self.draw_pixel(x, y)

    def draw_circle_2(self, xc, yc, r):
        """Draws a circle centered in xc, yc of radius r using the Jesko method

        Args:
            xc (int): Center's X coordinate
            yc (int): Center's Y coordinate
            r (int): Radius
        """
        t1 = int(r / 16)
        x = r
        y = 0
        while x >= y:
            self.draw_pixel(x + xc, y + yc)
            self.draw_pixel(-x + xc, y + yc)
            self.draw_pixel(x + xc, -y + yc)
            self.draw_pixel(-x + xc, -y + yc)
            y = y + 1
            t1 = t1 + y
            t2 = t1 - x
            if t2 >= 0:
                t1 = t2
                x = x - 1
        self.draw_group_pixels([(xc + r, yc),
                                (xc - r, yc),
                                (xc, yc + r),
                                (xc, yc - r)])

    def draw_circle(self, xc, yc, r):
        """Draws a circle with the Midpoint Algorithm

        Args:
            xc (int): X coordinate of the circle's center
            yc (int): Y coordinate of the circle's center
            r (int): Circle's radius
        """
        if r == 0:
            self.draw_pixel(xc, yc)
            return

        xk, yk = (r, 0)
        pk = 1 - r
        self.draw_group_pixels([(xk + xc, yk + yc),
                                (-xk + xc, yk + yc),
                                (xk + xc, -yk + yc),
                                (-xk + xc, -yk + yc)])
        self.draw_group_pixels([(xc, yc + r),
                                (xc, yc - r)])
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
            self.draw_group_pixels([(xk + xc, yk + yc),
                                    (-xk + xc, yk + yc),
                                    (xk + xc, -yk + yc),
                                    (-xk + xc, -yk + yc)])
            if xk != yk:
                self.draw_group_pixels([(yk + xc, xk + yc),
                                        (-yk + xc, xk + yc),
                                        (yk + xc, -xk + yc),
                                        (-yk + xc, -xk + yc)])

    def draw_bitmap(self, bitmap: np.array, x: int, y: int, w: int, h: int):
        """Draws a bitmap on the buffer. The bitmap starts at the upper left corner (x, y)
        and the lower right corner is (x+w, y+h)

        Args:
            bitmap (np.array): A 1-dimmensional array of bytes, has to have at least shape of (w, h)
            x (int): X coordinate where to start drawing the bitmap
            y (int): Y coordinate where to start drawing the bitmap
            w (int): Width of the bitmap
            h (int): Height of the bitmap
        """
        x_p = 0
        y_p = 0
        for byte in bitmap:
            bitmasks = np.array([0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01], dtype=np.uint8)
            bit = 0
            for mask in bitmasks:
                if mask & byte:
                    self.draw_pixel(x_p + x, y_p + y)
                bit = bit + 1
                x_p = x_p + 1
            if x_p == w:
                y_p = y_p + 1
                x_p = 0

    def _get_slice(self, x, y):
        """Locates the slice of the buffer that contains a whole byte given x and y coordinates

        Args:
            x (int): X coordinate of the pixel
            y (int): Y coordinate of the pixel

        Returns:
            tuple: start position, end position, bit offset
        """
        start = (y * self.WIDTH) + int(x / 8) * 8
        end = start + 8
        bit = x % 8
        return start, end, bit

    def pixel_address(self, x: int, y: int):
        """
        Obtains the byte addr that contains the bit representing the pixel at (x, y)
        :param x: X coordinate of the point of interest
        :param y: Y coordinate of the point of interest
        :return: The 0-based address (offset) of the byte
        """
        s, e, b = self._get_slice(x, y)
        return s

    def _valid_coords(self, x, y):
        """Validates that the given coordinates are within the display (and buffer) bounds.

        Args:
            x (int): X coordinate
            y (int): Y coordinate

        Raises:
            ValueError: If the flag DisplayBuffer._out_of_bounds_error is set to True and
            the coordinates are outside of the visible screen

        Returns:
            Boolean: True if they are valid (visible) coordinates, False otherwise
        """
        within_x = 0 <= x <= self.WIDTH
        within_y = 0 <= y <= self.HEIGHT
        if within_x and within_y:
            return True
        else:
            if self._out_of_bounds_error:
                raise ValueError('Coordinates out of bounds')
        return False

    def serialize(self):
        """Converts the internal buffer to a list of bytes

        Returns:
            np.array(np.uint8): The internal buffer as an array of bytes
        """
        bytelist = []
        total_pixels = self.WIDTH * self.HEIGHT
        logging.debug(f'The size of serialized buffer is {total_pixels}')
        for byte in range(int(total_pixels / 8)):
            start = byte * 8
            byte_nbr = self.create_byte_from_array(self._buffer[start: start + 8])
            bytelist.append(np.uint8(byte_nbr))
        logging.debug(f'Final size of list: {len(bytelist)}')
        return np.array(bytelist, dtype=np.uint8)

    @staticmethod
    def create_byte_from_array(bitarray: np.array):
        """Converts a binary array (1s and 0s only) into a byte

        Args:
            bitarray (np.array): An array of size 8 containing only 1s and 0s

        Raises:
            ValueError: if the array size isn't exactly 8

        Returns:
            np.uint8: The byte representation
        """
        # logging.debug(f'Bit array: {bitarray}')
        if len(bitarray) != 8:
            raise ValueError('Incorrect array size. Array needs to be exactly 8')
        number = 0
        for b in bitarray:
            number = (2 * number) + b
        return np.uint8(number)

    def dump_raw_buffer(self):
        """Prints the buffer in a matrix of WIDTH*HEIGHT
        """
        for y in range(self.HEIGHT):
            line_offset = y * self.WIDTH
            logging.debug(self._buffer[line_offset: line_offset + self.WIDTH])

    # █●
    def render(self, on_pixel='█', off_pixel=' '):
        """Generates a ASCII art representation of this buffer

        Returns:
            str : An ASCII art string
        """
        lines = []
        for line in range(self.HEIGHT):
            line_offset = line * self.WIDTH
            sliced_buffer = self._buffer[line_offset: line_offset + self.WIDTH]
            ascii_list = [on_pixel if p == 1 else off_pixel for p in sliced_buffer]
            ascii_line = ''.join(ascii_list)
            lines.append(ascii_line)
        return '\n'.join(lines)
