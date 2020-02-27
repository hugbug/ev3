# MOC-20177 Rov3r+

This is a program to use Xbox or PS Controller to remotely control the LEGO EV3 Model **Rov3r+** [MOC-20177](https://rebrickable.com/mocs/MOC-20177.

The program consists of a loop reading events from the controller virtual device file and adjusting the motors. 
The program prints the key mapping on the EV3 brick screen.

# How to use

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
