#!/usr/bin/env pybricks-micropython

#  This file is part of hugbug ev3 repository. See <https://github.com/hugbug/ev3>.
#
#  This is a program to use Xbox or PS controller to remotely control the
#  LEGO EV3 Model Rov3r+ MOC-20177 (https://rebrickable.com/mocs/MOC-20177).
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pybricks.ev3devices import (Motor)
from pybricks.parameters import (Port, SoundFile, Stop, Direction)
from pybricks import ev3brick as brick
from pybricks.tools import print
import time
import struct
import sys
import random
import uselect

random.seed(0)

# Defining stick dead zone which is a minimum amount of stick movement
# from the center position to start motors.
stick_deadzone = 5  # deadzone 5%

# Max steering angle for steering motor (in degrees).
# It is computed automatically during motor calibratation process.
# Here initialized with default value for debug purposes.
max_steering_angle = 300

# One of these can be disabled if you have connected both gamepads and want to use a particular one.
enable_xbox_detection = True
enable_ps_detection = True

# Constants for gamepad type.
gamepad_xbox = 1
gamepad_ps = 2

# Gamepad state.
gamepad_device = None
gamepad_type = 0 # gamepad_xbox or gamepad_ps
xbox = None # True if Xbox or False if PlayStation

# Constants for gearbox mode.
gearbox_manual = 1
gearbox_auto_sport = 2
gearbox_auto_comfort = 3

# Gearbox mode, initialized to default gearbox mode upon start.
gearbox_mode = gearbox_auto_sport

# Constants for automatic sport gearbox.
# Four gears. For each gear:
#  A) maximum RPM of the gear
#  B) Motor Power to gear up
#  C) RPM to gear up
#  D) gear up when the Motor-Power and RPM both are above B/C for as long seconds
#  E) Motor Power to gear down
#  F) RPM to gear down
#  G) gear down when the Motor-Power or RPM go below E/F for as long seconds
automatic_sport_gearbox = (
    (900, 70, 600, 0.6, 0, 0, 0), # Gear 1
    (900, 80, 650, 0.6, 50, 400, 0.3), # Gear 2
    (870, 90, 700, 0.7, 60, 500, 0.3), # Gear 3
    (820, 110, 10000, 1.0, 70, 550, 0.3)) # Gear 4

# Constants for automatic comfort gearbox.
# Four gears. For each gear:
#  A) maximum RPM of the gear
#  B) Motor Power to gear up
#  C) RPM to gear up
#  D) gear up when the Motor-Power and RPM both are above B/C for as long seconds
#  E) Motor Power to gear down
#  F) RPM to gear down
#  G) gear down when the Motor-Power or RPM go below E/F for as long seconds
#  H) gear up ratio compensation
#  I) gear up compensation time
#  J) gear down ratio compensation
#  K) gear down compensation time
automatic_comfort_gearbox = (
    (900, 70, 500, 0.7, 0, 0, 0, 0.8, 0, 0, 0), # Gear 1, 1:1 ratio
    (900, 80, 550, 1.0, 50, 400, 0.3, 0.8, 1.0, 1.2, 0), # Gear 2, 1:1.67 ratio
    (870, 90, 600, 1.0, 50, 450, 0.3, 0.8, 1.0, 1.2, 0.3), # Gear 3, 1:3 ratio
    (820, 110, 10000, 1.0, 50, 450, 0.3, 0, 0, 1.2, 0.3)) # Gear 4, 1:5 ratio

# Assuming sticks are in the middle and triggers are not pressed when starting
gear = 1 # Current gear (1..4)
power_pos = 0 # Current motor power (controlled by Y-axis of gamepad left stick) (-100..100)
power_bump = 0 # Power bump (controller by right trigger)
power_compensation = 1.0 # Power compensation after switching gears in comfort automatic mode
steering_pos = 0 # Steering position (-100..100)
motors = 2 # Use two motors

# An events read from the virtual device file consists of the following elements:
# long int, long int, unsigned short, unsigned short, long int
gamepad_event_format = 'llHHl'
gamepad_event_size = struct.calcsize(gamepad_event_format)

# Clear program title.
brick.display.clear()
brick.display.text("Rov3r+", (60, 20))

# Declare motors and check their connections.
try:
    first_motor = Motor(Port.A, Direction.COUNTERCLOCKWISE)
    second_motor = Motor(Port.D, Direction.COUNTERCLOCKWISE)
    steering_motor = Motor(Port.B)
    gearbox_motor = Motor(Port.C)
    second_motor.stop(Stop.COAST)
except:
    brick.display.text("Check motor cables", (0, 80))
    brick.sound.file(SoundFile.ERROR_ALARM)
    time.sleep(10)
    sys.exit(1)

def find_gamepad():
    """
    Checks device list by reading content of virtual file "/proc/bus/input/devices"
    looking for gamepad device.
    """
    global gamepad_type
    with open("/proc/bus/input/devices", "r") as fp:
        line = fp.readline()
        while line:
            if enable_xbox_detection and line.startswith("N: Name=") and line.find("Xbox") > -1:
                gamepad_type = gamepad_xbox
            if enable_ps_detection and line.startswith("N: Name=") and line.find("PLAYSTATION") > -1 and line.find("Motion") == -1:
                gamepad_type = gamepad_ps
            if gamepad_type > 0 and line.startswith("H: Handlers="):
                line = line[len("H: Handlers="):]
                pb = line.find("event")
                pe = line.find(" ", pb)
                return line[pb:pe]
            line = fp.readline()
    return None

def transform_stick(value):
    """
    Transforms range 0..max to -100..100, removes deadzone from the range.
    """
    max = 65535 if xbox else 255
    half = int((max + 1) / 2)
    deadzone = int((max + 1) / 100 * stick_deadzone)
    value -= half
    if abs(value) < deadzone:
        value = 0
    elif value > 0:
        value = (value - deadzone - 1) / (half - deadzone) * 100
    else:
        value = (value + deadzone) / (half - deadzone) * 100
    return value

def play_horn():
    """
    Plays a horn sound randomly selected from two available sounds.
    """
    if random.randint(1, 2) == 1:
        brick.sound.file(SoundFile.HORN_1)
    else:
        brick.sound.file(SoundFile.HORN_2)

def play_sound_effect():
    """
    Plays a random sound effect.
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

def calibrate_motors():
    """
    Calibrates gearbox motor: switches to first gear.
    Calibrates steering motor: finds the range by steering full to the left
    and full to the right, then centers the steering.
    """
    global max_steering_angle

    gearbox_motor.run_until_stalled(360, Stop.COAST, 50)
    gearbox_motor.run_angle(100, -20) # unstress the switcher
    gearbox_motor.reset_angle(0)

    steering_motor.run_until_stalled(720, Stop.COAST, 80)
    steering_motor.reset_angle(0)
    steering_motor.run_until_stalled(-720, Stop.COAST, 80)
    max_steering_angle = abs(steering_motor.angle()) / 2
    steering_motor.run_target(720, -max_steering_angle)
    steering_motor.reset_angle(0)
    max_steering_angle *= 0.90  # limit max steering angle a little

def print_help():
    """
    Prints program info and gamepad mapping to the brick display.
    Also prints current gearbox mode in the status line.
    """
    brick.display.clear()
    brick.display.text("Rov3r+", (60, 10))
    brick.display.text(("Xbox" if xbox else "PS") + " gamepad functions:", (0, 30))
    brick.display.text("Left Stick: movement", (0, 45))
    brick.display.text(("RB/LB" if xbox else "R1/L1") + ": gear up/down", (0, 55))
    brick.display.text(("A" if xbox else "X") + ": auto comfort/sport", (0, 65))
    brick.display.text(("B" if xbox else "O") + ": one/two motors", (0, 75))
    brick.display.text(("RT" if xbox else "R2") + ": steer. speed bump", (0, 85))
    brick.display.text(("X" if xbox else "/\\") + ": horn", (0, 95))
    brick.display.text(("Y" if xbox else "[]") + ": sound effect", (0, 105))
    brick.display.text((("manual" if gearbox_mode == gearbox_manual
        else "auto comfort" if gearbox_mode == gearbox_auto_comfort else "auto sport")) +
        ", " + str(motors) + " motor" + ("s" if motors > 1 else ""), (0, 125))

def drive(_power_pos, _power_bump, _power_compensation):
    """
    Sets current power settings for driving motors.
    """
    global power_pos, power_bump, power_compensation
    if _power_pos == None:
        _power_pos = power_pos
    if _power_bump == None:
        _power_bump = power_bump
    if _power_compensation == None:
        _power_compensation = power_compensation
    #print("Drive: ", _power_pos, _power_bump, _power_compensation)
    if power_pos != _power_pos or power_bump != _power_bump or power_compensation != _power_compensation:
        power_pos = _power_pos
        power_bump = _power_bump
        power_compensation = _power_compensation
        propulsion_power = power_pos * (1 + power_bump) * power_compensation
        first_motor.dc(propulsion_power)
        if motors == 2:
            second_motor.dc(propulsion_power)
        else:
            second_motor.stop(Stop.COAST)

def steer(_steering_pos):
    """
    Sets steering position.
    Computes required motor angle and rotates the steering motor there.
    """
    global steering_pos
    if steering_pos != _steering_pos:
        steering_pos = _steering_pos
        steering_angle = - steering_pos * max_steering_angle / 100
        steering_motor.track_target(steering_angle)

def switch_gear(_gear):
    """
    Switches gear of the gearbox.
    Computes required angle of the gearbox motor and rotates it to that position.
    """
    global gear
    if gear != _gear:
        gear = _gear
        gearing_angle = - (gear - 1) * 20 / 12 * 90
        gearbox_motor.track_target(gearing_angle)
        reset_automatic_gearbox()

def select_gearbox_mode(mode):
    """
    Sets current steering mode (automatic comfort, automatic sport or manual).
    Indicates current mode via beeps (one, two or three).
    """
    global gearbox_mode
    if mode != gearbox_mode:
        gearbox_mode = mode
        print_help()
        if gearbox_mode == gearbox_auto_comfort:
            brick.sound.beeps(1)
        elif gearbox_mode == gearbox_auto_sport:
            brick.sound.beeps(2)
        elif gearbox_mode == gearbox_manual:
            brick.sound.beeps(3)

def select_motors(motor_count):
    global motors
    if motors != motor_count:
        motors = motor_count
        print_help()
        brick.sound.beeps(motors)
        # Start or stop second motor.
        # We increase current power a little so that function "drive" see some changes to process.
        drive(power_pos + 1, None, None)

# Variables to hold state of the automatic gearbox.
gear_up_time = 0
gear_down_time = 0
comfort_time = 0
comfort_factor = 0
comfort_duration = 0

def reset_automatic_gearbox():
    """
    Aborts power compensation process and resets power compensation.
    This is for automtic comfort gearbox mode only.
    """    
    gear_up_time = 0
    gear_down_time = 0
    power_compensation = 1.0

def automatic_gearbox_control():
    """
    This function is called very often (many times for second) and is active
    only for automatic gearbox modes. 
    Checks current power and speed of the driving motors and switches to
    the next or previous gear of the gearbox when necessary.
    For automatic comfort gearbox: decreases motor power after gearing up or
    increases motor power after gearing down, to compensate for changed gear
    ratio in order to prevent jerky linear movement. The motor power is then
    smoothly correctd back to its original value within 0.5-2 seconds.
    """
    global gear_up_time, gear_down_time
    global comfort_time, comfort_factor, comfort_duration

    speed = abs(first_motor.speed())
    current_time = time.time()

    # Did we stop?
    if abs(power_pos) == 0 and speed == 0 and gear > 1:
        #print("Reset gear to", 1)
        switch_gear(1)

    comfort = gearbox_mode == gearbox_auto_comfort
    gearbox = automatic_comfort_gearbox if comfort else automatic_sport_gearbox
    gear_data = gearbox[gear - 1]
    power_compensation_in_progress = abs(power_compensation - 1.0) > 0.01

    # Can we gear up?
    if abs(power_pos) >= gear_data[1] and speed >= gear_data[2] and not power_compensation_in_progress:
        if gear_up_time == 0:
            gear_up_time = current_time
        elif current_time - gear_up_time >= gear_data[3] and gear < len(gearbox):
            # It's time to switch to the next gear 
            #print("Gear up to", gear + 1)
            switch_gear(gear + 1)
            if comfort:
                comfort_time = current_time
                comfort_factor = gear_data[7]
                comfort_duration = gear_data[8]
                #print("Compensate drive power", comfort_factor, comfort_duration, comfort_time)
                drive(None, None, comfort_factor)
            gear_up_time = 0
    else:
        gear_up_time = 0

    # Should we gear down?
    if abs(power_pos) <= gear_data[4] or speed <= gear_data[5] and not power_compensation_in_progress:
        if gear_down_time == 0:
            gear_down_time = current_time
        elif current_time - gear_down_time >= gear_data[6] and gear > 1:
            # It's time to switch to the previous gear 
            #print("Gear down to", gear - 1)
            switch_gear(gear - 1)
            if comfort:
                comfort_time = current_time
                comfort_factor = gear_data[9]
                comfort_duration = gear_data[10]
                #print("Compensate drive power", comfort_factor, comfort_duration, comfort_time)
                drive(None, None, comfort_factor)
            gear_down_time = 0
    else:
        gear_down_time = 0

    # Comfort gearbox: gradually adjust power factor compensation after switching to a higher gear
    if comfort_time > 0 and current_time > comfort_time:
        duration = current_time - comfort_time
        if duration < comfort_duration:
            if comfort_factor < 1.0:
                # Gear up
                compensation = comfort_factor + (1.0 - comfort_factor) * duration / comfort_duration
            else:
                # Gear down
                compensation = comfort_factor - (comfort_factor - 1.0) * duration / comfort_duration
            #print("Compensate drive power", compensation, comfort_factor, comfort_duration, comfort_time, current_time, duration)
        else:
            #print("Reset drive power")
            compensation = 1.0
            comfort_time = 0
        drive(None, None, compensation)

def process_gamepad_event(device_file):
    """
    Reads events from the gamepad device virtual file and processes them.
    """
    # Read from the gamepad device virtual file
    event = device_file.read(gamepad_event_size)

    (tv_sec, tv_usec, ev_type, code, value) = struct.unpack(gamepad_event_format, event)

    if ev_type == 3 or ev_type == 1:

        if ev_type == 3 and code == 0: # Left Stick Horz. Axis
            steer(transform_stick(value))

        elif ev_type == 3 and code == 1: # Left Stick Vert. Axis
            drive(-transform_stick(value), None, None)

        elif xbox and ev_type == 3 and code == 9: # Xbox Right Trigger
            drive(None, value / 1024, None)

        elif not xbox and ev_type == 3 and code == 5: # PS R2 paddle
            drive(None, value / 256, None)

        elif ev_type == 1 and code == 311 and value == 1: # RB pressed
            switch_gear(min(gear + 1, 4))
            select_gearbox_mode(gearbox_manual)

        elif ev_type == 1 and code == 310 and value == 1: # LB pressed
            switch_gear(max(gear - 1, 1))
            select_gearbox_mode(gearbox_manual)

        elif ev_type == 1 and code == 304 and value == 1: # A pressed
            select_gearbox_mode(gearbox_auto_comfort if gearbox_mode == gearbox_auto_sport else gearbox_auto_sport)

        elif ev_type == 1 and code == 305 and value == 1: # B pressed
            select_motors(2 if motors == 1 else 1)

        elif ev_type == 1 and code == 307 and value == 1: # X pressed
            play_horn()

        elif ev_type == 1 and code == 308 and value == 1: # Y pressed
            play_sound_effect()

# Find the gamepad
gamepad_device = find_gamepad()
xbox = gamepad_type == gamepad_xbox
#print("Gamepad device:", gamepad_device, ", type:", gamepad_type)

if gamepad_device is None:
    brick.display.text("Gamepad not found", (0, 80))
    brick.sound.file(SoundFile.ERROR_ALARM)
    time.sleep(10)
    sys.exit(1)

gamepad_infile_path = "/dev/input/" + gamepad_device
gamepad_infile = open(gamepad_infile_path, "rb")

print_help()

calibrate_motors()

# We use event polling mechanism to read from gamepad virtual device file.
# This allows us to check if there are new data in the file before attempting
# to read from it. As a result the "read from file"-function never blocks
# and we can do some other work when there are no gamepad events.
event_selector = uselect.poll()
event_selector.register(gamepad_infile, uselect.POLLIN)

while True:
    events = event_selector.poll(0)
    if (len(events) > 0 and events[0][1] & uselect.POLLIN):
        process_gamepad_event(gamepad_infile)
    else:
        # This code is executed when there are no gamepad events to proceed.
        # Here we can check sensors or do some other work.
        if gearbox_mode != gearbox_manual:
            automatic_gearbox_control()
        time.sleep(0.010) # sleep a little to reduce CPU load and power consumption

gamepad_infile.close() # will never executed actually, due to endless while loop
