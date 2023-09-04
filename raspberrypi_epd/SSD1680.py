import logging
import time
import spidev
import RPi.GPIO as GPIO
import raspberrypi_epd.commands as commands


SPI_BUS = 0
SPI_DEVICE = 1


class Color:
    BLACK = bytes([0x00])
    WHITE = bytes([0xff])
    RED = bytes([0xff])


class SSD1680:
    """
    Class to handle connection to an e-Paper Display with a SSD1680 controller
    """
    WIDTH = 250
    HEIGHT = 122

    def __init__(self, dc: int, cs: int, busy: int, reset: int):
        self.spi = spidev.SpiDev()
        self.configure_spi()
        self._spi_initialized = True
        self.DC = dc
        self.CS = cs
        self.RESET = reset
        # GPIO.setup([self.DC, self.CS, self.RESET], GPIO.OUT)
        GPIO.setup(self.DC, GPIO.OUT)
        GPIO.setup(self.CS, GPIO.OUT)
        GPIO.setup(self.RESET, GPIO.OUT)
        GPIO.output(self.RESET, GPIO.HIGH)
        self.BUSY = busy
        GPIO.setup(self.BUSY, GPIO.IN)
        self.init()

    def configure_spi(self):
        self.spi.open(SPI_BUS, SPI_DEVICE)
        # Set SPI speed and mode
        self.spi.max_speed_hz = 500000
        self.spi.mode = 0

    def __write_command(self, cmd: bytes):
        logging.debug(f'Sending Command: 0x{cmd.hex()}')
        if self._spi_initialized:
            GPIO.output(self.DC, GPIO.LOW)
            GPIO.output(self.CS, GPIO.LOW)
            self.spi.xfer2(cmd)
            GPIO.output(self.CS, GPIO.HIGH)
            GPIO.output(self.DC, GPIO.HIGH)
            time.sleep(0.005)

    def __write_data(self, data: bytes):
        logging.debug(f'Sending Data: 0x{data.hex()}')
        if self._spi_initialized:
            GPIO.output(self.CS, GPIO.LOW)
            self.spi.xfer2(data)
            GPIO.output(self.CS, GPIO.HIGH)
            time.sleep(0.005)

    def draw_pixel(self, x: int, y: int):
        pass

    def clear(self, color: bytes = Color.BLACK):
        self.__set_partial_ram_area(0, 0, self.WIDTH, self.HEIGHT)
        # After this command, data entries will be written into the BW RAM until another command is written.
        self.__write_command(commands.WRITE_RAM_BW)
        count = int(self.WIDTH * self.HEIGHT / 8)
        for i in range(count):
            self.__write_data(color)
        self.__write_command(commands.WRITE_RAM_RED)
        for i in range(count):
            negated_color = bytes([color[0] ^ 0xFF])
            self.__write_data(negated_color)
        self.__update_partial()

    def __update_partial(self):
        self.__write_command(commands.DISPLAY_UPDATE_CONTROL_2)
        self.__write_data(bytes([0xF7]))
        self.__write_command(commands.MASTER_ACTIVATION)

    def __wait_idle(self):
        while True:
            busy = GPIO.input(self.BUSY)
            if busy == 0:
                break
            time.sleep(0.005)

    def __init_display(self):
        # Send init code
        #   Set gate driver output (0x01)
        self.__write_command(commands.DRIVER_OUTPUT_CONTROL)
        self.__write_data(bytes([0x27]))
        self.__write_data(bytes([0x01]))
        self.__write_data(bytes([0x00]))
        #   Set display RAM size (0x11, 0x44, 0x45)
        self.__write_command(commands.DATA_ENTRY_MODE)
        self.__write_data(bytes([0x03]))
        #   Set panel border (0x3C)
        self.__write_command(commands.BORDER_WAVEFORM_CONTROL)
        self.__write_data(bytes([0x05]))
        # Load Waveform LUT
        #   Sense temp (0x18)
        self.__write_command(commands.TEMP_SENSOR_CONTROL)
        self.__write_data(bytes([0x80]))
        #   Load waveform LUT (0x22, 0x20)
        # Display update control
        self.__write_command(commands.DISPLAY_UPDATE_CONTROL)
        self.__write_data(bytes([0x00]))
        self.__write_data(bytes([0x80]))

    def __set_partial_ram_area(self, x, y, width, height):
        self.__write_command(commands.SET_RAM_X_STARTEND)
        # Specify the start/end positions of the window address in the X direction by 8 times address unit
        start_x_address = bytes([int(x / 8)])
        logging.debug(f"Start X addr: {int(x / 8)} => 0x{start_x_address.hex()}")
        self.__write_data(start_x_address)
        end_x_address = bytes([int((x + width - 1) / 8)])
        logging.debug(f'End X Address: {x + width - 1} => 0x{end_x_address.hex()}')
        self.__write_data(end_x_address)
        # Specify the start / end positions of the window address in the Y direction by an address unit.
        self.__write_command(commands.SET_RAM_Y_STARTEND)
        start_y_mod = bytes([int(y % 256)])
        logging.debug(f"Start Y addr (module): {int(y % 256)} => 0x{start_y_mod.hex()}")
        self.__write_data(start_y_mod)
        start_y_mult = bytes([int(y / 256)])
        logging.debug(f"Start Y addr (multiplier): {int(y / 256)} => 0x{start_y_mult.hex()}")
        self.__write_data(start_y_mult)
        end_y_mod = bytes([int((y + height - 1) % 256)])
        end_y_mult = bytes([int((y + height - 1) / 256)])
        logging.debug(f"End Y addr (module): {int((y + height - 1) % 256)} => 0x{end_y_mod.hex()}")
        logging.debug(f"End Y addr (multiplier): {int((y + height - 1) / 256)} => 0x{end_y_mult.hex()}")
        self.__write_data(end_y_mod)
        self.__write_data(end_y_mult)
        # X RAM Offset
        self.__write_command(commands.SET_RAM_X_ADDR_COUNTER)
        self.__write_data(start_x_address)
        # Y RAM Offset
        self.__write_command(commands.SET_RAM_Y_ADDR_COUNTER)
        self.__write_data(start_y_mod)
        self.__write_data(start_y_mult)

    def power_on(self):
        # Power on
        self.__write_command(commands.DISPLAY_UPDATE_CONTROL_2)
        self.__write_data(bytes([0xf8]))
        self.__write_command(commands.MASTER_ACTIVATION)
        self.__wait_idle()

    def reset(self):
        # HW Reset
        GPIO.output(self.RESET, GPIO.LOW)
        time.sleep(0.005)
        GPIO.output(self.RESET, GPIO.HIGH)
        # SW Reset (command 0x12)
        self.__write_command(commands.SW_RESET)
        self.__wait_idle()
        # Wait 10ms
        time.sleep(0.01)
        #   Wait BUSY low
        self.__wait_idle()

    def init(self):
        self.reset()
        self.__init_display()
        self.power_on()

    def close(self):
        self.spi.close()
        self._spi_initialized = False
        GPIO.cleanup()

    def power_off(self):
        """
        This method should be called for deep sleep
        :return:
        """
        # Deep sleep (0x10)
        pass
