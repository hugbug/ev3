#!/usr/bin/env pybricks-micropython
 
from pybricks.ev3devices import (Motor)
from pybricks.parameters import (Port, SoundFile)
from pybricks import ev3brick as brick
from pybricks.tools import print
import time
import struct

# Defining stick dead zone which is a minimum amount of stick movement
# from the center position to start motors
stick_deadzone = int(65536 / 100 * 5)  # deadzone 5%

# Clear program title
brick.display.clear()
brick.display.text("Gidd3", (60, 50))

# Declare motors 
left_motor = Motor(Port.B)
right_motor = Motor(Port.C)

# Initialize variables. 
# Assuming sticks are in the middle when starting.
left_stick_x = 0
left_stick_y = 0
right_trigger = 0
 
def transform_range(value):
    """
    Transform range 0..65535 to -100..100, remove deadzone from the range
    """
    value -= 32767
    if abs(value) < stick_deadzone:
        value = 0
    elif value > 0:
        value = (value - stick_deadzone - 1) / (32767 - stick_deadzone) * 100
    else:
        value = (value + stick_deadzone) / (32767 - stick_deadzone) * 100
    return value

# Find the Xbox Controller:
# /dev/input/event2 is the usual file handler for the gamepad.
# look at contents of /proc/bus/input/devices if it doesn't work.
infile_path = "/dev/input/event2"

# open file in binary mode
try:
    in_file = open(infile_path, "rb")
except:
    brick.display.text("Xbox One Controller", (0, 80))
    brick.display.text("not found", (0, 90))
    brick.sound.file(SoundFile.ERROR_ALARM)
    time.sleep(10)
    pass

# Read from the file
# long int, long int, unsigned short, unsigned short, long int
FORMAT = 'llHHl'
EVENT_SIZE = struct.calcsize(FORMAT)
event = in_file.read(EVENT_SIZE)

while event:
    (tv_sec, tv_usec, ev_type, code, value) = struct.unpack(FORMAT, event)

    if ev_type == 3 and code == 0:
        left_stick_x = transform_range(value)

    elif ev_type == 3 and code == 1:
        left_stick_y = transform_range(value)

    elif ev_type == 3 and code == 9:
        right_trigger = value / 1024

    #print(left_stick_y, left_stick_x, forward, left)

    # Set motor voltages. If we're steering left, the left motor
    # must run backwards so it has a -X component
    # It has a Y component for going forward too. 
    left_motor.dc(left_stick_y - left_stick_x * (1 - right_trigger / 1.1))
    right_motor.dc(left_stick_y + left_stick_x * (1 - right_trigger / 1.1))

    # Finally, read another event
    event = in_file.read(EVENT_SIZE)

in_file.close()