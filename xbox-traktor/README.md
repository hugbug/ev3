# MOC-28647 EV3 RC car

This is a program to use Xbox One Controller to remote control the LEGO EV3 Robot "EV3 RC car" [MOC-28647](https://rebrickable.com/mocs/MOC-28647/z52c/ev3-rc-car/#comments).

The robot has three motors. The two large motors work together to drive all four wheels.
The motors rotate at the same speed but in inverse directions.

The third motor is used for steering. It should be rotated only to small angles - max. ca. 90 degrees in each direction.
Trying to rotate the steering motor further may damage the model. The program takes care of this and will not rotate the
motor beyond safe zone.

The program consists of loop reading events from the XBox controller virtual device file and adjusting the motors. 
The left thumb stick controls the driving and steering simultaneously. Other buttons or sticks of the controller are not used.

# How to use

First you need to connect your Xbox One Controller to your EV3 brick.
The brick should be running LEGO MicroPython firmware image.

For instructions on how to connect the controller please see 
[Connecting Xbox One Controller to EV3 (EV3DEV or LEGO MicroPython)](https://github.com/hugbug/ev3/wiki/Connecting-Xbox-One-Controller-to-EV3-(EV3DEV-or-LEGO-MicroPython))

Once you have the controller connected upload the script to your EV3 brick and start it using EV3 brick file browser.

You can also use MS VS Code with LEGO MicroPython extension to upload the program to the brick.
Please refer to LEGO MicroPython documentation for details.

# How the program works

More details about the internals of the program can be found in article 
[Using Xbox One Controller with MicroPython on EV3](https://github.com/hugbug/ev3/wiki/Using-Xbox-One-Controller-with-MicroPython-on-EV3).
