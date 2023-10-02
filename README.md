SSD1680 for RaspberryPi
=======================

This code is made to drive an ePaper Display from a Raspberry Pi with Python. This is independent of 
MicroPython/CircuitPython and only uses a small set of dependencies.

Code is semiported from the Arduino library [GxEPD2](https://github.com/ZinggJM/GxEPD2) 

Only Tested with a WeAct Studio 2.13" three-color e-paper display, but it should be extendable to other displays
that use the same SSD1680 controller

Dependencies:
-------------
- numpy
- spidev
- RPi.GPIO
- bdfparser
- Pillow (only for a LocalRender test/debug)

Current capabilities:
---------------------
Currently it can draw:
- Geometric figures (only with a 1 pixel wide line)
  - Point
  - Line
  - Rectangle
  - Circle
- Text Rendering (with any bdf font)
- Bitmaps

What doesn't work
-----------------
Compared to the Arduino libraries
- Partial draw/refresh
