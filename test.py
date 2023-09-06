import raspberrypi_epd
import logging
import RPi.GPIO as GPIO

# Ejemplo de conexion
# BUSY          GPIO4
# RES           GPIO17
# D/C           GPIO27
# CS            GPIO22
# SCK           GPIO11 (SPI0 SCK)
# SDATA         GPIO10 (SPI0 MOSI)
# GND
# VCC
GPIO.setmode(GPIO.BCM)


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.DEBUG)
    logging.info("Initializing display")
    display = raspberrypi_epd.SSD1680(busy=4, reset=17, dc=27, cs=22)
    display.init()
    # ----------------------
    # display.set_rotation(1)
    # display.set_font()
    # display.set_text_color(raspberrypi_epd.Color.BLACK)
    # tx, ty, tw, th = display.get_text_bounds("Hello world!")
    # Center the bounding box
    # x = ((display.width() - tw) / 2) - tx
    # y = ((display.height() - th) / 2) - ty
    # display.set_full_window()
    # display.set_first_page()
    display.clear(raspberrypi_epd.Color.WHITE)
    logging.info("Clear command executed")
    input('Press enter to exit')
    display.close()


if __name__ == '__main__':
    main()
