#!/usr/bin/env pybricks-micropython
 
from pybricks.ev3devices import (Motor)
from pybricks.parameters import (Port)
 
import struct

# Adjustmenets (feel free to change a little)
left_stick_middle_x = 0
left_stick_middle_y = 0
left_stick_deadzone = 15
max_steering_angle = 90

# Declare motors 
left_motor = Motor(Port.B)
right_motor = Motor(Port.C)
steer_motor = Motor(Port.A)

# Initialize variables. 
# Assuming sticks are in the middle when starting.
left_stick_x = 0
left_stick_y = 0
left_trigger = 0
right_trigger = 0
 

# A helper function for converting stick (0..65535) and trigger (0..1023) values
# to more usable numbers (-100 - 100)
def scale(val, src, dst):
    """
    Scale the given value from the scale of src to the scale of dst.
 
    val: float or int
    src: tuple
    dst: tuple
 
    example: print(scale(99, (0.0, 99.0), (-1.0, +1.0)))
    """
    return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]
 
 
# Find the XBox Controller:
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

while event:
    (tv_sec, tv_usec, ev_type, code, value) = struct.unpack(FORMAT, event)

    process_event = False

    if ev_type == 3 and code == 0:
        left_stick_x = value
        process_event = True
    elif ev_type == 3 and code == 1:
        left_stick_y = value
        process_event = True

    if process_event:
        # Scale stick positions to -100,100
        forward = scale(left_stick_y, (0, 65535), (100, -100))
        left = scale(left_stick_x, (0, 65535), (max_steering_angle, -max_steering_angle))

        if (-left_stick_deadzone < forward and forward < left_stick_deadzone and
                -left_stick_deadzone < left and left < left_stick_deadzone):
            # Stop driving motors
            left_motor.dc(0)
            right_motor.dc(0)
            # Set steering to center
            steer_motor.track_target(0)
        else:
            # Set motor voltages. If we're steering left, the left motor
            # must run backwards so it has a -left component
            # It has a forward component for going forward too. 
            left_motor.dc(-forward)
            right_motor.dc(forward)
            # Set steering angle
            steer_motor.track_target(-left)

    # Finally, read another event
    event = in_file.read(EVENT_SIZE)
 
in_file.close()