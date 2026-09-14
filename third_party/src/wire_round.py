# A length of round silicone wire.
#
# The shape of a wire is a section swept along a route, and the route belongs to
# whatever the wire is installed in: a cable assembly states it, this part only
# knows how to follow one. Until an assembly has real placements to route
# through, the route is the straight run a cable has while it is still in its bag,
# which is 'length' long.
#
# 'length' and 'diameter' arrive as the part's parameters.

import build123d as bd

# The parameters of the part; PartCAD substitutes the declared values.
length = 100.0
diameter = 3.5

with bd.BuildPart() as result:
    bd.Cylinder(
        radius=diameter / 2.0,
        height=length,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )

if "show_object" in locals():
    show_object(result.part.wrapped, name="wire")  # noqa: F821
