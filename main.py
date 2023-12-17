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
            print(B, "Short Press")
            return 1  # Short press
        else:
            print(B, "Long Press")
            return -1  # Long press
    else:
        return 0


def printlines(lines, invert=[0]):
    if len(lines[0]) == 9:
        font = Font_Thick
    else:
        font = Font_Thin
    for i in range(3):
        font.printstring(lines[i], i + 1 in invert)
    oled.show()
    Writer.set_textpos(0, 0)


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


def start():
    printlines(["  Created by:  ", " " * 25, "   Aman Singh"])
    sleep(3)
    clear()


def load():
    for i in range(4):
        printlines([" " * 25, "loading" + "." * i, ""])
        sleep(1)
    clear()


def clear():
    oled.fill(0)
    oled.show()


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


def screen_control():
    while True:
        selected = option(options(0))  # Main menu
        if selected == 1:
            clear()
            return  # End function and return to the main loop

        elif selected == 2:
            while True:
                selected_controls = option(options(1))  # Controls submenu
                if selected_controls == 1:
                    break  # Go back to the main menu

                elif selected_controls == 2:
                    set_start(not start)
                    clear()
                    return

                elif selected_controls == 3:
                    if over:
                        set_over(False)
                    else:
                        set_over(True)
                        set_start(True)
                    clear()
                    return

        elif selected == 3:
            while True:
                selected = option(options(2))  # Limits submenu
                if selected == 1:
                    break  # Go back to the main menu

                if selected == 2:
                    selected_level = option(options(3))
                    # ['100%','75%','50%']
                    if selected_level == 1:
                        set_max(4)
                    elif selected_level == 2:
                        set_max(3)
                    elif selected_level == 3:
                        set_max(2)
                    if max - min < 2:
                        set_min(max - 2)

                elif selected == 3:
                    selected_level = option(options(4))
                    # ['50%','25%','0%']
                    if selected_level == 1:
                        set_min(2)
                    elif selected_level == 2:
                        set_min(1)
                    elif selected_level == 3:
                        set_min(0)
                    if max - min < 2:
                        set_max(min + 2)


def task_screen_idle():
    load()
    invert = [0]
    while True:
        if button(B_Select) == -1:
            screen_control()
        else:
            start_time = time.ticks_ms()
            lines = []
            filled = str(level * 25)
            if starting:
                lines = [
                    "Starting Motor",
                    "Level" + " " * (12 - 2 * len(filled)) + filled + "%",
                    "",
                ]
            elif filling:
                if overflowing:
                    lines = [
                        "  Overflowing  ",
                        " " * (12 - len(str(over_timer)))
                        + str(over_timer)
                        + " " * (12 - len(str(over_timer))),
                        "Filled" + " " * (12 - 2 * len(filled)) + filled + "%",
                    ]
                else:
                    lines = [
                        "  Motor is On   ",
                        "Filled" + " " * (12 - 2 * len(filled)) + filled + "%",
                        "",
                    ]
            else:
                lines = [
                    "  Motor is Off  ",
                    "Level" + " " * (12 - 2 * len(filled)) + filled + "%",
                    "",
                ]

            duration = time.ticks_ms() - start_time

            if duration > 10000:
                if invert == [0]:
                    invert = [1, 2, 3]
                else:
                    invert = [0]

            printlines(lines, invert)


def set_start(mode):
    global start
    start = mode
    file.seek(0)
    file.write(str(int(mode)))
    file.flush()
    print(f'{"Start Motor" if mode else "Stop Motor"} Command is Initiated')


def set_min(level):
    global min
    min = level
    file.seek(1)
    file.write(str(level))
    file.flush()


def set_max(level):
    global max
    max = level
    file.seek(2)
    file.write(str(level))
    file.flush()


def set_over(mode):
    global over
    over = mode
    file.seek(3)
    file.write(str(int(mode)))
    file.flush()
    print(f'{"Start Overflow" if mode else "Stop Overflow"} Command is Initiated')


async def task_blink(delay):
    while True:
        Led.toggle()
        await asyncio.sleep_ms(delay)


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


# For controlling motor
async def motor(mode):
    global starting
    if mode:
        starting = True
        print("Motor is Starting")
        Relay1.on()
        await asyncio.sleep(13)
        Relay2.on()
        await asyncio.sleep(3)
        Relay2.off()
        print("Motor is Started")
        starting = False
    else:
        starting = False
        print("Motor is Stoping")
        Relay2.off()
        Relay1.off()
        print("Motor is Stoped")


# For overflowing tank for 100 seconds
async def overflow():
    global overflowing, over_timer
    overflowing = True
    for i in range(120, -1, -1):
        over_timer = i
        await asyncio.sleep(1)
    set_start(False)
    set_over(False)
    overflowing = False


# Checking Main Line Power Supply
async def line():
    global power
    while True:
        await asyncio.sleep(1)
        if not In_Power.value():
            power = False
            print("No Power")
        elif power == False:
            await asyncio.sleep(3)
            power = True
            print("Power is On")


async def task_main():
    print("Main Task Initiated")
    global power, level, overflowing, filling
    asyncio.create_task(line())
    # asyncio.create_task(task_blink())

    while True:
        if new_level() != level:
            await asyncio.sleep(1)
            if new_level() != level:
                await asyncio.sleep(1)
                if new_level() != level:
                    level = new_level()
                    print(f"Water Level is changed to {level*25}%")

        # For contolling Start/Stop according to Min and Max Limits
        if level <= min and not start:
            set_start(True)
        elif level >= max and start:
            # Checking for overflow setting
            if over:
                # Checking conditions for Overflowing
                if filling and over and level == 4 and not overflowing:
                    indicate_overflow_task = asyncio.create_task(task_blink(250))
                    overflow_task = asyncio.create_task(overflow())
            else:
                set_start(False)

        # For checking conditions to Control Motor
        if start and power:
            if not filling:
                print("Motor Task Start Command")
                filling = True
                indicate_fill_task = asyncio.create_task(task_blink(500))
                motor_task = asyncio.create_task(motor(True))
        elif filling:
            print("Motor Task Cancel Command")
            filling = False
            motor_task.cancel()
            indicate_fill_task.cancel()
            await motor(False)
            if overflowing:
                # Cancelling task if Overflowing
                overflow_task.cancel()
                indicate_overflow_task.cancel()
                overflowing = False

        if power:
            if not filling and not overflowing:
                Led.on()
        else:
            Led.off()


start()
_thread.start_new_thread(task_screen_idle, ())
asyncio.run(task_main())
