# ledmatrix-scroll by Andrew Oakley www.aoakley.com Public Domain 2015-10-18
# Updated by C.Bailey 2024; packaged with setup notes in this repository.
#
# Takes an image file (e.g. PNG) as command line argument and scrolls it
# across a grid of WS2811 addressable LEDs, repeated in a loop until CTRL-C
#
# Use a very wide image for good scrolling effect.
#
# If you have a low resolution matrix (like mine, 12x8 LEDs) then you will
# probably need to create your image height equal to your matrix height
# and draw lettering pixel by pixel (e..g in GIMP or mtpaint) if you want
# words or detail to be legible.

#import time, sys, os, re
#from neopixel import * # See https://learn.adafruit.com/neopixels-on-raspberry-pi/software
#from PIL import Image  # Use apt-get install python-imaging to install this

import time
import sys
import os
import re
from rpi_ws281x import PixelStrip, Color
from PIL import Image

# LED strip configuration:
LED_COUNT      = int(os.environ.get("LED_COUNT", "96"))
LED_PIN        = int(os.environ.get("LED_PIN", "18"))      # BCM GPIO 18 = physical header pin 12.
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = int(os.environ.get("LED_DMA", "5"))
LED_BRIGHTNESS = int(os.environ.get("LED_BRIGHTNESS", "100"))  # 0 darkest; 255 brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

# Speed of movement, in seconds (recommend 0.1-0.3) og .075
SPEED=float(os.environ.get("LED_MATRIX_SPEED", "0.1"))

# Size of your matrix
MATRIX_WIDTH=int(os.environ.get("MATRIX_WIDTH", "12"))
MATRIX_HEIGHT=int(os.environ.get("MATRIX_HEIGHT", "8"))

# LED matrix layout
# A list converting LED string number to physical grid layout
# Start with top right and continue right then down
# For example, my string starts bottom right and has horizontal batons
# which loop on alternate rows.
#
# Mine ends at the top right here:     -----------\
# My last LED is number 95                        |
#                                      /----------/
#                                      |
#                                      \----------\
# The first LED is number 0                       |
# Mine starts at the bottom left here: -----------/ 


myMatrix = [
    row * MATRIX_WIDTH + (col if row % 2 == 0 else MATRIX_WIDTH - 1 - col)
    for row in range(MATRIX_HEIGHT)
    for col in range(MATRIX_WIDTH)
]


# Feel free to write a fancy set of loops to populate myMatrix
# if you have a really big display! I used two cheap strings of
# 50 LEDs, so I just have a 12x8 grid = 96 LEDs
# I got mine from: http://www.amazon.co.uk/gp/product/B00MXW054Y
# I also used an 74AHCT125 level shifter & 10 amp 5V PSU
# Good build tutorial here:
# https://learn.adafruit.com/neopixels-on-raspberry-pi?view=all

# Check that we have sensible width & height
if MATRIX_WIDTH * MATRIX_HEIGHT != len(myMatrix) or LED_COUNT != len(myMatrix):
  raise Exception("LED_COUNT must equal MATRIX_WIDTH x MATRIX_HEIGHT")

def allonecolour(strip,colour):
  # Paint the entire matrix one colour
  for i in range(strip.numPixels()):
    strip.setPixelColor(i,colour)
  strip.show()

def colour(r,g,b):
  # Fix for Neopixel RGB->GRB, also British spelling
  return Color(g,r,b)

def colourTuple(rgbTuple):
  return Color(rgbTuple[1],rgbTuple[0],rgbTuple[2])

def initLeds(strip):
  # Intialize the library (must be called once before other functions).
  strip.begin()
  # Wake up the LEDs by briefly setting them all to white
  allonecolour(strip,colour(255,255,255))
  time.sleep(0.01)


# Ensure there is an image file argument
if len(sys.argv) <= 1:
    raise Exception("Please provide an image filename as a parameter.")

## Open the image file given as the command line parameter
#try:
#  loadIm=Image.open(sys.argv[1])
#except:
#  if len(sys.argv)==0:
#    raise Exception("Please provide an image filename as a parameter.")
#  else:
#    raise Exception("Image file %s could not be loaded" % sys.argv[1])

# Load the image file
try:
    loadIm = Image.open(sys.argv[1])
except IOError:
    raise Exception(f"Image file {sys.argv[1]} could not be loaded")

# If the image height doesn't match the matrix, resize it while preserving
# aspect ratio. Pillow requires integer dimensions; the old expression could
# produce a float (or divide by zero for images shorter than the matrix).
if loadIm.size[1] != MATRIX_HEIGHT:
  new_width = max(1, round(loadIm.size[0] * MATRIX_HEIGHT / loadIm.size[1]))
  resampling = getattr(Image, "Resampling", Image).BICUBIC
  origIm = loadIm.resize((new_width, MATRIX_HEIGHT), resampling)
else:
  origIm=loadIm.copy()
# If the input is a very small portrait image, then no amount of resizing will save us
if origIm.size[0] < MATRIX_WIDTH:
  raise Exception("Picture is too narrow. Must be at least %s pixels wide" % MATRIX_WIDTH)

# Check if there's an accompanying .txt file which tells us
# how the user wants the image animated
# Commands available are:
# NNNN speed S.SSS
#   Set the scroll speed (in seconds)
#   Example: 0000 speed 0.150
#   At position zero (first position), set the speed to 150ms
# NNNN hold S.SSS
#   Hold the frame still (in seconds)
#   Example: 0011 hold 2.300
#   At position 11, keep the image still for 2.3 seconds
# NNNN-PPPP flip S.SSS
#   Animate MATRIX_WIDTH frames, like a flipbook
#   with a speed of S.SSS seconds between each frame
#   Example: 0014-0049 flip 0.100
#   From position 14, animate with 100ms between frames
#   until you reach or go past position 49
#   Note that this will jump positions MATRIX_WIDTH at a time
#   Takes a bit of getting used to - experiment
# NNNN jump PPPP
#   Jump to position PPPP
#   Example: 0001 jump 0200
#   At position 1, jump to position 200
#   Useful for debugging only - the image will loop anyway
txtlines=[]
match=re.search( r'^(?P<base>.*)\.[^\.]+$', sys.argv[1], re.M|re.I)
if match:
  txtfile=match.group('base')+'.txt'
  if os.path.isfile(txtfile):
    print ("Found text file %s" % (txtfile))
    f=open(txtfile,'r')
    txtlines=f.readlines()
    f.close()

# Add a copy of the start of the image, to the end of the image,
# so that it loops smoothly at the end of the image
im=Image.new('RGB',(origIm.size[0]+MATRIX_WIDTH,MATRIX_HEIGHT))
im.paste(origIm,(0,0,origIm.size[0],MATRIX_HEIGHT))
im.paste(origIm.crop((0,0,MATRIX_WIDTH,MATRIX_HEIGHT)),(origIm.size[0],0,origIm.size[0]+MATRIX_WIDTH,MATRIX_HEIGHT))

# Create NeoPixel object with appropriate configuration.
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
initLeds(strip)

# And here we go.
try:
  while(True):

    # Loop through the image widthways
    # Can't use a for loop because Python is dumb
    # and won't jump values for FLIP command
    x=0
    # Initialise a pointer for the current line in the text file
    tx=0

    while x<im.size[0]-MATRIX_WIDTH:

      # Set the sleep period for this frame
      # This might get changed by a textfile command
      thissleep=SPEED

      # Set the increment for this frame
      # Typically advance 1 pixel at a time but
      # the FLIP command can change this
      thisincrement=1

      rg=im.crop((x,0,x+MATRIX_WIDTH,MATRIX_HEIGHT))
      dots=list(rg.getdata())
  
      for i in range(len(dots)):
        strip.setPixelColor(myMatrix[i],colourTuple(dots[i]))
      strip.show()

      # Check for instructions from the text file
      if tx<len(txtlines):
        match = re.search( r'^(?P<start>\s*\d+)(-(?P<finish>\d+))?\s+((?P<command>\S+)(\s+(?P<param>\d+(\.\d+)?))?)$', txtlines[tx], re.M|re.I)
        if match:
          print ("Found valid command line %d:\n%s" % (tx,txtlines[tx]))
          st=int(match.group('start'))
          fi=st
          print ("Current pixel %05d start %05d finish %05d" % (x,st,fi))
          if match.group('finish'):
            fi=int(match.group('finish'))
          if x>=st and tx<=fi:
            if match.group('command').lower()=='speed':
              SPEED=float(match.group('param'))
              thissleep=SPEED
              print ("Position %d : Set speed to %.3f secs per frame" % (x,thissleep))
            elif match.group('command').lower()=='flip':
              thissleep=float(match.group('param'))
              thisincrement=MATRIX_WIDTH
              print ("Position %d: Flip for %.3f secs" % (x,thissleep))
            elif match.group('command').lower()=='hold':
              thissleep=float(match.group('param'))
              print ("Position %d: Hold for %.3f secs" % (x,thissleep))
            elif match.group('command').lower()=='jump':
              print ("Position %d: Jump to position %s" % (x,match.group('param')))
              x=int(match.group('param'))
              thisincrement=0
          # Move to the next line of the text file
          # only if we have completed all pixels in range
          if x>=fi:
            tx=tx+1
        else:
          print ("Found INVALID command line %d:\n%s" % (tx,txtlines[tx]))
          tx=tx+1

      x=x+thisincrement
      time.sleep(thissleep)

except (KeyboardInterrupt, SystemExit):
  print ("Stopped")
  allonecolour(strip,colour(0,0,0))
