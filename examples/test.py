import raspberrypi_epd
import logging

# Ejemplo de conexion
# BUSY          GPIO4
# RES           GPIO17
# D/C           GPIO27
# CS            GPIO22
# SCK           GPIO11 (SPI0 SCK)
# SDATA         GPIO10 (SPI0 MOSI)
# GND
# VCC


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.DEBUG)
    display = raspberrypi_epd.SSD1680(busy=4, reset=17, dc=27, cs=22)
    display.init()
    display.clear()
    display.close()


if __name__ == '__main__':
    main()