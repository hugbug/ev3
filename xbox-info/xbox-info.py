#!/usr/bin/env pybricks-micropython
 
from pybricks.tools import print
 
import struct
 
# Find the Xbox Controller:
# /dev/input/event2 is the usual file handler for the gamepad.
# look at contents of /proc/bus/input/devices if it doesn't work.
infile_path = "/dev/input/event2"
 
# open file in binary mode
in_file = open(infile_path, "rb")
 
# Read from the file
# long int, long int, unsigned short, unsigned short, long int
FORMAT = 'llHHl'
EVENT_SIZE = struct.calcsize(FORMAT)
event = in_file.read(EVENT_SIZE)

num = 0

while event:
    (tv_sec, tv_usec, ev_type, code, value) = struct.unpack(FORMAT, event)

    if ev_type == 1 or ev_type == 3:
        num = num + 1
        button = ""

        if ev_type == 1:
            if code == 304:
                button = "A"
            elif code == 305:
                button = "B"
            elif code == 307:
                button = "X"
            elif code == 308:
                button = "Y"
            elif code == 310:
                button = "LB"
            elif code == 311:
                button = "RB"
            elif code == 158:
                button = "BACK"
            elif code == 315:
                button = "MENU"
            elif code == 317:
                button = "LEFT STICK"
            elif code == 318:
                button = "RIGHT STICK"

        elif ev_type == 3:
            if code == 0:
                button = "LEFT STICK X"
            elif code == 1:
                button = "LEFT STICK Y"
            elif code == 2:
                button = "RIGHT STICK X"
            elif code == 5:
                button = "RIGHT STICK Y"
            elif code == 9:
                button = "RT"
            elif code == 10:
                button = "LT"
            elif code == 16:
                button = "D-PAD X"
            elif code == 17:
                button = "D-PAD Y"

        message = "[%d] RAW: %d %d %d" % (num, ev_type, code, value)
        if button != "":
            message = message + (", DECODED: %s %s" % (button, value))
        print(message)

    # Finally, read another event
    event = in_file.read(EVENT_SIZE)
 
in_file.close()