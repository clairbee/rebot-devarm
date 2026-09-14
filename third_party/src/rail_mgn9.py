# Envelope of an MGN9 linear rail.
#
# The MGN9 profile is 9 mm wide and 10 mm high, which is what decides whether the
# rail fits its seat; the ball grooves down the flanks and the M3 counterbores
# along the top are not here. 'length' is the part's parameter (170 mm as the
# readme orders it).
#
# The rail lies along +X with its mounting face on the XY plane, so a part it is
# screwed to sits at z = 0.

import build123d as bd

# A parameter of the part; PartCAD substitutes the declared value.
length = 170.0

WIDTH = 9.0
HEIGHT = 10.0

with bd.BuildPart() as result:
    with bd.BuildSketch(bd.Plane.XZ) as section:
        bd.Rectangle(WIDTH, HEIGHT, align=(bd.Align.CENTER, bd.Align.MIN))
        # The waist the carriage's lips reach into, as a plain flat rather than
        # the two ball grooves it stands for.
        with bd.Locations((WIDTH / 2.0, HEIGHT * 0.55), (-WIDTH / 2.0, HEIGHT * 0.55)):
            bd.Rectangle(1.2, 3.0, mode=bd.Mode.SUBTRACT)
    bd.extrude(amount=length, dir=(0, 1, 0))

if "show_object" in locals():
    show_object(result.part.wrapped, name="rail")  # noqa: F821
