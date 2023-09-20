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
    display = raspberrypi_epd.WeAct213(busy=4, reset=17, dc=27, cs=22)
    display.init()
    # ----------------------
    # display.set_rotation(1)
    # display.set_font()
    # display.clear(raspberrypi_epd.Color.WHITE)
    display.fill(raspberrypi_epd.Color.RED)
    display.refresh(False)
    input('Display was cleared, press ENTER to continue')
    display.write_pixel(32, 32, raspberrypi_epd.Color.BLACK)
    input('Next point')
    display.write_pixel(61, 125, raspberrypi_epd.Color.WHITE)
    logging.info("Clear command executed")
    input('Press enter to exit')
    display.close()


if __name__ == '__main__':
    main()
