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

#QR Code, Imagen se transformo usando https://javl.github.io/image2cpp/
# Se sube la imagen se dejan las opciones de default solamente cambiar el tamaño al deseado y la opción
# 'Scaling' a Scale to fit, revisar en el preview y generar el codigo en "Plain bytes"
# 80x80px
qr_code = np.array([0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
                    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xe0, 0x00,
                    0x00, 0xe0, 0x7f, 0xf1, 0xff, 0x00, 0x00, 0x07, 0xe0, 0x00, 0x00, 0xe0, 0x7f, 0xf1, 0xff, 0x00,
                    0x00, 0x07, 0xe0, 0x00, 0x00, 0xe0, 0x7f, 0xf1, 0xff, 0x00, 0x00, 0x07, 0xe3, 0xff, 0xf8, 0xe3,
                    0xff, 0x8f, 0xc7, 0x1f, 0xff, 0xc7, 0xe3, 0xff, 0xf8, 0xe3, 0xff, 0x8f, 0xc7, 0x1f, 0xff, 0xc7,
                    0xe3, 0xff, 0xf8, 0xe3, 0xff, 0x8f, 0xc7, 0x1f, 0xff, 0xc7, 0xe3, 0x80, 0x38, 0xe0, 0x7e, 0x01,
                    0xff, 0x1c, 0x01, 0xc7, 0xe3, 0x80, 0x38, 0xe0, 0x7e, 0x01, 0xff, 0x1c, 0x01, 0xc7, 0xe3, 0x80,
                    0x38, 0xe0, 0x7e, 0x01, 0xff, 0x1c, 0x01, 0xc7, 0xe3, 0x80, 0x38, 0xff, 0x80, 0x00, 0x07, 0x1c,
                    0x01, 0xc7, 0xe3, 0x80, 0x38, 0xff, 0x80, 0x00, 0x07, 0x1c, 0x01, 0xc7, 0xe3, 0x80, 0x38, 0xff,
                    0x80, 0x00, 0x07, 0x1c, 0x01, 0xc7, 0xe3, 0x80, 0x38, 0xe0, 0x71, 0x81, 0xc7, 0x1c, 0x01, 0xc7,
                    0xe3, 0x80, 0x38, 0xe0, 0x71, 0x81, 0xc7, 0x1c, 0x01, 0xc7, 0xe3, 0x80, 0x38, 0xe0, 0x71, 0x81,
                    0xc7, 0x1c, 0x01, 0xc7, 0xe3, 0xff, 0xf8, 0xff, 0x81, 0x81, 0xff, 0x1f, 0xff, 0xc7, 0xe3, 0xff,
                    0xf8, 0xff, 0x81, 0x81, 0xff, 0x1f, 0xff, 0xc7, 0xe3, 0xff, 0xf8, 0xff, 0x81, 0x81, 0xff, 0x1f,
                    0xff, 0xc7, 0xe0, 0x00, 0x00, 0xe3, 0x8e, 0x71, 0xc7, 0x00, 0x00, 0x07, 0xe0, 0x00, 0x00, 0xe3,
                    0x8e, 0x71, 0xc7, 0x00, 0x00, 0x07, 0xe0, 0x00, 0x00, 0xe3, 0x8e, 0x71, 0xc7, 0x00, 0x00, 0x07,
                    0xff, 0xff, 0xff, 0xff, 0x8e, 0x0e, 0x3f, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x8e, 0x0e,
                    0x3f, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x8e, 0x0e, 0x3f, 0xff, 0xff, 0xff, 0xe3, 0xf0,
                    0x00, 0x03, 0xfe, 0x70, 0x00, 0xfc, 0x70, 0x07, 0xe3, 0xf0, 0x00, 0x03, 0xfe, 0x70, 0x00, 0xfc,
                    0x70, 0x07, 0xe3, 0xf0, 0x00, 0x03, 0xfe, 0x70, 0x00, 0xfc, 0x70, 0x07, 0xe3, 0x80, 0x3f, 0xfc,
                    0x71, 0x80, 0x3f, 0xe0, 0x00, 0x3f, 0xe3, 0x80, 0x3f, 0xfc, 0x71, 0x80, 0x3f, 0xe0, 0x00, 0x3f,
                    0xe3, 0x80, 0x3f, 0xfc, 0x71, 0x80, 0x3f, 0xe0, 0x00, 0x3f, 0xe0, 0x0e, 0x38, 0x1f, 0x81, 0x80,
                    0x38, 0xe3, 0x8f, 0xc7, 0xe0, 0x0e, 0x38, 0x1f, 0x81, 0x80, 0x38, 0xe3, 0x8f, 0xc7, 0xe0, 0x0e,
                    0x38, 0x1f, 0x81, 0x80, 0x38, 0xe3, 0x8f, 0xc7, 0xff, 0x81, 0xc7, 0xe0, 0x71, 0xfe, 0x3f, 0x03,
                    0x80, 0x07, 0xff, 0x81, 0xc7, 0xe0, 0x71, 0xfe, 0x3f, 0x03, 0x80, 0x07, 0xff, 0x81, 0xc7, 0xe0,
                    0x71, 0xfe, 0x3f, 0x03, 0x80, 0x07, 0xff, 0x81, 0xf8, 0x00, 0x7e, 0x7f, 0xc7, 0x03, 0xff, 0xc7,
                    0xff, 0x81, 0xf8, 0x00, 0x7e, 0x7f, 0xc7, 0x03, 0xff, 0xc7, 0xe3, 0xf1, 0xff, 0xff, 0x8e, 0x00,
                    0x38, 0xfc, 0x7e, 0x3f, 0xe3, 0xf1, 0xff, 0xff, 0x8e, 0x00, 0x38, 0xfc, 0x7e, 0x3f, 0xe3, 0xf1,
                    0xff, 0xff, 0x8e, 0x00, 0x38, 0xfc, 0x7e, 0x3f, 0xe0, 0x01, 0xc0, 0x1c, 0x7e, 0x0e, 0x00, 0x1c,
                    0x00, 0x07, 0xe0, 0x01, 0xc0, 0x1c, 0x7e, 0x0e, 0x00, 0x1c, 0x00, 0x07, 0xe0, 0x01, 0xc0, 0x1c,
                    0x7e, 0x0e, 0x00, 0x1c, 0x00, 0x07, 0xe3, 0xf0, 0x3f, 0xe3, 0xfe, 0x7e, 0x07, 0x03, 0x81, 0xc7,
                    0xe3, 0xf0, 0x3f, 0xe3, 0xfe, 0x7e, 0x07, 0x03, 0x81, 0xc7, 0xe3, 0xf0, 0x3f, 0xe3, 0xfe, 0x7e,
                    0x07, 0x03, 0x81, 0xc7, 0xe3, 0x8e, 0x00, 0xe3, 0xfe, 0x0e, 0x00, 0x00, 0x70, 0x3f, 0xe3, 0x8e,
                    0x00, 0xe3, 0xfe, 0x0e, 0x00, 0x00, 0x70, 0x3f, 0xe3, 0x8e, 0x00, 0xe3, 0xfe, 0x0e, 0x00, 0x00,
                    0x70, 0x3f, 0xff, 0xff, 0xff, 0xe3, 0xff, 0x8f, 0xc7, 0xfc, 0x70, 0x3f, 0xff, 0xff, 0xff, 0xe3,
                    0xff, 0x8f, 0xc7, 0xfc, 0x70, 0x3f, 0xff, 0xff, 0xff, 0xe3, 0xff, 0x8f, 0xc7, 0xfc, 0x70, 0x3f,
                    0xe0, 0x00, 0x00, 0xe3, 0xf1, 0x81, 0xc7, 0x1c, 0x7f, 0xc7, 0xe0, 0x00, 0x00, 0xe3, 0xf1, 0x81,
                    0xc7, 0x1c, 0x7f, 0xc7, 0xe0, 0x00, 0x00, 0xe3, 0xf1, 0x81, 0xc7, 0x1c, 0x7f, 0xc7, 0xe3, 0xff,
                    0xf8, 0xe0, 0x00, 0x0e, 0x07, 0xfc, 0x7f, 0xff, 0xe3, 0xff, 0xf8, 0xe0, 0x00, 0x0e, 0x07, 0xfc,
                    0x7f, 0xff, 0xe3, 0xff, 0xf8, 0xe0, 0x00, 0x0e, 0x07, 0xfc, 0x7f, 0xff, 0xe3, 0x80, 0x38, 0xe3,
                    0xff, 0xf0, 0x00, 0x00, 0x7f, 0xff, 0xe3, 0x80, 0x38, 0xe3, 0xff, 0xf0, 0x00, 0x00, 0x7f, 0xff,
                    0xe3, 0x80, 0x38, 0xe3, 0xff, 0xf0, 0x00, 0x00, 0x7f, 0xff, 0xe3, 0x80, 0x38, 0xe3, 0x81, 0xfe,
                    0x00, 0x1f, 0xfe, 0x07, 0xe3, 0x80, 0x38, 0xe3, 0x81, 0xfe, 0x00, 0x1f, 0xfe, 0x07, 0xe3, 0x80,
                    0x38, 0xe3, 0x81, 0xfe, 0x00, 0x1f, 0xfe, 0x07, 0xe3, 0x80, 0x38, 0xff, 0x81, 0x81, 0xf8, 0xfc,
                    0x00, 0x07, 0xe3, 0x80, 0x38, 0xff, 0x81, 0x81, 0xf8, 0xfc, 0x00, 0x07, 0xe3, 0x80, 0x38, 0xff,
                    0x81, 0x81, 0xf8, 0xfc, 0x00, 0x07, 0xe3, 0xff, 0xf8, 0xff, 0x8f, 0xfe, 0x38, 0xe0, 0x70, 0x07,
                    0xe3, 0xff, 0xf8, 0xff, 0x8f, 0xfe, 0x38, 0xe0, 0x70, 0x07, 0xe3, 0xff, 0xf8, 0xff, 0x8f, 0xfe,
                    0x38, 0xe0, 0x70, 0x07, 0xe0, 0x00, 0x00, 0xe0, 0x7e, 0x7f, 0xc0, 0x1f, 0x8f, 0xc7, 0xe0, 0x00,
                    0x00, 0xe0, 0x7e, 0x7f, 0xc0, 0x1f, 0x8f, 0xc7, 0xe0, 0x00, 0x00, 0xe0, 0x7e, 0x7f, 0xc0, 0x1f,
                    0x8f, 0xc7, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
                    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff
                    ], dtype=np.uint8)


def main():
    logging.basicConfig(format='%(asctime)s %(module)s %(levelname)s %(message)s',
                        level=logging.DEBUG)
    logging.info("Initializing display")
    display = raspberrypi_epd.WeAct213(busy=4, reset=17, dc=27, cs=22)
    display.init()
    display.fill(raspberrypi_epd.Color.WHITE)
    display.refresh(False)

    display.set_font('fonts/helvB14.bdf')
    display.draw_text('Orientacion 0', 0, 0, raspberrypi_epd.Color.BLACK)
    # Rota la pantalla 90º y dibuja texto
    display.set_rotation(90)
    display.draw_text('Texto a 90', 35, 0, raspberrypi_epd.Color.RED)
    # Dibuja una linea rotada a 180º
    display.set_rotation(180)
    display.draw_line(0, 0, 121, 0, raspberrypi_epd.Color.BLACK)
    display.draw_line(1, 0, 121, 1, raspberrypi_epd.Color.BLACK)
    display.draw_line(2, 0, 121, 2, raspberrypi_epd.Color.BLACK)
    display.draw_line(3, 0, 121, 3, raspberrypi_epd.Color.RED)
    display.draw_line(4, 0, 121, 4, raspberrypi_epd.Color.RED)
    display.draw_line(5, 0, 121, 5, raspberrypi_epd.Color.RED)
    # Rota a 270º
    display.set_rotation(270)
    # Para centrar se calcula (Display.WIDTH/2-(bitmap.width/2)) y (Display.HEIGHT/2-(bitmap.height/2))
    #                         (125 - 40), (66 - 40) => (85, 26)
    display.draw_bitmap(qr_code, 85, 26, 80, 80, raspberrypi_epd.Color.BLACK)
    display.draw_rectangle(8, 8, 117, 53, raspberrypi_epd.Color.RED)
    display.write_buffer()
    input('Press enter to exit')
    display.close()


if __name__ == '__main__':
    main()
