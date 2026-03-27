# MackPad — All-in-One Macro Controller  
### By Sivansh Gupta

---

## Overview  
MackPad is a compact, high-functionality macropad designed to deliver maximum utility within a minimal footprint. Built around the Seeeduino XIAO ESP32 S3, it efficiently utilizes nearly all available GPIO pins to support a wide range of features.

Key features include:  
- 3x3 NKRO macro keypad  
- Rotary encoder with integrated push functionality  
- 0.91" OLED display for real-time feedback  
- Neopixel backlighting for visual indication  
- Fully programmable firmware using KMK  

This device is designed for productivity, quick controls, and customizable workflows, making it ideal for developers, creators, and power users.

---

## Features  
- Compact and efficient design  
- Fully programmable macros and keymaps  
- Layer indication and UI via OLED display  
- Custom rotary encoder handling via analog input  
- Hot-swappable switches  
- RGB-capable lighting system (currently neopixel-based)  

---

## Usage  

### Setup Steps  
1. Flash the Seeeduino XIAO ESP32 S3 with the appropriate CircuitPython `.uf2` firmware  
2. Upload the following files to the board:  
   - `code.py`  
   - required libraries  
   - display assets (images/icons)  
3. Save and reboot the device  

### Customization  
All customization can be done inside the `code.py` file:  
- Key mappings  
- Macro definitions  
- Lighting effects  
- Display output and UI  

---

## Motivation  
This project originated from a need for a rotary encoder-based control system for volume and workflow shortcuts. It evolved into a fully featured macropad with enhanced functionality, modularity, and visual feedback.

---

## Firmware  
- Built using KMK firmware  
- OLED used for:  
  - Layer indication  
  - Icon rendering  
  - Status and signature display  
- Neopixels used for backlighting  
- Custom rotary encoder decoding via analog input  
- Custom key object for multi-function encoder input  
- Advanced macro and hotkey integration  

---

## Bill of Materials (BOM)

| Qty | Component                          | Notes                          | Approx Price (USD) | Approx Price (INR) |
|-----|-----------------------------------|--------------------------------|--------------------|--------------------|
| 1   | Seeeduino XIAO ESP32 S3             | Microcontroller                | $6.00              | ₹500               |
| 9   | MX-style switches                 | Mechanical switches            | $4.50              | ₹375               |
| 9   | 1N4148 diodes                     | Switch matrix                  | $0.90              | ₹75                |
| 1   | SSD1306 0.91" OLED (128x32)       | I2C display                    | $3.00              | ₹250               |
| 9   | DSA keycaps                       | Blank keycaps                  | $5.00              | ₹400               |
| 1   | 1x4 female header (2.54mm)        | Display mounting               | $0.50              | ₹40                |
| 1   | EC11 rotary encoder               | Input control                  | $1.50              | ₹120               |
| 1   | 10kΩ resistor                     | Voltage divider                | $0.10              | ₹10                |
| 1   | 47kΩ resistor                     | Voltage divider                | $0.10              | ₹10                |
| 1   | 100kΩ resistor                    | Voltage divider                | $0.10              | ₹10                |
| 9   | Kailh hot-swap sockets            | Switch mounting                | $6.00              | ₹500               |

### Estimated Total Cost  
- USD: ~$27.70  
- INR: ~₹2,290  

*Prices may vary depending on supplier and region.*

---

## Future Improvements  

Planned upgrades to expand functionality and user interaction:

### 1. Advanced RGB Lighting  
- Per-key RGB control instead of uniform backlighting  
- Layer-based color indication  
- Reactive lighting effects (typing, macros, system status)  

### 2. Touch Sensor Integration  
- Capacitive touch inputs for gesture-based controls  
- Swipe or tap gestures for media, scrolling, or layer switching  
- Reduced reliance on physical switches for certain actions  

### 3. Wireless Capability  
- Bluetooth support for portable usage  
- Battery-powered operation  

### 4. Enhanced UI System  
- Improved OLED UI with animations  
- Menu-based navigation system  
- Dynamic macro preview  

---

## Final Notes  
MackPad demonstrates efficient embedded system design by maximizing limited hardware resources while maintaining usability and flexibility. It serves as both a practical productivity tool and a showcase of integrated hardware, firmware, and product design.

---
