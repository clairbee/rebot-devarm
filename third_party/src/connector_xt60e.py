# Envelope of an XT60E-F panel-mount connector.
#
# The part the power supply's front cover is cut for: a rectangular flange with
# two M3 fixing holes, the socket body behind it, and the two 3.5 mm bullets
# inside. Step 1-3 of the power supply assembly screws through those two holes,
# which is why they are modelled rather than left to the envelope.
#
# The flange lies on the XY plane; the body goes down (-Z), into the enclosure.

import build123d as bd

FLANGE_LENGTH = 16.0
FLANGE_WIDTH = 24.0
FLANGE_THICKNESS = 2.0
BODY_LENGTH = 15.6
BODY_WIDTH = 8.1
BODY_DEPTH = 16.0
HOLE_PITCH = 19.0
HOLE_DIAMETER = 3.2
BULLET_DIAMETER = 3.5
BULLET_PITCH = 7.2

with bd.BuildPart() as result:
    bd.Box(
        FLANGE_LENGTH,
        FLANGE_WIDTH,
        FLANGE_THICKNESS,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )
    # The socket body, behind the flange.
    bd.Box(
        BODY_LENGTH,
        BODY_WIDTH,
        BODY_DEPTH,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX),
    )
    # The two bullets inside it.
    with bd.Locations((0, -BULLET_PITCH / 2.0), (0, BULLET_PITCH / 2.0)):
        bd.Cylinder(
            radius=BULLET_DIAMETER / 2.0,
            height=BODY_DEPTH * 0.8,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX),
        )
    # The two M3 fixing holes, across the flange.
    with bd.Locations(bd.Plane.XY.offset(FLANGE_THICKNESS)):
        with bd.Locations((0, -HOLE_PITCH / 2.0), (0, HOLE_PITCH / 2.0)):
            bd.Hole(radius=HOLE_DIAMETER / 2.0, depth=FLANGE_THICKNESS)

if "show_object" in locals():
    show_object(result.part.wrapped, name="connector")  # noqa: F821
