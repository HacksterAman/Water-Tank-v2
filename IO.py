from machine import Pin

# Buttons Pin Declaration
B_Next=Pin(16, Pin.IN, Pin.PULL_UP)
B_Select=Pin(5, Pin.IN, Pin.PULL_UP)

# Input Pin declaration
In_Power=Pin(6, Pin.IN, Pin.PULL_UP)
In_100=Pin(8, Pin.IN, Pin.PULL_UP)
In_75=Pin(7, Pin.IN, Pin.PULL_UP)
In_50=Pin(17, Pin.IN, Pin.PULL_UP)
In_25=Pin(4, Pin.IN, Pin.PULL_UP)

# Output Pin declaration
Relay1=Pin(9, Pin.OUT)
Relay2=Pin(10, Pin.OUT)
Buzzer=Pin(11, Pin.OUT)

# Indicator Led Pin declaration
Led=Pin(12, Pin.OUT)

# Display Pin declaration
sda=Pin(2)
scl=Pin(3)