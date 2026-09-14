# Envelope of an enclosed switching power supply (MeanWell LRS series).
#
# The case and the two mounting flanges it is screwed down by, from the series
# datasheet. The terminal block, the vents and the output trimmer are left out:
# the shape is here to check that the 3D printed covers fit around the supply,
# which is what the enclosure in ./cable-xt30-2x2.assy's sibling
# 'power-supply' assembly does.
#
# The case lies with its base on the XY plane and its length along X.

import build123d as bd

# The parameters of the part; PartCAD substitutes the declared values.
length = 215.0
width = 115.0
height = 30.0

FLANGE_THICKNESS = 1.0
FLANGE_WIDTH = 8.0
FLANGE_HOLE_DIAMETER = 4.0

with bd.BuildPart() as result:
    bd.Box(length, width, height, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    # The flanges along both long sides, at the height the series puts them.
    for sign in (1, -1):
        with bd.Locations((0, sign * (width / 2.0 + FLANGE_WIDTH / 2.0), height * 0.25)):
            bd.Box(
                length * 0.75,
                FLANGE_WIDTH,
                FLANGE_THICKNESS,
                align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
            )
    # One fixing hole at each end of each flange. Their positions are
    # approximate - the datasheet drawing is what would settle them.
    with bd.Locations(bd.Plane.XY.offset(height * 0.25 + FLANGE_THICKNESS)):
        with bd.GridLocations(length * 0.6, width + FLANGE_WIDTH, 2, 2):
            bd.Hole(radius=FLANGE_HOLE_DIAMETER / 2.0, depth=FLANGE_THICKNESS)

if "show_object" in locals():
    show_object(result.part.wrapped, name="psu")  # noqa: F821
