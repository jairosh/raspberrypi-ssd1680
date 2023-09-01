import time
import board
import displayio
import adafruit_ssd1680

displayio.release_displays()

# This pinout works on a Metro M4 and may need to be altered for other boards.
spi = board.SPI()  # Uses SCK and MOSI
epd_cs = board.D22  # board.D9 -> pin.D9 -> Pin(9) -> GPIO.bcm_number(9)
epd_dc = board.D27  # pin.D10
epd_reset = board.D17    # Set to None for FeatherWing
epd_busy = board.D4    # Set to None for FeatherWing

display_bus = displayio.FourWire(
    spi, command=epd_dc, chip_select=epd_cs, reset=epd_reset, baudrate=1000000
)
time.sleep(1)

display = adafruit_ssd1680.SSD1680(
    display_bus,
    width=250,
    height=122,
    busy_pin=epd_busy,
    highlight_color=0xFF0000,
    rotation=270,
)

g = displayio.Group()

# CircuitPython 6 & 7 compatible
f = open("/display-ruler.bmp", "rb")
pic = displayio.OnDiskBitmap(f)
t = displayio.TileGrid(
    pic, pixel_shader=getattr(pic, "pixel_shader", displayio.ColorConverter())
)

# # CircuitPython 7 compatible only
# pic = displayio.OnDiskBitmap("/display-ruler.bmp")
# t = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)

g.append(t)

display.show(g)

display.refresh()
print("refreshed")

time.sleep(120)
