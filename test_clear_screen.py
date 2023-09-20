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
    color_option = input('Pick color to clear the screen:\n0 = black\n1 = white\n2 = red\n')
    if color_option in ['0', '1', '2']:
        color = raspberrypi_epd.Color.RED
        if color_option == '0':
            logging.debug('Filling with BLACK')
            color = raspberrypi_epd.Color.BLACK
        elif color_option == '1':
            logging.debug('Filling with WHITE')
            color = raspberrypi_epd.Color.WHITE
        else:
            logging.debug('Filling with RED')
        display.fill(color)
        display.refresh(False)
    else:
        logging.info('Invalid color option')
    display.close()


if __name__ == '__main__':
    main()
