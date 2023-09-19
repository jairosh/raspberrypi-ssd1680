import numpy as np
import raspberrypi_epd.commands as cmd
import logging
import time
import spidev
import RPi.GPIO as GPIO
from enum import Enum
from raspberrypi_epd.buffer import DisplayBuffer


class Color(Enum):
    BLACK = 0
    WHITE = 1
    RED = 2


BLACK = np.uint8(0x00)
WHITE = np.uint8(0xFF)
RED = np.uint8(0xFF)


class WeAct213:
    """
    Provides the low level control/writing operations on the display
    """
    HEIGHT = 250
    WIDTH = 128
    WIDTH_VISIBLE = 122
    CONTROLLER = 'SSD1680'
    # Timings
    POWER_ON_TIME = 100
    POWER_OFF_TIME = 250
    FULL_REFRESH_TIME = 4100
    PARTIAL_REFRESH_TIME = 750
    RESET_WAIT_TIME = 10
    LUT_PARTIAL = np.array([0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x80, 0x80, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x40, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x0A, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x02, 0x01, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x00, 0x00, 0x00], dtype=np.uint8)

    def __init__(self, dc: int, cs: int, busy: int, reset: int):
        self._DC = dc
        self._CS = cs
        self._RESET = reset
        self._BUSY = busy
        GPIO.setup(self._DC, GPIO.OUT)
        GPIO.setup(self._CS, GPIO.OUT)
        GPIO.setup(self._RESET, GPIO.OUT)
        GPIO.output(self._RESET, GPIO.HIGH)
        self.BUSY = busy
        GPIO.setup(self.BUSY, GPIO.IN)
        self._spi = spidev.SpiDev()
        self._spi.open(bus=0, device=0)
        self._spi.max_speed_hz = 500000     # 500KHz
        self._spi.mode = 0                  # Clock polarity/phase
        self._bw_buffer = DisplayBuffer(self.WIDTH, self.HEIGHT)
        self._red_buffer = DisplayBuffer(self.WIDTH, self.HEIGHT)
        self.powered = False
        self._using_partial_mode = False

    def init(self):
        self.reset()
        self._startup()
        self._power_on()
        self._using_partial_mode = False

    def _power_on(self):
        # Power on
        self._write_command(cmd.DISPLAY_UPDATE_CONTROL_2)
        self._write_data_byte(np.uint8(0xf8))
        self._write_command(cmd.MASTER_ACTIVATION)
        self._wait_while_busy()
        self.powered = True
        logging.debug('Power on complete')

    def _power_off(self):
        if self.powered:
            self._write_command(cmd.DISPLAY_UPDATE_CONTROL_2)
            self._write_data_byte(np.uint8(0x83))
            self._write_command(cmd.MASTER_ACTIVATION)
            self._wait_while_busy()
            self.powered = False
            self._using_partial_mode = False

    def _init_partial(self):
        self._startup()
        # self._set_partial_area(0, 0, self.WIDTH, self.HEIGHT)
        self._write_command(cmd.WRITE_LUT_REG)
        self._write_data(self.LUT_PARTIAL)
        self._power_on()
        self.using_partial_mode = True

    def reset(self):
        logging.debug('Reseting the display')
        # Do a HW Reset
        GPIO.output(self._RESET, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self._RESET, GPIO.HIGH)
        # SW Reset (command 0x12)
        self._write_command(cmd.SW_RESET)
        self._wait_while_busy()
        # Wait 10ms
        time.sleep(0.01)
        #   Wait BUSY low
        self._wait_while_busy()
        logging.debug('Display was reset')

    def close(self):
        self._spi.close()
        GPIO.cleanup()

    def _wait_while_busy(self):
        counter = 0
        while True:
            busy = GPIO.input(self.BUSY)
            if busy == 0:
                break
            time.sleep(0.005)
            counter = counter + 1
        logging.debug(f'Display was busy for {counter*5} ms')

    def _startup(self):
        # Send init code
        #   Set gate driver output (0x01)
        self._write_command(cmd.DRIVER_OUTPUT_CONTROL)
        self._write_data_byte(np.uint8(0x27))
        self._write_data_byte(np.uint8([0x01]))
        self._write_data_byte(np.uint8([0x00]))
        #   Set display RAM size (0x11, 0x44, 0x45)
        self._write_command(cmd.DATA_ENTRY_MODE)
        self._write_data_byte(np.uint8([0x03]))
        #   Set panel border (0x3C)
        self._write_command(cmd.BORDER_WAVEFORM_CONTROL)
        self._write_data_byte(np.uint8(0x05))
        #   Sense temp (0x18)
        self._write_command(cmd.TEMP_SENSOR_CONTROL)
        self._write_data_byte(np.uint8(0x80))
        #   Load waveform LUT (0x22, 0x20)
        # Display update control
        self._write_command(cmd.DISPLAY_UPDATE_CONTROL)
        self._write_data_byte(np.uint8(0x00))
        self._write_data_byte(np.uint8(0x80))

    def _set_partial_area(self, x, y, width, height):
        self._write_command(cmd.SET_RAM_X_STARTEND)
        # Specify the start/end positions of the window address in the X direction by 8 times address unit
        start_x_address = np.uint8(x / 8)
        logging.debug(f"Start X addr: {int(x / 8)} => 0x{start_x_address.tobytes().hex()}")
        self._write_data_byte(start_x_address)
        end_x_address = np.uint8((x + width - 1) / 8)
        logging.debug(f'End X Address: {x + width - 1} => 0x{end_x_address.tobytes().hex()}')
        self._write_data_byte(end_x_address)
        # Specify the start / end positions of the window address in the Y direction by an address unit.
        self._write_command(cmd.SET_RAM_Y_STARTEND)
        start_y_mod = np.uint8(y % 256)
        logging.debug(f"Start Y addr (module): {int(y % 256)} => 0x{start_y_mod.tobytes().hex()}")
        self._write_data_byte(start_y_mod)
        start_y_mult = np.uint8(y / 256)
        logging.debug(f"Start Y addr (multiplier): {int(y / 256)} => 0x{start_y_mult.tobytes().hex()}")
        self._write_data_byte(start_y_mult)
        end_y_mod = np.uint8((y + height - 1) % 256)
        end_y_mult = np.uint8((y + height - 1) / 256)
        logging.debug(f"End Y addr (module): {int((y + height - 1) % 256)} => 0x{end_y_mod.tobytes().hex()}")
        logging.debug(f"End Y addr (multiplier): {int((y + height - 1) / 256)} => 0x{end_y_mult.tobytes().hex()}")
        self._write_data_byte(end_y_mod)
        self._write_data_byte(end_y_mult)
        # X RAM Offset
        self._write_command(cmd.SET_RAM_X_ADDR_COUNTER)
        self._write_data_byte(start_x_address)
        # Y RAM Offset
        self._write_command(cmd.SET_RAM_Y_ADDR_COUNTER)
        self._write_data_byte(start_y_mod)
        self._write_data_byte(start_y_mult)

    def _write_command(self, command: np.uint8):
        logging.debug(f'Sending command: 0x{command.tobytes().hex()}')
        GPIO.output(self._DC, GPIO.LOW)
        GPIO.output(self._CS, GPIO.LOW)
        self._spi.xfer2(command.tobytes())
        GPIO.output(self._CS, GPIO.HIGH)
        GPIO.output(self._DC, GPIO.HIGH)

    def _write_data_byte(self, data: np.uint8):
        logging.debug(f'Sending data byte: 0x{data.tobytes().hex()}')
        GPIO.output(self._CS, GPIO.LOW)
        self._spi.xfer2(data.tobytes())
        GPIO.output(self._CS, GPIO.HIGH)

    def _write_data(self, data: np.array):
        self._spi.writebytes2(data)

    def _update_full(self):
        self._write_command(cmd.DISPLAY_UPDATE_CONTROL_2)
        self._write_data_byte(np.uint8(0xF4))
        self._write_command(cmd.MASTER_ACTIVATION)
        self._wait_while_busy()

    def _update_partial(self):
        self._write_command(cmd.DISPLAY_UPDATE_CONTROL_2)
        self._write_data_byte(np.uint8(0xCC)) #F7
        self._write_command(cmd.MASTER_ACTIVATION)
        self._wait_while_busy()

    def fill(self, color: Color):
        if color == Color.RED:
            self._bw_buffer.clear_screen(BLACK)
            self._red_buffer.clear_screen(RED)
        else:
            self._bw_buffer.clear_screen(color.value)
            self._red_buffer.clear_screen(0)
        self.write_buffer()

    def write_buffer(self):
        self._set_partial_area(0, 0, self.WIDTH, self.HEIGHT)
        # After this command, data entries will be written into the BW RAM until another command is written.
        self._write_command(cmd.WRITE_RAM_BW)
        count = int(self.WIDTH * self.HEIGHT / 8)
        bw_buffer_bytes = self._bw_buffer.serialize()
        for pixel in bw_buffer_bytes:
            self._write_data_byte(pixel)

        self._write_command(cmd.WRITE_RAM_RED)
        red_buffer_bytes = self._red_buffer.serialize()
        self._write_data(red_buffer_bytes)
        # for pixel in red_buffer_bytes:
        #    self._write_data_byte(pixel)
        self._update_partial()

    def write_pixel(self, x: int, y: int, color: Color):
        """
        Writes a single pixel to the display RAM
        :param x: X coordinate of the pixel
        :param y: Y coordinate of the pixel
        :param color: Color of the pixel
        :return:
        """
        # Calculate the byte where to write the bit representing the pixel
        # RAM size is 176x296 bits (22x37 bytes)
        byte_addr = self._bw_buffer.pixel_address(x, y)
        self._set_partial_area(x, y, 1, 1)
        bit = x % 8
        if color is Color.BLACK or color is Color.WHITE:
            # Write the pixel in the BW RAM area and then clear the same pixel in RED RAM area
            self._write_command(cmd.WRITE_RAM_BW)
            self._bw_buffer.draw_pixel(x, y)
            display_byte = self._bw_buffer.get_pixel_byte(x, y)
            self._write_data_byte(display_byte)
            self._red_buffer.clear_pixel(x, y)
            display_byte = self._red_buffer.get_pixel_byte(x, y)
            self._write_command(cmd.WRITE_RAM_RED)
            self._write_data_byte(display_byte)
        else:
            # Set the bit in the RED RAM area
            self._red_buffer.draw_pixel(x, y)
            display_byte = self._red_buffer.get_pixel_byte(x, y)
            self._write_command(cmd.WRITE_RAM_RED)
            self._write_data_byte(display_byte)
        self._update_partial()

    def write_image(self, command: np.uint8, bitmap: np.ndarray, x: int, y: int, w: int, h: int, invert: bool):
        # A pixel is represented by a bit, so all coordinates and dimmensions need to be converted to bytes
        d = np.array(x, y, w, h)
        dimmensions = np.array(np.ceil(d / 8), dtype=np.uint8)
        width_bytes = np.uint8(np.ceil(w / 8))
        x -= x % 8
        w = width_bytes * 8
        # Calculate the actual coordinates of the bounding box, including if the image clips out of the display
        x_box, y_box, w_box, h_box = self._get_visible_bbox(x, y, w, h)
        dx = x_box - x
        dy = y_box - y

    def _get_visible_bbox(self, x, y, w, h):
        x1, y1, w1, h1 = [0] * 4
        if x < 0:
            x1 = 0
        elif x < self.WIDTH:
            x1 = x
        else:
            raise ValueError('Image located completely outside of the display')

        if y < 0:
            y1 = 0
        elif y < self.HEIGHT:
            y1 = y
        else:
            raise ValueError('Image located completely outside of the display')

        if x + w < 0 or x > self.WIDTH:
            w1 = w
        elif x < 0:
            w1 = x + w
        elif x + w > self.WIDTH:
            w1 = self.WIDTH - x
        else:
            w1 = w

        if y + h < 0 or y > self.HEIGHT:
            # the image is completely outside of bounds
            h1 = h
        elif y < 0:
            h1 = y + h
        elif y + h > self.HEIGHT:
            h1 = self.HEIGHT - y
        else:
            h1 = h
        return x1, y1, w1, h1
