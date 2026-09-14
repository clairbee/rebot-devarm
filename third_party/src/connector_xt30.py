# Envelope of an XT30 2+2 connector housing.
#
# Two 2 mm power bullets and two signal pins in a nylon block: the connector at
# each end of the motor harnesses that run down the arm. The block is what has to
# clear a cable channel, and the pins are here so that the mating direction is
# visible in a render.
#
# Approximate throughout - Amass publishes no drawing of the 2+2 variant, and
# these are the proportions of the photographs in the readme.
#
# The housing sits on the XY plane with the pins pointing along +Z, which is the
# direction it is pushed home.

import build123d as bd

BODY_LENGTH = 16.0
BODY_WIDTH = 12.0
BODY_HEIGHT = 8.0
POWER_PIN_DIAMETER = 3.0
SIGNAL_PIN_DIAMETER = 1.5
PIN_LENGTH = 6.0
POWER_PITCH = 6.0
SIGNAL_PITCH = 2.5

with bd.BuildPart() as result:
    bd.Box(BODY_LENGTH, BODY_WIDTH, BODY_HEIGHT, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    with bd.Locations(bd.Plane.XY.offset(BODY_HEIGHT)):
        # The two power bullets, side by side across the width.
        with bd.Locations((-POWER_PITCH / 2.0, -2.0), (POWER_PITCH / 2.0, -2.0)):
            bd.Cylinder(
                radius=POWER_PIN_DIAMETER / 2.0,
                height=PIN_LENGTH,
                align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
            )
        # The two signal pins behind them.
        with bd.Locations((-SIGNAL_PITCH / 2.0, 3.5), (SIGNAL_PITCH / 2.0, 3.5)):
            bd.Cylinder(
                radius=SIGNAL_PIN_DIAMETER / 2.0,
                height=PIN_LENGTH,
                align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
            )

if "show_object" in locals():
    show_object(result.part.wrapped, name="connector")  # noqa: F821
