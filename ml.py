import numpy as np
import RPi.GPIO as GPIO
import raspberrypi_epd
import logging
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


# 72x72px
rpi_gh = np.array([0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
                0xff, 0xff, 0xc0, 0x00, 0xe7, 0xe7, 0xe0, 0x1e, 0x1f, 0x00, 0x03, 0xc0, 0x00, 0xe7, 0xe7, 0xe0,
                0x1e, 0x1f, 0x00, 0x03, 0xcf, 0xfc, 0xff, 0x9f, 0x99, 0xe0, 0x07, 0x3f, 0xf3, 0xcf, 0xfc, 0xff,
                0x9f, 0x99, 0xe0, 0x07, 0x3f, 0xf3, 0xcc, 0x0c, 0xe1, 0xe1, 0xf8, 0x7e, 0x1f, 0x30, 0x33, 0xcc,
                0x0c, 0xe1, 0xe1, 0xf8, 0x7e, 0x1f, 0x30, 0x33, 0xcc, 0x0c, 0xe6, 0x00, 0x7f, 0x86, 0x07, 0x30,
                0x33, 0xcc, 0x0c, 0xe6, 0x00, 0x7f, 0x86, 0x07, 0x30, 0x33, 0xcc, 0x0c, 0xff, 0xf8, 0x61, 0xe7,
                0x9f, 0x30, 0x33, 0xcc, 0x0c, 0xff, 0xf8, 0x61, 0xe7, 0x9f, 0x30, 0x33, 0xcf, 0xfc, 0xe1, 0xe6,
                0x67, 0x87, 0xe7, 0x3f, 0xf3, 0xcf, 0xfc, 0xe1, 0xe6, 0x67, 0x87, 0xe7, 0x3f, 0xf3, 0xc0, 0x00,
                0xe6, 0x66, 0x66, 0x66, 0x67, 0x00, 0x03, 0xc0, 0x00, 0xe6, 0x66, 0x66, 0x66, 0x67, 0x00, 0x03,
                0xff, 0xff, 0xe0, 0x1f, 0x98, 0x00, 0x1f, 0xff, 0xff, 0xff, 0xff, 0xe0, 0x1f, 0x98, 0x00, 0x1f,
                0xff, 0xff, 0xff, 0xff, 0xc0, 0x1f, 0x98, 0x00, 0x1f, 0xff, 0xff, 0xf3, 0x30, 0x00, 0x7e, 0x67,
                0xf8, 0x78, 0x0c, 0x33, 0xf3, 0x30, 0x00, 0x7e, 0x67, 0xf8, 0x78, 0x0c, 0x33, 0xc3, 0x0f, 0x00,
                0x78, 0x00, 0x67, 0xe0, 0x0f, 0xc3, 0xc3, 0x0f, 0x00, 0x78, 0x00, 0x67, 0xe0, 0x0f, 0xc3, 0xfc,
                0xcc, 0x1e, 0x19, 0xfe, 0x07, 0xe0, 0x03, 0x33, 0xfc, 0xcc, 0x1e, 0x19, 0xfe, 0x07, 0xe0, 0x03,
                0x33, 0xff, 0x0f, 0x19, 0x9f, 0xe7, 0xe0, 0x78, 0x30, 0xff, 0xff, 0x0f, 0x19, 0x9f, 0xe7, 0xe0,
                0x78, 0x30, 0xff, 0xf3, 0x00, 0xfe, 0x18, 0x1e, 0x18, 0x18, 0x0c, 0xf3, 0xf3, 0x00, 0xfe, 0x18,
                0x1e, 0x18, 0x18, 0x0c, 0xf3, 0xf0, 0xcf, 0xe6, 0x01, 0xff, 0x9e, 0x67, 0x30, 0x03, 0xf0, 0xcf,
                0xe6, 0x01, 0xff, 0x9e, 0x67, 0x30, 0x03, 0xcf, 0x3c, 0xff, 0x80, 0x7e, 0x61, 0x80, 0x0c, 0x0f,
                0xcf, 0x3c, 0xff, 0x80, 0x7e, 0x61, 0x80, 0x0c, 0x0f, 0xc3, 0x03, 0xff, 0xe0, 0x67, 0x99, 0xff,
                0x0c, 0xcf, 0xc3, 0x03, 0xff, 0xe0, 0x67, 0x99, 0xff, 0x0c, 0xcf, 0xf0, 0x3c, 0xf8, 0x66, 0x61,
                0x80, 0x67, 0x33, 0xcf, 0xf0, 0x3c, 0xf8, 0x66, 0x61, 0x80, 0x67, 0x33, 0xcf, 0xc3, 0x0f, 0x00,
                0x61, 0xe0, 0x7f, 0x80, 0xcc, 0xff, 0xc3, 0x0f, 0x00, 0x61, 0xe0, 0x7f, 0x80, 0xcc, 0xff, 0xff,
                0xcc, 0x1f, 0x87, 0xf8, 0x7f, 0xe7, 0x3f, 0x03, 0xff, 0xcc, 0x1f, 0x87, 0xf8, 0x7f, 0xe7, 0x3f,
                0x03, 0xcf, 0x3f, 0xe1, 0xff, 0xf8, 0x01, 0x87, 0x0f, 0xc3, 0xcf, 0x3f, 0xe1, 0xff, 0xf8, 0x01,
                0x87, 0x0f, 0xc3, 0xc0, 0xcc, 0xfe, 0x1f, 0x87, 0x81, 0x98, 0xcf, 0xc3, 0xc0, 0xcc, 0xfe, 0x1f,
                0x87, 0x81, 0x98, 0xcf, 0xc3, 0xff, 0xcf, 0x01, 0xe6, 0x19, 0xf8, 0x60, 0x3f, 0x03, 0xff, 0xcf,
                0x01, 0xe6, 0x19, 0xf8, 0x60, 0x3f, 0x03, 0xc0, 0x3c, 0x1e, 0x01, 0x9f, 0x81, 0xe7, 0x0c, 0xf3,
                0xc0, 0x3c, 0x1e, 0x01, 0x9f, 0x81, 0xe7, 0x0c, 0xf3, 0xf0, 0xc3, 0x1e, 0x66, 0x78, 0x18, 0x1f,
                0xcc, 0xcf, 0xf0, 0xc3, 0x1e, 0x66, 0x78, 0x18, 0x1f, 0xcc, 0xcf, 0xcf, 0x30, 0xf8, 0x66, 0x00,
                0x61, 0xe0, 0x00, 0xcf, 0xcf, 0x30, 0xf8, 0x66, 0x00, 0x61, 0xe0, 0x00, 0xcf, 0xff, 0xff, 0xe0,
                0x67, 0x87, 0x98, 0x63, 0xf0, 0xf3, 0xff, 0xff, 0xe0, 0x67, 0x87, 0x98, 0x67, 0xf0, 0xf3, 0xff,
                0xff, 0xe0, 0x67, 0x87, 0x98, 0x67, 0xf0, 0xf3, 0xc0, 0x00, 0xe7, 0xf9, 0x86, 0x60, 0x67, 0x30,
                0x0f, 0xc0, 0x00, 0xe7, 0xf9, 0x86, 0x60, 0x67, 0x30, 0x0f, 0xcf, 0xfc, 0xe7, 0xff, 0xfe, 0x00,
                0x67, 0xf3, 0xc3, 0xcf, 0xfc, 0xe7, 0xff, 0xfe, 0x00, 0x67, 0xf3, 0xc3, 0xcc, 0x0c, 0xf9, 0x86,
                0x7e, 0x60, 0x60, 0x00, 0xc3, 0xcc, 0x0c, 0xf9, 0x86, 0x7e, 0x60, 0x60, 0x00, 0xc3, 0xcc, 0x0c,
                0xe6, 0x19, 0xe6, 0x7e, 0x1f, 0x33, 0xcf, 0xcc, 0x0c, 0xe6, 0x19, 0xe6, 0x7e, 0x1f, 0x33, 0xcf,
                0xcc, 0x0c, 0xfe, 0x61, 0xf9, 0xf9, 0xff, 0xf3, 0xf3, 0xcc, 0x0c, 0xfe, 0x61, 0xf9, 0xf9, 0xff,
                0xf3, 0xf3, 0xcf, 0xfc, 0xe7, 0x87, 0xe6, 0x19, 0xe0, 0xff, 0xff, 0xcf, 0xfc, 0xe7, 0x87, 0xe6,
                0x19, 0xe0, 0xff, 0xff, 0xc0, 0x00, 0xfe, 0x61, 0xe7, 0xf9, 0xe0, 0xf0, 0xcf, 0xc0, 0x00, 0xfe,
                0x61, 0xe7, 0xf9, 0xe0, 0xf0, 0xcf, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
                0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff], dtype=np.uint8)

# 72x72px
weact_gh = np.array([0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
                    0xff, 0xff, 0xc0, 0x00, 0xe0, 0x7f, 0xe6, 0x61, 0x9f, 0x00, 0x03, 0xc0, 0x00, 0xe0, 0x7f, 0xe6,
                    0x61, 0x9f, 0x00, 0x03, 0xcf, 0xfc, 0xe7, 0xfe, 0x60, 0x7f, 0x87, 0x3f, 0xf3, 0xcf, 0xfc, 0xe7,
                    0xfe, 0x60, 0x7f, 0x87, 0x3f, 0xf3, 0xcc, 0x0c, 0xf9, 0xe0, 0x66, 0x06, 0x67, 0x30, 0x33, 0xcc,
                    0x0c, 0xf9, 0xe0, 0x66, 0x06, 0x67, 0x30, 0x33, 0xcc, 0x0c, 0xe0, 0x7f, 0xf9, 0xe6, 0x7f, 0x30,
                    0x33, 0xcc, 0x0c, 0xe0, 0x7f, 0xf9, 0xe6, 0x7f, 0x30, 0x33, 0xcc, 0x0c, 0xf9, 0xf9, 0xe1, 0x9f,
                    0xe7, 0x30, 0x33, 0xcc, 0x0c, 0xf9, 0xf9, 0xe1, 0x9f, 0xe7, 0x30, 0x33, 0xcf, 0xfc, 0xf9, 0xe6,
                    0x07, 0x98, 0x67, 0x3f, 0xf3, 0xcf, 0xfc, 0xf9, 0xe6, 0x07, 0x98, 0x67, 0x3f, 0xf3, 0xc0, 0x00,
                    0xe6, 0x66, 0x66, 0x66, 0x67, 0x00, 0x03, 0xc0, 0x00, 0xe6, 0x66, 0x66, 0x66, 0x67, 0x00, 0x03,
                    0xff, 0xff, 0xe7, 0xe7, 0x80, 0x7f, 0x87, 0xff, 0xff, 0xff, 0xff, 0xe7, 0xe7, 0x80, 0x7f, 0x87,
                    0xff, 0xff, 0xff, 0xff, 0xe7, 0xe7, 0x80, 0x7f, 0x87, 0xff, 0xff, 0xcc, 0x30, 0x18, 0x7f, 0x80,
                    0x18, 0x67, 0x3c, 0xc3, 0xcc, 0x30, 0x18, 0x7f, 0x80, 0x18, 0x67, 0x3c, 0xc3, 0xf3, 0xcf, 0x00,
                    0x79, 0xe0, 0x01, 0x9f, 0x0c, 0x3f, 0xf3, 0xcf, 0x00, 0x79, 0xe0, 0x01, 0x9f, 0x0c, 0x3f, 0xcc,
                    0x00, 0x1e, 0x79, 0xf8, 0x7f, 0x98, 0x00, 0xc3, 0xcc, 0x00, 0x1e, 0x79, 0xf8, 0x7f, 0x98, 0x00,
                    0xc3, 0xf0, 0x3f, 0x06, 0x7f, 0xff, 0xe7, 0xff, 0xcc, 0xff, 0xf0, 0x3f, 0x06, 0x7f, 0xff, 0xe7,
                    0xff, 0xcc, 0xff, 0xff, 0xf0, 0x1f, 0xe6, 0x01, 0xfe, 0x00, 0xf0, 0xcf, 0xff, 0xf0, 0x1f, 0xe6,
                    0x01, 0xfe, 0x00, 0xf0, 0xcf, 0xc3, 0x03, 0x06, 0x60, 0x79, 0x98, 0x07, 0xcc, 0xcf, 0xc3, 0x03,
                    0x06, 0x60, 0x79, 0x98, 0x07, 0xcc, 0xcf, 0xf3, 0xf0, 0x18, 0x1e, 0x79, 0x81, 0xff, 0x30, 0xff,
                    0xf3, 0xf0, 0x18, 0x1e, 0x79, 0x81, 0xff, 0x30, 0xff, 0xff, 0xc3, 0x18, 0x1f, 0x9f, 0x81, 0x98,
                    0x3c, 0x3f, 0xff, 0xc3, 0x18, 0x1f, 0x9f, 0x81, 0x98, 0x3c, 0x3f, 0xcc, 0x3c, 0x01, 0xfe, 0x7e,
                    0x18, 0x78, 0x30, 0x3f, 0xcc, 0x3c, 0x01, 0xfe, 0x7e, 0x18, 0x78, 0x30, 0x3f, 0xf0, 0x0f, 0x19,
                    0x9e, 0x1e, 0x06, 0x00, 0x30, 0xc3, 0xf0, 0x0f, 0x19, 0x9e, 0x1e, 0x06, 0x00, 0x30, 0xc3, 0xf0,
                    0xc0, 0xe1, 0xe1, 0x87, 0xe1, 0xe0, 0xc3, 0x0f, 0xf0, 0xc0, 0xe1, 0xe1, 0x87, 0xe1, 0xe0, 0xc3,
                    0x0f, 0xcc, 0x33, 0xe1, 0xff, 0xe0, 0x1f, 0x87, 0x33, 0xcf, 0xcc, 0x33, 0xe1, 0xff, 0xe0, 0x1f,
                    0x87, 0x33, 0xcf, 0xcf, 0xfc, 0x06, 0x7e, 0x67, 0xf9, 0xff, 0xcc, 0x3f, 0xcf, 0xfc, 0x06, 0x7e,
                    0x67, 0xf9, 0xff, 0xcc, 0x3f, 0xc3, 0xc3, 0x1e, 0x18, 0x06, 0x01, 0x87, 0x3f, 0x33, 0xc3, 0xc3,
                    0x1e, 0x18, 0x06, 0x01, 0x87, 0x3f, 0x33, 0xfc, 0xc0, 0x1e, 0x06, 0x18, 0x79, 0x80, 0x03, 0x03,
                    0xfc, 0xc0, 0x1e, 0x06, 0x18, 0x79, 0x80, 0x03, 0x03, 0xf0, 0x0f, 0xe6, 0x61, 0x9f, 0x87, 0x87,
                    0x30, 0xf3, 0xf0, 0x0f, 0xe6, 0x61, 0x9f, 0x87, 0x87, 0x30, 0xf3, 0xcf, 0x0c, 0x1e, 0x1e, 0x67,
                    0x9e, 0x00, 0x00, 0xcf, 0xcf, 0x0c, 0x1e, 0x1e, 0x67, 0x9e, 0x00, 0x00, 0xcf, 0xff, 0xff, 0xe7,
                    0xff, 0x86, 0x07, 0xe3, 0xf0, 0xc3, 0xff, 0xff, 0xe7, 0xff, 0x86, 0x07, 0xe7, 0xf0, 0xc3, 0xff,
                    0xff, 0xe7, 0xff, 0x86, 0x07, 0xe7, 0xf0, 0xc3, 0xc0, 0x00, 0xe1, 0x86, 0x60, 0x07, 0x87, 0x33,
                    0xff, 0xc0, 0x00, 0xe1, 0x86, 0x60, 0x07, 0x87, 0x33, 0xff, 0xcf, 0xfc, 0xe0, 0x67, 0x80, 0x60,
                    0x07, 0xf0, 0x03, 0xcf, 0xfc, 0xe0, 0x67, 0x80, 0x60, 0x07, 0xf0, 0x03, 0xcc, 0x0c, 0xf9, 0xe7,
                    0xe0, 0x00, 0x00, 0x03, 0x0f, 0xcc, 0x0c, 0xf9, 0xe7, 0xe0, 0x00, 0x00, 0x03, 0x0f, 0xcc, 0x0c,
                    0xe7, 0x9e, 0x67, 0x81, 0x9f, 0xcc, 0xf3, 0xcc, 0x0c, 0xe7, 0x9e, 0x67, 0x81, 0x9f, 0xcc, 0xf3,
                    0xcc, 0x0c, 0xe1, 0xff, 0x80, 0x7e, 0x7f, 0x0f, 0x3f, 0xcc, 0x0c, 0xe1, 0xff, 0x80, 0x7e, 0x7f,
                    0x0f, 0x3f, 0xcf, 0xfc, 0xf8, 0x1f, 0xf8, 0x06, 0x07, 0xc3, 0xf3, 0xcf, 0xfc, 0xf8, 0x1f, 0xf8,
                    0x06, 0x07, 0xc3, 0xf3, 0xc0, 0x00, 0xe0, 0x06, 0x78, 0x19, 0x9f, 0xf0, 0xff, 0xc0, 0x00, 0xe0,
                    0x06, 0x78, 0x19, 0x9f, 0xf0, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
                    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff], dtype=np.uint8)


def test_drawing():
    """
    Para usar unicamente la renderizacion local hay que extraer buffer.py y localrender.py
    debido a que la dependencia RPi.GPIO dará problemas
    :return:
    """
    buffer = raspberrypi_epd.DisplayBuffer(128, 250, bg=0, fg=1)
    buffer.clear_screen(0)
    buffer.rotate(90)
    buffer.draw_bitmap(rpi_gh, 27, 35, 72, 72, 1)
    buffer.draw_bitmap(weact_gh, 151, 35, 72, 72, 1)
    font = Font('fonts/helvB14.bdf')
    buffer.draw_text('Raspberry', font, 10, 0, 1)
    buffer.draw_text('Arduino', font, 150, 0, 1)
    buffer.rotate(0)
    font = Font('fonts/spleen-8x16.bdf')
    buffer.draw_text("Código de", font, 20, 115, 1)
    buffer.draw_text("ejemplo", font, 30, 131, 1)
    img = raspberrypi_epd.Render(128, 250, buffer.serialize())
    img.render()
    img.show()


def draw():
    display = raspberrypi_epd.WeAct213(busy=4, reset=17, dc=27, cs=22)
    display.init()
    display.fill(raspberrypi_epd.Color.WHITE)
    display.refresh(False)
    display.set_rotation(90)
    display.draw_bitmap(rpi_gh, 27, 35, 72, 72, raspberrypi_epd.Color.BLACK)
    display.draw_bitmap(weact_gh, 151, 35, 72, 72, raspberrypi_epd.Color.BLACK)
    display.set_font('fonts/helvB14.bdf')
    display.draw_text('Raspberry', 10, 0, raspberrypi_epd.Color.BLACK)
    display.draw_text('Arduino', 150, 0, raspberrypi_epd.Color.BLACK)
    display.set_rotation(0)
    display.set_font('fonts/spleen-8x16.bdf')
    display.draw_text("Código de",  20, 115, raspberrypi_epd.Color.RED)
    display.draw_text("ejemplo",  30, 131, raspberrypi_epd.Color.RED)
    display.write_buffer()
    display.close()


def main():
    logging.basicConfig(format='%(asctime)s %(module)s %(levelname)s %(message)s', level=logging.DEBUG)
    logging.info("Initializing display")
    # test_drawing()
    draw()


if __name__ == '__main__':
    main()
