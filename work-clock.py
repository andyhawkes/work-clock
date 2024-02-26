#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from inky.auto import auto
from PIL import Image, ImageFont, ImageDraw
from font_fredoka_one import FredokaOne
from datetime import datetime
import pytz
import inflect
import argparse
import sys

# Get arguments
parser = argparse.ArgumentParser()
parser.add_argument('--timezone', '-t', type=str, required=False, help="Your desired timezone e.g. Europe/London")
parser.add_argument('--rotation', '-r', type=int, required=False, help="The rotation of your screen e.g. 270. Defaults to 90")
parser.add_argument('--days', '-d', type=str, required=False, help="Non-working days as a comma-separated list. Monday = 0, Sunday = 6")
parser.add_argument('--start', '-s', type=int, required=False, choices=range(0, 23), help="The hour of the day when work starts e.g. 9")
parser.add_argument('--end', '-e', type=int, required=False, choices=range(0, 23), help="The hour of the day when work stops e.g. 18")

args, _ = parser.parse_known_args()

# Set screen rotation from "rotation" argument or fall back to default
# On Pi Zero W, 90 = USB's at the top, 270 = USBs at the bottom
rotation = args.rotation or 90

# Set timezone from "timezone" argument or fall back to default
timezone = args.timezone or 'Europe/London'

# Get local time
tz = pytz.timezone(timezone)
localtime = datetime.now(tz)

# Set the weekend / non-working days from "days" argument or fall back to default
weekend_days = set(args.days.split(',')) if args.days is not None else {5,6}

# Define work day start and end times (hours) from "start" and "end" arguments, or fall back to defaults
workday_start = args.start or 9
workday_end = args.end or 17

# Location of status file containing clock status from last execution
status_file = "/path/to/your/script/work-clock-status.txt"

# Set up Inky pHAT
board = auto()

# Define available colours
red=board.RED
black=board.BLACK
white=board.WHITE

# Define basic layout
board.set_border(white)
board.rotation = rotation
padding = 10

# Use inflect to turn numbers into words
inflection = inflect.engine()

# Prepare a canvas
img = Image.new('P', (board.WIDTH, board.HEIGHT))
draw = ImageDraw.Draw(img)

# Define font options
big_font = ImageFont.truetype(FredokaOne, 30)
small_font = ImageFont.truetype(FredokaOne, 24)

# Output aligned text
def alignText(h="l", v="t", message='DEBUG', font=small_font, colour=black):
    mw, mh = font.getsize(message)

    # if an integer is passed for the h (horizontal) position then use it
    if isinstance(h, int):
        x = h
    # otherwise align left (l - default), middle (m) or right (r) 
    elif h == "r":
        x = board.WIDTH - mw - padding
    elif h == "m":
        x = (board.WIDTH / 2) - (mw / 2)
    else:
        x = padding

    # if an integer is passed for the v (vertical) position then use it
    if isinstance(v, int):
        y = v
    # otherwise align top (t - default), middle (m), or bottom(b)
    elif v == "b":
        y = ((board.HEIGHT / 3) * 2.5) - (mh / 2) - padding
    elif v == "m":
        y = ((board.HEIGHT / 3) * 1.5) - (mh / 2)
    else:
        y = ((board.HEIGHT / 3) * 0.5) - (mh / 2) + padding

    draw.text((x, y), message, fill=colour, font=font)

# Get current hour and minutes
hour24 = localtime.hour
mins = localtime.minute

# Get clock status from last execution
with open(status_file, "r") as f:
    clock_status = f.read()

# We don't want to update the display too often to avoid shortening the lifespan
# Check if it's the weekend
# We only update once during the weekend
if localtime.weekday() in weekend_days:
    if clock_status != "weekend":
        with open(status_file, "w") as f:
            f.write("weekend")
        alignText("m", "t", "It's", big_font)
        alignText("m", "m", "the", big_font)
        alignText("m", "b", "weekend!", big_font)
        board.set_image(img)
        board.show()
        print("It's the weekend!")
    sys.exit()
# We only update once during non-working hours
elif hour24 < workday_start or hour24 >= workday_end:
    if clock_status != "not working":
        with open(status_file, "w") as f:
            f.write("not working")
        alignText("l", "t", "It's")
        alignText("m", "t", "not", big_font, red)
        alignText("m", "m", "work")
        alignText("m", "b", "time")
        alignText("r", "b", "now")
        board.set_image(img)
        board.show()
        print("It's not work time now")
    sys.exit()
# We update when needed during working hours on working days
else:
    if clock_status != "working":
        with open(status_file, "w") as f:
            f.write("working")

# Format the hour correctly for output
if hour24 < 12:
    hour = hour24 if mins < 35 else hour24 + 1
elif hour24 == 12:
    hour = hour24 if mins < 35 else 1
else:
    hour = hour24 - 12 if mins < 35 else hour24 - 11

# Format the basic time output
time1 = ''
time2 = 'past' if mins < 35 else 'to'
time3 = inflection.number_to_words(hour)

# Break the minutes into 5 minute blocks
if mins < 5:
    time1 = 'bang on'
    time2 = inflection.number_to_words(hour)
    time3 = "o'clock"
elif 5 <= mins < 10 or mins >= 55:
    time1 = 'five'
elif 10 <= mins < 15 or 50 <= mins < 55:
    time1 = 'ten'
elif 15 <= mins < 20 or 45 <= mins < 50:
    time1 = 'a quarter'
elif 20 <= mins < 25 or 40 <= mins < 45:
    time1 = 'twenty'
elif 25 <= mins < 30 or 35 <= mins < 40:
    time1 = 'twenty-five'
else:
    time1 = 'half'

# Format the time for display
alignText("l", "t", "It's")
alignText("m", "t", time1)
alignText("m", "m", time2)
alignText("m", "b", time3)
alignText("r", "b", 'ish')

# Update the display
board.set_image(img)
board.show()

print("It's " + time1 + " " + time2 + " " + time3 + " ish")
