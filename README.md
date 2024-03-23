# Submersible Motor Control System

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Hardware Requirements](#hardware-requirements)
- [Installation and Setup](#installation-and-setup)

## Overview

The Submersible Motor Control System is designed for efficient control of submersible motors used in water tank systems. This system includes features such as motor control, level monitoring, and intentional overflow for tank water cleanup. It is equipped with customization options for adjusting minimum and maximum water levels to suit various applications.

## Features

- **Motor Control:**
  - Control of submersible motors with a stabilizer (Relay 1) and a starter (Relay 2).
  - Manual start/stop motor control for flexibility.

- **Water Level Monitoring:**
  - Precise monitoring of five water levels to ensure accurate control.

- **Overflow Protection:**
  - Intentional overflow feature for tank water cleanup.
  - Option to enable or disable overflow protection.

- **Customization:**
  - Adjustable minimum and maximum water level limits for personalized settings.

- **Real-time Display:**
  - OLED display for real-time status monitoring.

- **User-friendly Interface:**
  - Menu-based navigation for easy configuration.

## Hardware Requirements

- Microcontroller (e.g., ESP32 or similar)
- Submersible motor with stabilizer (Relay 1) and starter (Relay 2)
- Water level sensors
- Input buttons (Next, Select)
- OLED display (128x64 pixels)
- Buzzer for audible feedback
- Indicator LED

## Installation and Setup

1. Clone the repository:

   ```bash
   https://github.com/HacksterAman/Water-Tank-v2.git
   ```
   

2. Connect the hardware components based on the provided wiring diagram.

3. Upload the code to your microcontroller, using thonny.

4. Open the serial monitor to view system status and debug messages.

5. Power on the system and adjust settings using the input buttons.

## Configuration

- **Buttons:**
  - `Next`: Navigate through menu options.
  - `Select`: Confirm selection. Long press to go to menu.

- **Menu Options:**
  1. **Controls:**
     - Start or stop the submersible motor.
     - Enable or disable intentional overflow for tank water cleanup.
  2. **Limits:**
     - Adjust the maximum and minimum water level limits.
  3. **Overflow Settings:**
     - Configure overflow behavior.
