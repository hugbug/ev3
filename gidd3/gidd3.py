#!/usr/bin/env pybricks-micropython
 
from pybricks.ev3devices import (Motor)
from pybricks.parameters import (Port, SoundFile)
from pybricks import ev3brick as brick
from pybricks.tools import print
import time
import struct
import sys
import random

random.seed(0)

# Defining stick dead zone which is a minimum amount of stick movement
# from the center position to start motors
stick_deadzone = 5  # deadzone 5%

# Clear program title
brick.display.clear()
brick.display.text("Gidd3", (60, 20))

# Declare motors
try:
    left_motor = Motor(Port.B)
    right_motor = Motor(Port.C)
except:
    brick.display.text("Check motor cables", (0, 80))
    brick.sound.file(SoundFile.ERROR_ALARM)
    time.sleep(10)
    sys.exit(1)

# Constants
gamepad_xbox = 1
gamepad_ps = 2

# Initialize variables. 
# Assuming sticks are in the middle and triggera are not pressed when starting
left_stick_x = 0
left_stick_y = 0
right_trigger = 0

gamepad_device = None
gamepad_type = None # gamepad_xbox or gamepad_ps
stick_xbox_deadzone = int(65536 / 100 * stick_deadzone)

def find_controller():
    """
    Checks device list by reading content of virtual file "/proc/bus/input/devices"
    looking for gamepad device.
    """
    global gamepad_type
    in_device = False
    with open("/proc/bus/input/devices", "r") as fp:
        line = fp.readline()
        while line:
            if line.startswith("N: Name=") and line.find("Xbox") > -1:
                in_device = True
            if in_device and line.startswith("H: Handlers=kbd "):
                gamepad_type = gamepad_xbox
                return line[len("H: Handlers=kbd "):].strip()
            line = fp.readline()
    return None

def transform_stick_xbox(value):
    """
    Transform range 0..65535 to -100..100, remove deadzone from the range
    """
    value -= 32767
    if abs(value) < stick_xbox_deadzone:
        value = 0
    elif value > 0:
        value = (value - stick_xbox_deadzone - 1) / (32767 - stick_xbox_deadzone) * 100
    else:
        value = (value + stick_xbox_deadzone) / (32767 - stick_xbox_deadzone) * 100
    return value

def play_horn():
    """
    Plays a horn sound randomly selected from two available sounds
    """
    if random.randint(1, 2) == 1:
        brick.sound.file(SoundFile.HORN_1)
    else:
        brick.sound.file(SoundFile.HORN_2)

def play_sound_effect():
    """
    Plays a random sound effect
    """
    effect = random.randint(1, 4)
    if effect == 1:
        brick.sound.file(SoundFile.AIR_RELEASE)
    elif effect == 2:
        brick.sound.file(SoundFile.AIRBRAKE)
    elif effect == 3:
        brick.sound.file(SoundFile.LASER)
    elif effect == 4:
        brick.sound.file(SoundFile.SONAR)

# Find the Xbox Controller:
# /dev/input/event2 is the usual file handler for the gamepad.
# The contents of /proc/bus/input/devices lists all devices.
gamepad_device = find_controller()
if gamepad_device is None:
    brick.display.text("Gamepad not found", (0, 80))
    brick.sound.file(SoundFile.ERROR_ALARM)
    time.sleep(10)
    sys.exit(1)

# currently supporting only Xbox One Controller
if gamepad_type != gamepad_xbox:
    brick.display.text("Gamepad not supported", (0, 80))
    brick.sound.file(SoundFile.ERROR_ALARM)
    time.sleep(10)
    sys.exit(1)

brick.display.text("Gamepad functions:", (0, 40))
brick.display.text("Left Stick: movement", (0, 60))
brick.display.text("RT: steering sensitiv.", (0, 70))
brick.display.text("A: horn", (0, 80))
brick.display.text("B: sound effect", (0, 90))

infile_path = "/dev/input/" + gamepad_device
in_file = open(infile_path, "rb")

# Read from the file
# long int, long int, unsigned short, unsigned short, long int
FORMAT = 'llHHl'
EVENT_SIZE = struct.calcsize(FORMAT)
event = in_file.read(EVENT_SIZE)

while event:
    (tv_sec, tv_usec, ev_type, code, value) = struct.unpack(FORMAT, event)

    if ev_type == 3 and code == 0: # Left Stick Horz. Axis
        left_stick_x = transform_stick_xbox(value)

    elif ev_type == 3 and code == 1: # Left Stick Vert. Axis
        left_stick_y = transform_stick_xbox(value)

    elif ev_type == 3 and code == 9: # Right Trigger
        right_trigger = value / 1024

    elif ev_type == 1 and code == 304 and value == 1:  # A pressed
        play_horn()

    elif ev_type == 1 and code == 305 and value == 1:  # B pressed
        play_sound_effect()

    #print(left_stick_y, left_stick_x, forward, left)

    # Set motor voltages. If we're steering left, the left motor
    # must run backwards so it has a -X component
    # It has a Y component for going forward too. 
    left_motor.dc(left_stick_y - left_stick_x * (1 - right_trigger / 1.1))
    right_motor.dc(left_stick_y + left_stick_x * (1 - right_trigger / 1.1))

    # Finally, read another event
    event = in_file.read(EVENT_SIZE)

in_file.close()