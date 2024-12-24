#!/usr/bin/env python3
"""Sample script to run pulse test on the LEDs."""

from fably import leds

STARTING_COLORS = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0x00FFFF]


def main():
    lights = leds.LEDs(STARTING_COLORS)

    try:
        lights.start("rotate")
        input("Press enter to stop the LEDs...\n")
        lights.stop()
        input("Press enter to start them again...\n")
        lights.start("rotate")
        input("Press enter once again to stop the program...\n")
        lights.stop()
    finally:
        # stop if any exception or keyboard interrupt happened
        lights.stop()


if __name__ == "__main__":
    main()
