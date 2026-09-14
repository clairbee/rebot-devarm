# Envelope of a shielded deep-groove ball bearing.
#
# The bore, the outside diameter and the width are what a housing and a shaft are
# cut to, and they are all a fit check needs. The balls, the raceways and the
# shield are inside that envelope, so leaving them out changes nothing about what
# this shape can be used for - see the 'summary' of each bearing in partcad.yaml.
#
# 'bore', 'od' and 'width' arrive as the part's parameters.

import build123d as bd

# The parameters of the part. PartCAD substitutes the declared values for these
# assignments, so each one has to be assigned here to be settable at all.
bore = 17.0
od = 26.0
width = 5.0

# The chamfer every ring carries on its outer edges. Small, and it is what tells
# the two faces apart when the shape is rendered.
chamfer = min(0.4, width / 6.0)

with bd.BuildPart() as result:
    bd.Cylinder(radius=od / 2.0, height=width)
    with bd.Locations((0, 0, 0)):
        bd.Cylinder(radius=bore / 2.0, height=width, mode=bd.Mode.SUBTRACT)
    if chamfer > 0:
        bd.chamfer(result.edges().filter_by(bd.GeomType.CIRCLE), chamfer)

if "show_object" in locals():
    show_object(result.part.wrapped, name="bearing")  # noqa: F821
