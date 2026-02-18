"""
MIDI-Controlled Fullscreen Light Wash

Creates a dynamic fullscreen display that responds to MIDI input from Logic Pro,
displaying fullscreen color washes that fade based on note velocity and duration.

SETUP:
------
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
"""

import pygame
import mido
import threading
import random
import os

os.environ["SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS"] = "0"

DECAY = 0.5
TRAIL_ALPHA = 100

DISPLAYS_CONFIG = [
    {
        'id': 0,
        'monitor_index': 0,
        'name': 'Display 1',
        'note_range': (0, 47),      # C0-B3
    },
    {
        'id': 1,
        'monitor_index': 1,
        'name': 'Display 2',
        'note_range': (48, 95),     # C4-B7
    }
]

PALETTE = {
    0:  (255, 0, 0),        # C
    1:  (255, 0, 110),      # C#
    2:  (255, 100, 0),      # D
    3:  (255, 200, 0),      # D#
    4:  (255, 255, 0),      # E
    5:  (120, 255, 0),      # F
    6:  (0, 255, 0),        # F#
    7:  (0, 255, 140),      # G
    8:  (0, 255, 255),      # G#
    9:  (0, 80, 255),       # A
    10: (100, 0, 255),      # A#
    11: (220, 0, 255)       # B
}


class Display:
    """Manages fullscreen color washes for a display region."""
    
    def __init__(self, display_id, monitor_index, name, note_range):
        self.id = display_id
        self.monitor_index = monitor_index
        self.name = name
        self.note_min, self.note_max = note_range
        self.w, self.h = 1920, 1080
        self.active_washes = []
        self.lock = threading.Lock()
    
    def note_in_range(self, note):
        return self.note_min <= note <= self.note_max
    
    def set_dimensions(self, w, h):
        self.w = w
        self.h = h
    
    def add_wash(self, note, velocity):
        with self.lock:
            vel = velocity / 127.0
            self.active_washes.append(ColorWash(note, vel, self.w, self.h))
    
    def release_note(self, note):
        target_idx = note % 12
        with self.lock:
            for wash in self.active_washes:
                if wash.note_index == target_idx and wash.held:
                    wash.release()
    
    def update(self):
        with self.lock:
            for wash in self.active_washes:
                wash.update()
            self.active_washes = [w for w in self.active_washes if w.intensity > 0.01]
    
    def draw(self, surface):
        with self.lock:
            for wash in self.active_washes:
                wash.draw(surface)


class ColorWash:
    """A fullscreen color overlay that fades over time."""
    
    def __init__(self, note, velocity, screen_w, screen_h):
        self.vel = velocity
        self.w = screen_w
        self.h = screen_h
        self.note_index = note % 12
        self.base_color = PALETTE.get(self.note_index, (255, 255, 255))
        self.intensity = 1.0
        self.held = True
        self.flash = 1.0 if self.vel > 0.9 else 0.0
    
    def release(self):
        self.held = False
    
    def update(self):
        if not self.held:
            self.intensity *= DECAY
        else:
            self.intensity = random.uniform(0.92, 1.0)
        self.flash *= 0.80
        self.intensity = max(0, min(self.intensity, 1.0))
    
    def draw(self, surface):
        if self.intensity < 0.01:
            return
        
        overlay = pygame.Surface((self.w, self.h))
        r, g, b = self.base_color
        
        fr = min(255, r + (255 - r) * self.flash)
        fg = min(255, g + (255 - g) * self.flash)
        fb = min(255, b + (255 - b) * self.flash)
        
        display_r = int(fr * self.intensity * self.vel)
        display_g = int(fg * self.intensity * self.vel)
        display_b = int(fb * self.intensity * self.vel)
        
        overlay.fill((display_r, display_g, display_b))
        surface.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)


displays = []


def midi_listener():
    """Listen for MIDI messages and route them to displays."""
    ports = mido.get_input_names()
    target = next((p for p in ports if "IAC" in p or "Bus 1" in p), ports[0] if ports else None)
    
    if not target:
        print("No MIDI input found. Waiting for MIDI connection...")
        return
    
    print(f"Connected to: {target}")
    
    try:
        inport = mido.open_input(target)
    except Exception as e:
        print(f"Error: {e}")
        return
    
    for msg in inport:
        if msg.type not in ['note_on', 'note_off']:
            continue
        
        for display in displays:
            if not display.note_in_range(msg.note):
                continue
            
            if msg.type == 'note_on' and msg.velocity > 0:
                display.add_wash(msg.note, msg.velocity)
            elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
                display.release_note(msg.note)


if __name__ == "__main__":
    pygame.init()
    
    try:
        sizes = pygame.display.get_desktop_sizes()
    except AttributeError:
        sizes = [(1920, 1080), (1920, 1080)]
    
    print(f"Detected {len(sizes)} monitor(s): {sizes}")
    
    active_config = DISPLAYS_CONFIG[0]
    w, h = sizes[active_config['monitor_index']] if active_config['monitor_index'] < len(sizes) else sizes[0]
    
    for config in DISPLAYS_CONFIG:
        display = Display(config['id'], config['monitor_index'], config['name'], config['note_range'])
        display.set_dimensions(w, h)
        displays.append(display)
        print(f"Display {config['id']}: notes {config['note_range'][0]}-{config['note_range'][1]}")
    
    screen = pygame.display.set_mode((w, h), pygame.NOFRAME, display=active_config['monitor_index'])
    pygame.display.set_caption("MIDI Color Link")
    
    dimmer = pygame.Surface((w, h))
    dimmer.set_alpha(TRAIL_ALPHA)
    dimmer.fill((0, 0, 0))
    
    pygame.mouse.set_visible(False)
    
    threading.Thread(target=midi_listener, daemon=True).start()
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
        
        screen.blit(dimmer, (0, 0))
        
        for display in displays:
            display.update()
            display.draw(screen)
        
        pygame.display.flip()
    
    pygame.quit()
