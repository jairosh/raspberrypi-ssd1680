import numpy as np
import commands as cmd
import logging
import time
import spidev
import RPi.GPIO as GPIO


class Color:
    BLACK = bytes([0x00])
    WHITE = bytes([0xff])
    RED = bytes([0xff])


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

    def init(self):
        self.reset()
        self._startup()
        self.power_on()

    def power_on(self):
        pass

    def reset(self):
        pass

    def hibernate(self):
        pass

    def end(self):
        self._spi.close()
        GPIO.cleanup()

    def _is_busy(self):
        pass

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
        # Load Waveform LUT
        #   Sense temp (0x18)
        self._write_command(cmd.TEMP_SENSOR_CONTROL)
        self._write_data_byte(np.uint8(0x80))
        #   Load waveform LUT (0x22, 0x20)
        # Display update control
        self._write_command(cmd.DISPLAY_UPDATE_CONTROL)
        self._write_data_byte(np.uint8(0x00))
        self._write_data_byte(np.uint8(0x80))

    def _write_command(self, command: np.uint8):
        pass

    def _write_data_byte(self, data: np.uint8):
        pass

    def _write_data(self, data: np.array, size: int):
        pass


class EPDDisplay:
    """
    Represents a higher level abstraction of a display, operations described here act over a buffer
    """
    def __init__(self, controller: WeAct213):
        self._buffer = np.array([0] * controller.WIDTH * controller.HEIGHT, dtype=np.uint8)
        self.controller = controller

    def init(self):
        self.controller.init()
        pass

    def set_rotation(self, rotation: int):
        pass

    def draw_pixel(self, x: int, y: int, color: Color):
        pass

    def draw_bitmap(self, x: int, y: int, w: int, h: int, color: Color):
        pass

    def draw_text(self, text: str, font: Font, size: int, x: int, y: int):
        pass

    def close(self):
        pass
