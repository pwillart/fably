"""Code to manage a series of LEDs."""
import random
import time
import threading

try:
    from apa102_pi.driver import apa102
except (ImportError, NotImplementedError):
    apa102 = None

from fably import utils


class LEDs:
    """Class to manage a series of rgb LEDs."""

    def __init__(self, colors=None, brightness=1, step=1, pause=0.007):
        default_colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0x00FFFF]
        if colors is None:
            colors = default_colors
        self.colors = colors
        self.starting_colors = colors
        self.brightness = brightness
        self.step = step
        self.pause = pause
        self.running = False
        self.thread = None
        self.mode = "rotate"  # Supported modes are "rotate", "spin", "twinkle"
        self.twinkle_leds = [False, False, False, False, False]
        self.twinkle_brightness = [0, 0, 0, 0, 0]
        self.twinkle_direction = [False, False, False, False, False]
        self.twinkle_brightness_step = 1

    def _run(self):
        # If we can't load the library, we can't do anything.
        # We should not be getting here but just in case.
        if not apa102:
            return

        strip = apa102.APA102(num_led=len(self.colors))
        strip.clear_strip()

        while self.running and self.mode == "rotate":
            for i, color in enumerate(self.colors):
                new_color = utils.rotate_rgb_color(color, self.step)
                strip.set_pixel_rgb(i, new_color, self.brightness)
                self.colors[i] = new_color
            strip.show()
            time.sleep(self.pause)

        while self.running and self.mode == "spin":
            for i, color in enumerate(self.colors):
                new_color = self.starting_colors[i] if i == self.step else 0x000000
                strip.set_pixel_rgb(i, new_color, self.brightness)
                self.colors[i] = new_color
            self.step = 0 if self.step == 4 else self.step + 1
            strip.show()
            time.sleep(self.pause * 25)

        while self.running and self.mode == "twinkle":
            # print("twinkle")
            for i, color in enumerate(self.colors):
                new_color = self.starting_colors[i] if self.twinkle_leds[i] == 1 else 0x000000
                if self.twinkle_leds[i]:
                    current_brightness = self.twinkle_brightness[i]
                    print(f"Current i: {i} brightness: {current_brightness} direction: {self.twinkle_direction[i]}")
                    # new_brightness = current_brightness
                    if self.twinkle_direction[i]:
                        new_brightness = current_brightness + self.twinkle_brightness_step
                        if new_brightness >= 100:
                            new_brightness = 100
                            self.twinkle_direction[i] = False
                    else:
                        new_brightness = current_brightness - self.twinkle_brightness_step
                        if new_brightness <= 0:
                            new_brightness = 0
                            # Pick new twinkle led
                            new_twinkle_led = self.pick_new_twinkle_led()
                            self.twinkle_leds[i] = False
                            self.twinkle_leds[new_twinkle_led[0]] = True
                            self.twinkle_direction[new_twinkle_led[0]] = True
                    self.twinkle_brightness[i] = new_brightness
                    print(f"New i: {i} brightness: {new_brightness} direction: {self.twinkle_direction[i]}")
                    strip.set_pixel_rgb(i, new_color, new_brightness)
            strip.show()
            time.sleep(self.pause)

        strip.clear_strip()
        strip.cleanup()

    def start(self, mode="rotate"):
        # print(f"leds {mode}")
        if not apa102 or self.thread:
            return
        self.mode = mode
        if mode == "rotate":
            self.starting_colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0x00FFFF]
        if mode == "spin":
            self.starting_colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0x00FFFF]
        if mode == "twinkle":
            # select two leds to start twinkling
            active_leds = random.sample(range(0, 4), 2)
            for i, color in enumerate(self.colors):
                self.twinkle_leds[i] = True if i in active_leds else False
                self.twinkle_brightness[i] = random.randint(0, 100) if i in active_leds else 0
                self.twinkle_direction[i] = random.choice([True, False]) if i in active_leds else False
            self.colors = [0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF]
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def stop(self):
        # print(f"leds stop")
        if self.thread and self.running:
            self.running = False
            self.thread.join()
            self.thread = None
            self.step = 1
            self.colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0x00FFFF]
            self.twinkle_leds = [False, False, False, False, False]
            self.twinkle_brightness = [0, 0, 0, 0, 0]
            self.twinkle_direction = [False, False, False, False, False]

    def pick_new_twinkle_led(self):
        new_twinkle_led = random.sample(range(0, 4), 1)
        return new_twinkle_led if not self.twinkle_leds[new_twinkle_led[0]] else self.pick_new_twinkle_led()