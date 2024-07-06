# Import necessary libraries
import _thread
from utime import sleep, sleep_ms
import time
import uasyncio as asyncio
import sh1106
from machine import Pin, I2C
from writer import Writer
import freesans20
import courier20

# Buttons Pin Declaration
B_Next = Pin(16, Pin.IN, Pin.PULL_UP)
B_Select = Pin(5, Pin.IN, Pin.PULL_UP)

# Input Pin declaration
In_Power = Pin(6, Pin.IN, Pin.PULL_UP)
In_100 = Pin(8, Pin.IN, Pin.PULL_UP)
In_75 = Pin(7, Pin.IN, Pin.PULL_UP)
In_50 = Pin(17, Pin.IN, Pin.PULL_UP)
In_25 = Pin(4, Pin.IN, Pin.PULL_UP)

# Output Pin declaration
Relay1 = Pin(9, Pin.OUT)
Relay2 = Pin(10, Pin.OUT)
Buzzer = Pin(11, Pin.OUT)

# Indicator Led Pin declaration
Led = Pin(12, Pin.OUT)

# Display Pin declaration
sda = Pin(2)
scl = Pin(3)

# Display Initialization
i2c = I2C(1, sda=sda, scl=scl)
width = 128
height = 64
oled = sh1106.SH1106_I2C(width, height, i2c, Pin(4), 0x3C)
Font_Thin = Writer(oled, freesans20)
Font_Thick = Writer(oled, courier20)

# Permanent Data Storage File
file = open("Log.txt", "r+")
log = file.read()

# Global Variables
start = bool(int(log[0]))
min = int(log[1])
max = int(log[2])
over = bool(int(log[3]))
level = 0
power = False
starting = False
filling = False
overflowing = False
over_timer = 0


# Function to handle button presses
def button(B, long_press_threshold=1.5):
    if not B.value():
        Buzzer.on()
        press_start_time = time.ticks_ms()  # Record the start time of the button press
        while not B.value():
            pass
        press_duration = (
            time.ticks_ms() - press_start_time
        )  # Calculate the duration of the button press
        Buzzer.off()
        if press_duration < long_press_threshold * 1000:
            return 1  # Short press
        else:
            return -1  # Long press
    else:
        return 0


# Function to print lines on the display
def printlines(lines, invert=[0]):
    if len(lines[0]) == 9:
        font = Font_Thick
    else:
        font = Font_Thin
    for i in range(3):
        font.printstring(lines[i], i + 1 in invert)
    oled.show()
    Writer.set_textpos(0, 0)


# Function to handle option selection on the display
def option(o):
    i = [1, 2, 3]
    O = []
    selected = 1
    for x in o:
        O += [x + " " * (9 - len(x))]
    printlines(O, [1])
    while not button(B_Select):
        if button(B_Next):
            i = i[1:] + i[:1]
            selected = i[0]
            printlines(O, [selected])
    return selected


# Initialization function to be called at the start
def start():
    printlines(["  Created by:  ", " " * 25, "   Aman Singh"])
    sleep(3)
    clear()


# Function to display loading animation
def load():
    for i in range(4):
        printlines([" " * 25, "loading" + "." * i, ""])
        sleep(1)
    clear()


# Function to clear the display
def clear():
    oled.fill(0)
    oled.show()


# Function to define options for different menus
def options(o):
    if o == 0:
        return ["Back", "Controls", "Limits"]
    elif o == 1:
        return ["Back", "Stop" if start else "Start", "Overflow"]
    elif o == 2:
        return ["Back", "Max  " + str(max * 25) + "%", "Min  " + str(min * 25) + "%"]
    elif o == 3:
        return ["100%", "75%", "50%"]
    elif o == 4:
        return ["50%", "25%", "0%"]


# Main function for controlling the display and user input
def screen_control():
    while True:
        # Main menu options
        selected = option(options(0))  # Main menu
        if selected == 1:
            clear()
            return  # End function and return to the main loop

        elif selected == 2:
            while True:
                # Controls submenu options
                selected_controls = option(options(1))  # Controls submenu
                if selected_controls == 1:
                    break  # Go back to the main menu

                elif selected_controls == 2:
                    # Start/Stop Motor option
                    if start:
                        set_start(False)
                        set_over(False)
                    elif level < max:
                        set_start(True)
                    clear()
                    return

                elif selected_controls == 3:
                    # Overflow option
                    if over:
                        set_over(False)
                    else:
                        set_over(True)
                        set_start(True)
                    clear()
                    return

        elif selected == 3:
            while True:
                # Limits submenu options
                selected = option(options(2))  # Limits submenu
                if selected == 1:
                    break  # Go back to the main menu

                if selected == 2:
                    # Set Max Limit option
                    selected_level = option(options(3))
                    # ['100%', '75%', '50%']
                    if selected_level == 1:
                        set_max(4)
                    elif selected_level == 2:
                        set_max(3)
                    elif selected_level == 3:
                        set_max(2)
                    if max - min < 2:
                        set_min(max - 2)

                elif selected == 3:
                    # Set Min Limit option
                    selected_level = option(options(4))
                    # ['50%', '25%', '0%']
                    if selected_level == 1:
                        set_min(2)
                    elif selected_level == 2:
                        set_min(1)
                    elif selected_level == 3:
                        set_min(0)
                    if max - min < 2:
                        set_max(min + 2)


# Task function for the idle screen
def task_screen_idle():
    load()
    invert = [0]
    start_time = time.ticks_ms()
    while True:
        # Check if any of the buttons are pressed
        if button(B_Select) == -1 or button(B_Next) == -1:
            # If pressed, go to the screen control menu
            screen_control()
        else:
            lines = []
            filled = str(level * 25)
            if starting:
                # Display information during motor starting phase
                lines = [
                    "Starting Motor",
                    "Level" + " " * (12 - 2 * len(filled)) + filled + "%",
                    f"{'Overflow is on' if over else ' '*25}",
                ]
            elif filling:
                # Display information when the motor is on and filling
                if overflowing:
                    lines = [
                        "  Overflowing  ",
                        " " * (12 - len(str(over_timer)))
                        + str(over_timer)
                        + " " * (12 - len(str(over_timer))),
                        " " * 25,
                    ]
                else:
                    lines = [
                        "  Motor is On   ",
                        "Filled" + " " * (12 - 2 * len(filled)) + filled + "%",
                        f"{'Overflow is on' if over else ' '*25}",
                    ]
            else:
                # Display information when the motor is off
                lines = [
                    "  Motor is Off  ",
                    "Level" + " " * (12 - 2 * len(filled)) + filled + "%",
                    f"{'Overflow is on' if over else ' '*25}",
                ]

            duration = time.ticks_ms() - start_time

            # Invert the display every 15 seconds
            if duration > 15000:
                if invert == [0]:
                    invert = [1, 2, 3]
                else:
                    invert = [0]
                start_time = time.ticks_ms()

            # Print the lines on the display
            printlines(lines, invert)


# Function to set the start mode (motor on/off) and update the log file
def set_start(mode):
    global start
    start = mode
    file.seek(0)
    file.write(str(int(mode)))
    file.flush()


# Function to set the minimum water level and update the log file
def set_min(level):
    global min
    min = level
    file.seek(1)
    file.write(str(level))
    file.flush()


# Function to set the maximum water level and update the log file
def set_max(level):
    global max
    max = level
    file.seek(2)
    file.write(str(level))
    file.flush()


# Function to set the overflow mode and update the log file
def set_over(mode):
    global over
    over = mode
    file.seek(3)
    file.write(str(int(mode)))
    file.flush()


# Task function for blinking the indicator LED
async def task_blink():
    while True:
        Led.toggle()
        await asyncio.sleep_ms(500)


# Function to determine the current water level based on input pins
def new_level():
    if not In_100.value():
        return 4
    elif not In_75.value():
        return 3
    elif not In_50.value():
        return 2
    elif not In_25.value():
        return 1
    else:
        return 0

# Function to monitor and update current water level
async def monitor_level():
    global level 
    while True:
        temp_level = new_level()  # Capture the current level
        if temp_level != level:  # Check if there's a change in the level
            for _ in range(3):  # Loop to confirm the change over 3 seconds
                await asyncio.sleep(1)  # Wait for 1 second
                if new_level() != temp_level:  # Check if the level has changed again
                    break  # Break if it has changed
            else:  # If the level is consistent for 3 seconds
                level = temp_level  # Update the level to the new value

# Task function for controlling motor
async def motor(mode):
    global starting
    if mode:
        starting = True
        await asyncio.sleep(3)
        Relay1.on()
        await asyncio.sleep(20)
        Relay2.on()
        await asyncio.sleep(3)
        Relay2.off()
        starting = False
    else:
        starting = False
        Relay2.off()
        Relay1.off()


# Task function for overflowing tank for 100 seconds
async def overflow():
    global overflowing, over_timer
    overflowing = True
    for i in range(100, -1, -1):
        over_timer = i
        await asyncio.sleep(1)
    set_start(False)
    set_over(False)
    overflowing = False


# Task function for checking the main line power supply
async def line():
    global power
    while True:
        await asyncio.sleep(1)
        if not In_Power.value():
            power = False
        elif power == False:
            await asyncio.sleep(3)
            power = True


# Main task function for controlling the entire system
async def task_main():
    global power, level, overflowing, filling
    asyncio.create_task(line())
    asyncio.create_task(monitor_level())
    sleep(5)

    while True:

        # For checking conditions and controling motor and indicator
        if power:
            if indicate_fill_task is None:
                Led.on()  # Turn on the LED
            if start:
                if not filling:
                    filling = True
                    indicate_fill_task = asyncio.create_task(task_blink())
                    motor_task = asyncio.create_task(motor(True))
        else:
            if indicate_fill_task is not None:
                indicate_fill_task.cancel()  # Cancel the task if power is off
                indicate_fill_task = None
            Led.off()  # Turn off the LED
            if filling:
                filling = False
                motor_task.cancel()
                await motor(False)
                if overflowing:
                    # Cancelling task if Overflowing
                    overflow_task.cancel()
                    overflowing = False

        # For controlling Start/Stop according to Min and Max Limits
        if level <= min and not start:
            set_start(True)
        elif level >= max and start:
            # Checking for overflow setting
            if over:
                # Checking conditions for Overflowing
                if filling and level == 4 and not overflowing and not starting:
                    overflow_task = asyncio.create_task(overflow())
            else:
                set_start(False)

# Call the start function
start()

# Start a new thread for the screen idle task
_thread.start_new_thread(task_screen_idle, ())

# Run the main task
asyncio.run(task_main())
