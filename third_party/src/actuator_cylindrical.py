# Envelope of a cylindrical joint actuator (a Damiao DM43xx or a RobStride RS0x).
#
# These actuators are a frameless motor, a planetary or harmonic stage and a
# driver board in one machined housing: a cylinder with an output boss on one end
# and a connector on the side. The envelope keeps the cylinder and the boss, which
# is what decides whether the joint clears its neighbours, and drops the rest.
#
# It is inscribed in the bounding box the vendor's listing states rather than
# measured off a model, so it is right about how much room the actuator needs and
# wrong about everything a fastener would be located from. See the part's
# 'summary' in partcad.yaml.
#
# The housing stands on the XY plane; the output boss is on top, which is the
# direction the next link goes.

import build123d as bd

# The parameters of the part; PartCAD substitutes the declared values.
diameter = 57.0
height = 57.0
output_diameter = 30.0
output_height = 4.0

with bd.BuildPart() as result:
    bd.Cylinder(radius=diameter / 2.0, height=height, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    with bd.Locations(bd.Plane.XY.offset(height)):
        bd.Cylinder(
            radius=output_diameter / 2.0,
            height=output_height,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        )

if "show_object" in locals():
    show_object(result.part.wrapped, name="actuator")  # noqa: F821
