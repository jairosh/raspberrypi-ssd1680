import raspberrypi_epd
import logging
import RPi.GPIO as GPIO
import numpy as np
from bdfparser import Font

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

pattern_bitmap = np.array([0x26, 0xc5, 0x4a, 0x0a, 0x8a, 0xb2, 0xb9, 0x5c, 0x8b, 0x61, 0x4a, 0x92, 0x2a, 0xaa, 0xa1, 0x46,
                       0xe1, 0x21, 0x4a, 0x94, 0x6a, 0x8a, 0x4d, 0x50, 0x30, 0x91, 0x55, 0x31, 0xca, 0x91, 0x59, 0x59,
                       0x9c, 0xda, 0xa5, 0x23, 0x15, 0x05, 0x52, 0x8d, 0xc7, 0x6c, 0x85, 0x46, 0x75, 0x11, 0x42, 0x81,
                       0x71, 0x24, 0x35, 0x9c, 0xc5, 0x3c, 0x2a, 0xa9, 0x18, 0x12, 0x62, 0x31, 0x88, 0x66, 0x2a, 0xaa,
                       0xce, 0x58, 0xc8, 0x67, 0x29, 0xc3, 0x8a, 0xb2, 0xa2, 0xa3, 0x99, 0xcc, 0x2b, 0x18, 0xc5, 0x50,
                       0xa8, 0xa6, 0x33, 0x18, 0x2a, 0x72, 0x75, 0x51, 0x28, 0x8c, 0xe6, 0x72, 0x94, 0xc3, 0x15, 0x63,
                       0x2a, 0xa9, 0x84, 0xe2, 0xc5, 0x89, 0xc5, 0x0e, 0x2b, 0x43, 0x31, 0x8a, 0x71, 0x28, 0x6a, 0x98,
                       0x55, 0x4e, 0x1c, 0x2a, 0x18, 0x6a, 0x2a, 0x33, 0x15, 0x58, 0xc6, 0x2a, 0xce, 0x65, 0x0a, 0xe6,
                       0x01, 0x50, 0x73, 0x8a, 0xe3, 0x15, 0x6a, 0x8c, 0xf1, 0x42, 0x18, 0xea, 0x39, 0xc5, 0x6a, 0x38,
                       0x3a, 0xa8, 0x8e, 0x76, 0x8c, 0x75, 0x54, 0x62, 0x02, 0x95, 0x43, 0x14, 0xc7, 0x3a, 0x94, 0xca,
                       0xe2, 0x95, 0x51, 0xc5, 0x11, 0x8a, 0x95, 0x8a, 0x7a, 0x94, 0xd4, 0x15, 0x14, 0xe2, 0x94, 0x2a,
                       0x05, 0x14, 0x95, 0x35, 0x54, 0x22, 0xa8, 0x75, 0xa5, 0x4a, 0xa8, 0x65, 0x55, 0x8d, 0x4b, 0x35,
                       0x95, 0x6a, 0x29, 0xc5, 0x28, 0x19, 0x49, 0x85, 0x95, 0x0a, 0x23, 0x15, 0x2a, 0x71, 0x48, 0xe1,
                       0x15, 0x08, 0x26, 0x75, 0x28, 0xc4, 0x2a, 0x30, 0x4a, 0x35, 0x0c, 0xc1, 0x29, 0x9c, 0xa3, 0x9c,
                       0x22, 0x65, 0x31, 0x98, 0x13, 0x30, 0x80, 0xc7, 0x21, 0xc5, 0x67, 0x0e, 0x54, 0x62, 0x98, 0x71,
                       0x2c, 0x12, 0x8c, 0x43, 0x11, 0xca, 0x33, 0x18, 0xa7, 0x32, 0x99, 0x51, 0xc3, 0x14, 0x66, 0x0e,
                       0x51, 0x82, 0xb1, 0x5c, 0x62, 0x55, 0xcc, 0xa3, 0x50, 0xe2, 0x81, 0x47, 0x38, 0xd5, 0x19, 0xa8,
                       0x56, 0x31, 0x4a, 0xa1, 0x8c, 0x54, 0x70, 0x54, 0x2b, 0x9d, 0x4a, 0xa8, 0xe7, 0x10, 0xc0, 0x55,
                       0xa8, 0xc5, 0x4a, 0xaa, 0x31, 0xa9, 0x8b, 0x52, 0x28, 0x71, 0x4a, 0x55, 0x1c, 0x2b, 0x15, 0x52,
                       0x29, 0x18, 0x95, 0x55, 0x06, 0x28, 0x15, 0x52, 0x95, 0x48, 0x95, 0x45, 0x23, 0xa8, 0x94, 0xaa,
                       0xd5, 0x42, 0x95, 0x45, 0x50, 0x52, 0x94, 0xa4, 0x14, 0x46, 0x95, 0x95, 0x52, 0x51, 0x4a, 0xa0,
                       0x96, 0x18, 0x2a, 0x2a, 0x56, 0x54, 0x4a, 0xa3, 0x8b, 0x83, 0x28, 0xea, 0x48, 0x56, 0x0a, 0x46,
                       0x28, 0xe6, 0x29, 0x8a, 0x28, 0x03, 0x85, 0x0c, 0x6e, 0x70, 0x2b, 0x2a, 0x2a, 0xa8, 0xc5, 0x39,
                       0xc3, 0x1c, 0x26, 0x54, 0xac, 0xae, 0x70, 0x63, 0x91, 0xc6, 0x10, 0xd5, 0x94, 0xa3, 0x18, 0xce,
                       0x34, 0x73, 0x83, 0x84, 0x14, 0xa1, 0xc1, 0x98, 0xe5, 0x18, 0xc6, 0x30, 0xd4, 0x54, 0x66, 0x31,
                       0x85, 0x0e, 0x70, 0x18, 0x8a, 0x55, 0x0c, 0xe1, 0x2a, 0xa3, 0x19, 0xce, 0x2a, 0x55, 0x19, 0x8a,
                       0x2a, 0xa9, 0xc0, 0x63, 0x0a, 0x4a, 0x73, 0x2a, 0xaa, 0xa0, 0x6a, 0x39, 0xcc, 0x2a, 0xc6, 0x6a,
                       0x4a, 0x96, 0x35, 0x0c, 0x74, 0x0a, 0x98, 0xc0, 0x4a, 0x54, 0x85, 0x47, 0x11, 0x0a, 0x33, 0x14,
                       0x55, 0x51, 0x85, 0x51, 0x87, 0x35, 0x64, 0x55, 0x55, 0x53, 0x15, 0x28, 0xcc, 0x65, 0x01, 0xd5,
                       0x05, 0xaa, 0x25, 0x2a, 0x19, 0xc5, 0x31, 0x14, 0xc0, 0x28, 0xaa, 0xaa, 0x33, 0x05, 0x1c, 0x2a,
                       0xfe, 0x28, 0xaa, 0xa8, 0xc6, 0x2a, 0x87, 0x2b, 0x0f, 0xac, 0xaa, 0x95, 0x9c, 0xaa, 0xb1, 0x89,
                       0x80, 0x55, 0x4a, 0x15, 0x30, 0x56, 0x98, 0xe0, 0xfc, 0x14, 0x54, 0x54, 0x61, 0x54, 0x4e, 0x31],
                       dtype=np.uint8)


def main():
    logging.basicConfig(format='%(asctime)s %(module)s %(levelname)s %(message)s',
                        level=logging.DEBUG)
    logging.info("Initializing display")
    display = raspberrypi_epd.WeAct213(busy=4, reset=17, dc=27, cs=22)
    display.init()
    display.fill(raspberrypi_epd.Color.WHITE)
    display.refresh(False)
    font = Font('fonts/helvB14.bdf')
    display.draw_text('Prueba', 0, 0, font, raspberrypi_epd.Color.BLACK)
    display.refresh()
    input('Display was cleared, press ENTER to draw black pixel')
    # display.write_pixel(32, 32, raspberrypi_epd.Color.BLACK)
    input('Next WHITE pixel')
    # display.write_pixel(61, 125, raspberrypi_epd.Color.WHITE)
    input("Draw BLACK line")
    # display.write_line(22, 125, 100, 125, raspberrypi_epd.Color.BLACK)
    input("Draw WHITE line")
    display.draw_line(61, 50, 61, 200, raspberrypi_epd.Color.WHITE)
    display.draw_bitmap(pattern_bitmap, 0, 0, 64, 64, raspberrypi_epd.Color.BLACK)
    display.write_buffer()
    input('Press enter to exit')
    display.close()


if __name__ == '__main__':
    main()
