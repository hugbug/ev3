# MOC-20177 Rov3r+

This is a program to use Xbox or PS Controller to remotely control the LEGO EV3 Model **Rov3r+** [MOC-20177](https://rebrickable.com/mocs/MOC-20177).

The program consists of a loop reading events from the controller virtual device file and adjusting the motors. 
The program prints the key mapping on the EV3 brick screen.

# Keys and functions
Use **left thumb stick** to move the model. The stick controls the drive speed and the steering simultaneously.
The vehicle has 4-speed gearbox. The program implements three modes for the gearbox: one manual mode and two automatic modes.
In the manual mode the gears are switched using buttons **LB** and **RB** on Xbox controllers (**L1** and **R1** on PS). In automatic mode the gears are switched automatically (as expected).

Button **A** on Xbox controller (&#x25A2; on PS) switches between automatic comfort and sport gearbox modes.

What's the difference? The **sport mode** is a simpler one. The gearbox is switched to the next gear after the motor achieved certain speed and was able keep it for certain amount of time (about a half of second). The gear is shifted and that causes an immediate speed bump.

In **comfort mode** after switching the gear up the motor power is immediately reduced to compensate for the increased gear ratio. The rover continues to drive at the same speed. In the next short period of time (about a second or less) the motor power is smoothly increased to the required leveland the vehicle (smoothly) accelerates. A similar process happens when the gears are shifted down.

The program starts in automatic sport mode (this can be changed in a variable). You can switch to comfort mode with button **A** (&#x25A2; on PS) or to manual mode with button **LB** (**L1** on PS).

Button **B** (&#x25EF; on PS) disables or enables the second drive motor. The rover profits from the second motor a lot. You will probably not use the one motor mode much.

# How to install

First you need to connect your controller to your EV3 brick.
The brick should be running LEGO MicroPython firmware image.

For instructions on how to connect the controller please see 
[Connecting Xbox One Controller to EV3](https://github.com/hugbug/ev3/wiki/Connecting-Xbox-One-Controller-to-EV3-(EV3DEV-or-LEGO-MicroPython)) and [Connecting PlayStation Controller to EV3](https://github.com/hugbug/ev3/wiki/Connecting-PlayStation-Controller-to-EV3-(EV3DEV-or-LEGO-MicroPython)).

Once you have the controller connected upload the script to your EV3 brick and start it using EV3 brick file browser.

You can also use MS VS Code with LEGO MicroPython extension to upload the program to the brick.
Please refer to LEGO MicroPython documentation for details.

# How the program works

More details about the internals of the program can be found in article 
[Using Xbox One Controller with MicroPython on EV3](https://github.com/hugbug/ev3/wiki/Using-Xbox-One-Controller-with-MicroPython-on-EV3).
