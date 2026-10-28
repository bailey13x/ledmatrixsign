# Raspberry Pi WS2811 LED Matrix

This is the 12 × 8 scrolling display code for 96 WS2811 LEDs. It uses the
`rpi_ws281x` library and Pillow. The original scrolling program is by Andrew
Oakley; see the credit and tutorial links at the end.

## Hardware used

- Raspberry Pi with a 40-pin GPIO header (the recovered build used a Pi 4)
- 96 WS2811 LEDs arranged as 12 columns × 8 rows, in a serpentine chain
- Regulated 5 V LED supply. The original project notes specify a 10 A supply.
- Short data lead from the Pi to the first LED
- Optional 74AHCT125 level shifter and 300–500 Ω series data resistor

The Pi uses its own power supply. Do not power the LED load through the Pi or
through breadboard power rails. At full white, some WS2811 pixels can draw up
to about 60 mA each, so 96 pixels can approach 5.8 A. Start with brightness
low and use wiring and connectors rated for the current.

## Wiring, by wire

Make all connections with both supplies unplugged.

| Wire | From | To |
|---|---|---|
| LED data | Raspberry Pi physical pin 12 (BCM GPIO18) | DIN on the first LED |
| Shared ground | Raspberry Pi physical pin 6 (GND) | LED supply negative and LED strip GND |
| LED positive | LED supply +5 V | LED strip +5 V |
| Pi power | Pi's own USB-C power supply | Raspberry Pi USB-C power input |

Keep the LED supply's +5 V wire off the Pi's 5 V pins. The grounds must be
joined so the Pi data signal has the same reference as the LEDs. Connect the
external supply directly to the strip's power input; do not run LED current
through a solderless breadboard. The breadboard can be used for the low-current
data and ground connections if its jumpers and contacts are sound.

Check the strip markings for `DIN`/`DI`, `+5V`, and `GND`; data must enter at
`DIN`, not `DOUT`. If the matrix uses two strips in one chain, connect the
first strip's `DOUT` to the second strip's `DIN`. Power both from the 5 V supply
with suitable wire, and keep their grounds common. The software maps image
row 0 to the top row. The original sign mapping runs from LED 0 at the bottom
right through the serpentine rows to LED 95 at the top right.

### Pin numbering

Use the Raspberry Pi board's physical pin numbers, not GPIO/BCM numbers, when
counting header pins. With the Pi held so the USB ports face down and the GPIO
header is along the top edge, physical pin 1 is the 3.3 V corner pin; pin 2 is
beside it. Pin 12 is GPIO18, and pin 6 is a ground pin. Confirm pin 1 from the
board marking before wiring.

### Optional signal conditioning

The recovered build notes list a 74AHCT125 level shifter and a 10 A 5 V supply.
The display has also been reported to work with GPIO18 connected directly to
DIN, so the shifter is not required to try the known-working setup. Pi GPIO is
3.3 V while the LED data input is powered at 5 V; a 74AHCT125 can make that
signal more reliable, especially with a longer lead. If adding the shifter,
power it from 5 V, connect its ground to the common ground, feed GPIO18 into an
enabled buffer input, and connect that buffer output to LED DIN. Follow the
notch/dot and the exact chip datasheet for pin numbering. A 300–500 Ω resistor
in series with the data lead near the first LED and a 500–1000 µF capacitor
across LED +5 V and GND near the strip input are common protection/stability
measures; observe capacitor polarity. They are optional for a setup that is
already stable.

## Install and run

On Raspberry Pi OS, from the Pi terminal:

```sh
cd ~
git clone https://github.com/bailey13x/ledmatrixsign.git ledmatrix
cd ~/ledmatrix
python3 -m venv --system-site-packages .venv
. .venv/bin/activate
pip install -r ledmatrix-requirements.txt
```

Copy an image such as `halov2.png` and optionally a matching `halov2.txt`
animation file into `~/ledmatrix`. Then run:

```sh
sudo /home/pi/ledmatrix/.venv/bin/python /home/pi/ledmatrix/ledmatrix_scroll.py /home/pi/ledmatrix/halov2.png
```

Press Ctrl+C to stop. Use the actual Linux account home path if it is not
`/home/pi`. The script starts with the configured brightness of 100/255; lower
`LED_BRIGHTNESS` in the script while testing.

Images scroll across the display. The script resizes images to 8 pixels high
while preserving their aspect ratio. A same-name `.txt` file can add animation
commands; examples are shown below. Positions are horizontal pixel offsets:

```text
0-335 flip 0.400
336 speed 0.2
516 hold 3
```

Supported commands are `speed`, `hold`, `flip`, and `jump`; the script's source
comments describe each command in detail.

## Configuration

The main hardware and display settings are at the top of
`ledmatrix_scroll.py`:

- `LED_COUNT = 96`
- `LED_PIN = 18` (BCM numbering; physical header pin 12)
- `LED_BRIGHTNESS = 100` (0–255)
- `MATRIX_WIDTH = 12`, `MATRIX_HEIGHT = 8`
- `myMatrix` maps the pixel stream to the serpentine physical layout

If text is mirrored or upside down, change `myMatrix` to match the direction
of the physical chain. If colors are swapped, adjust `colourTuple()` for the
LED strip's color order.

## Troubleshooting

- **No light:** verify supply polarity and 5 V at the strip input; verify the
  Pi and strip grounds are connected; check that data goes to `DIN`.
- **Flicker or random colors:** shorten the data lead, lower brightness, check
  the shared ground, and consider the 74AHCT125 buffer.
- **Only part of the matrix lights:** inspect the `DOUT`-to-`DIN` connection
  between strips and check the first unlit pixel and its power connections.
- **Wrong orientation:** confirm the physical LED 0 location and row direction.
  This build uses LED 0 at bottom right and LED 95 at top right, matching the
  original `ledmatrixgood.py` mapping.
- **Wrong colors:** adjust the channel order in `colourTuple()`.

## Credits

- Original scrolling program: Andrew Oakley, public domain, 2015:
  [Raspberry Pi Christmas LED Matrix](https://www.aoakley.com/articles/2015-11-18-raspberry-pi-christmas-led-matrix.php)
- Build tutorial: [Adafruit NeoPixel Überguide for Raspberry Pi](https://learn.adafruit.com/neopixels-on-raspberry-pi)

## Animated Halloween marquee

A new long-form Halloween design is included at `assets/halloween_marquee.png`, with
paired frame instructions in `assets/halloween_marquee.txt`. It uses pumpkin,
candy corn, ghost, bat, and cat flipbook frames between bright Halloween phrases.
Copy both files to the Pi with matching base names, then run:

```sh
sudo /home/pi/ledmatrix/.venv/bin/python /home/pi/ledmatrix/ledmatrix_scroll.py /home/pi/ledmatrix/halloween_marquee.png
```

The scrolling program accepts environment overrides for the control panel:
`LED_COUNT`, `LED_PIN`, `LED_BRIGHTNESS`, `LED_DMA`, `LED_MATRIX_SPEED`,
`MATRIX_WIDTH`, and `MATRIX_HEIGHT`. Defaults match a 96-pixel 12 × 8 sign.
