## Scramp-fish is a utility with a friendly GUI that will help extend the life cycle of your laptop's battery.

![screenshot.png](dev%2Fscreenshot.png)

#### Features

- Turn on/off "Rapid charge".
- Activation of the "Conservation" mode.

#### Description

The "Rapid charge" mode can be extremely useful when you need
quickly charge the battery and continue working. However, regular
using can significantly reduce battery life.
It is recommended to avoid using "Rapid charge" at every turn.

The "Conservation" mode is designed to significantly slow down the process of 
battery degradation, especially when the device use external power source most 
of the time. When activated, battery charge will be limited up to 55-60% of its 
capacity and the "Rapid charge" mode is automatically turned off.

#### Tests

The application has been confirmed to work correctly on the following laptop 
models:

- Lenovo Legion 5-15ACH6H (2021, BIOS: GKCN60WW, GKCN64WW)

#### Installation

1. Clone the repository to a location you want:

     ```bash
     git clone git@github.com:CuriousGecko/scramp-fish.git
     ```
2. Go to the cloned repository folder:

     ```bash
     cd scramp-fish
     ```
3. Build and install the package:

     ```bash
     makepkg -si
     ```

#### Technology
The project was developed in python3.9 using the PySide6 framework.