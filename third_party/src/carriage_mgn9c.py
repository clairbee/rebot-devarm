# Envelope of an MGN9C carriage block.
#
# 20 mm wide, 39 mm long, 10 mm high, with the slot that straddles the rail and
# the four M3 mounting holes on the top face at the standard 20 x 10 mm pitch -
# the holes being what the gripper's bracket is screwed to, and so the one detail
# worth having beyond the box.
#
# The block sits with its top face at z = 10 and the slot opening downwards, so it
# sits on a rail whose mounting face is z = 0.

import build123d as bd

WIDTH = 20.0
LENGTH = 39.0
HEIGHT = 10.0
SLOT_WIDTH = 9.4  # clearance over the 9 mm rail
SLOT_DEPTH = 7.0
HOLE_PITCH_X = 20.0
HOLE_PITCH_Y = 10.0
HOLE_DIAMETER = 3.0

with bd.BuildPart() as result:
    bd.Box(LENGTH, WIDTH, HEIGHT, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    # The channel the rail runs in.
    with bd.Locations((0, 0, 0)):
        bd.Box(
            LENGTH,
            SLOT_WIDTH,
            SLOT_DEPTH,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
            mode=bd.Mode.SUBTRACT,
        )
    # The four tapped holes on the top face.
    with bd.Locations(bd.Plane.XY.offset(HEIGHT)):
        with bd.GridLocations(HOLE_PITCH_X, HOLE_PITCH_Y, 2, 2):
            bd.Hole(radius=HOLE_DIAMETER / 2.0, depth=HEIGHT - SLOT_DEPTH)

if "show_object" in locals():
    show_object(result.part.wrapped, name="carriage")  # noqa: F821
