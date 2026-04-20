# MIDI Controlled Fullscreen Light Wash
Creates a dynamic fullscreen lighting wash that responds to MIDI input, displaying color fills that fade based on note velocity and duration.

## Why?
Concert Lighting.

I made this (or asked Gemini to) to have a cheap (or free) alternative to that kind of lighting at home. Just connect a monitor (or two) and you’re good to go. Even better if you have projectors.

I don’t really know much about professional lighting systems. I just wanted to time-code my music to lights in a simple way using MIDI from my DAW.

## Here’s where I used this

- [1](https://www.instagram.com/reel/DSSiHb4DpeV/)  
- [2](https://www.instagram.com/reel/DUzsoJGjm9L/)

## Setup
Adding all this information here in case I forget, but if you're reading this, welcome.

1. Install dependencies:
   pip install pygame mido python-rtmidi

2. Configure the driver:
   - Go to Audio MIDI Setup > Window > MIDI Studio > IAC Driver
   - Check "Device is online" and create a new port (e.g. "Bus 1")

3. Route MIDI to this script:
   - In Logic Pro, make a new External MIDI track (I have no idea about other DAWs but it should be similar)
   - Set the MIDI Destination to IAC Driver
   - In the track settings, set the MIDI Input and Internal MIDI In to Off
   - Add a MIDI region and draw some notes to test

4. Run the script:
   python midi_light.py

5. Control from Logic Pro:
   - Play the MIDI region to see colors on the screen

CUSTOMIZATION:
--------------
- Edit DISPLAYS_CONFIG: Add/remove displays and adjust note ranges
- Edit PALETTE: Change the 12-note chromatic color mapping
- Adjust DECAY: Control how quickly colors fade (0.5 = fast, 0.95 = slow)
- Adjust TRAIL_ALPHA: Brightness of the fade trail (0-255)

Have fun creating dynamic music videos!
